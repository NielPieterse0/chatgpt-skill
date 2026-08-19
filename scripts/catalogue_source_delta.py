#!/usr/bin/env python3
"""Detect reviewed-source drift for repository-sourced adopted skills without syncing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.skill_security import TEXT_SCAN_SUFFIXES, compute_skill_hash

RECHECKS = [
    "portability",
    "trigger-overlap",
    "progressive-disclosure",
    "security",
    "references-scripts",
    "behavioral-evidence",
]


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ValueError(message)
    return result.stdout.strip()


def _normalize_repository(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"source repository must be an absolute HTTPS URL: {value}")
    path = parsed.path.rstrip("/")
    if path.lower().endswith(".git"):
        path = path[:-4]
    return f"https://{parsed.netloc.lower()}{path}"


def _load_json(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _is_link_like(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    except OSError as exc:
        raise ValueError(f"unable to inspect path identity: {path}") from exc
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _safe_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise ValueError(f"skill directory does not exist: {root}")
    if _is_link_like(root):
        raise ValueError(f"skill directory must not be linked or reparse-backed: {root}")

    def fail_walk(error: OSError) -> None:
        raise ValueError(f"unable to enumerate skill directory: {root}") from error

    files: list[Path] = []
    for current, directories, names in os.walk(
        root, topdown=True, onerror=fail_walk, followlinks=False
    ):
        current_path = Path(current)
        for directory in directories:
            child = current_path / directory
            if _is_link_like(child):
                raise ValueError(
                    f"skill contains linked or reparse path: {child.relative_to(root).as_posix()}"
                )
        for name in names:
            child = current_path / name
            if _is_link_like(child):
                raise ValueError(
                    f"skill contains linked or reparse path: {child.relative_to(root).as_posix()}"
                )
            if child.is_file():
                files.append(child)
    files.sort(
        key=lambda path: (
            path.relative_to(root).as_posix().casefold(),
            path.relative_to(root).as_posix(),
        )
    )
    return files


def _adopted_content_hash(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    files = [
        path for path in _safe_files(skill_dir) if path.name != "adoption-manifest.json"
    ]
    for path in sorted(files, key=lambda item: item.relative_to(skill_dir).as_posix()):
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8")
        content = path.read_bytes()
        if path.suffix.lower() in TEXT_SCAN_SUFFIXES:
            content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _source_exists(repo: Path, revision: str, source_path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{revision}:{source_path}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _changed_paths(repo: Path, baseline: str, current: str, source_path: str) -> list[str]:
    output = _git(repo, "diff", "--name-status", baseline, current, "--", source_path)
    paths: set[str] = set()
    for line in output.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        for path in fields[1:]:
            paths.add(path)
    return sorted(paths, key=lambda value: (value.casefold(), value))


def _manifest_record(repo_root: Path, manifest_path: Path) -> tuple[str, str, str, str]:
    manifest = _load_json(manifest_path)
    skill_id = manifest.get("skill")
    source = manifest.get("source")
    if not isinstance(skill_id, str) or not skill_id:
        raise ValueError(f"manifest skill is invalid: {manifest_path}")
    if not isinstance(source, dict):
        raise ValueError(f"manifest source is invalid: {manifest_path}")
    repository = source.get("repository")
    revision = source.get("revision")
    adopted_hash = source.get("adopted_content_sha256")
    if not all(isinstance(value, str) and value for value in (repository, revision, adopted_hash)):
        raise ValueError(f"manifest source identity is incomplete: {manifest_path}")
    skill_dir = repo_root / "skills" / skill_id
    actual_hash = _adopted_content_hash(skill_dir)
    if actual_hash != adopted_hash:
        raise ValueError(f"adopted content hash mismatch for {skill_id}")
    return skill_id, repository, revision, adopted_hash


def _mapped_source(
    repository: str, source_repositories: Mapping[str, Path]
) -> Path | None:
    expected = _normalize_repository(repository)
    for key, candidate in source_repositories.items():
        if _normalize_repository(key) == expected:
            return Path(candidate).expanduser().resolve()
    return None


def _workspace_evidence(
    skill_id: str,
    expected_hash: str,
    catalog_root: Path | None,
    *,
    baseline_label: str,
) -> tuple[str | None, str]:
    if catalog_root is None:
        return None, "not_observed"
    skill_dir = catalog_root / skill_id
    if not skill_dir.is_dir():
        return None, "missing"
    actual_hash = _adopted_content_hash(skill_dir)
    status = (
        f"matches_{baseline_label}"
        if actual_hash == expected_hash
        else f"diverged_from_{baseline_label}"
    )
    return actual_hash, status


def _source_item(
    skill_id: str,
    repository: str,
    reviewed_revision: str,
    adopted_hash: str,
    source_repositories: Mapping[str, Path],
    catalog_root: Path | None,
    *,
    reviewed_revision_override: str | None = None,
    workspace_baseline_hash: str | None = None,
) -> dict[str, object]:
    source_path = f".agents/skills/{skill_id}"
    effective_revision = reviewed_revision_override or reviewed_revision
    expected_workspace_hash = workspace_baseline_hash or adopted_hash
    workspace_label = (
        "reviewed_workspace_baseline" if workspace_baseline_hash else "adoption_record"
    )
    workspace_hash, workspace_status = _workspace_evidence(
        skill_id,
        expected_workspace_hash,
        catalog_root,
        baseline_label=workspace_label,
    )
    source_repo = _mapped_source(repository, source_repositories)
    if source_repo is None:
        return {
            "skill_id": skill_id,
            "source_repository": repository,
            "source_path": source_path,
            "origin_reviewed_revision": reviewed_revision,
            "reviewed_revision": effective_revision,
            "current_revision": None,
            "adopted_content_sha256": adopted_hash,
            "workspace_baseline_sha256": expected_workspace_hash,
            "workspace_content_sha256": workspace_hash,
            "workspace_status": workspace_status,
            "source_status": "not_observable",
            "status": "not_observable",
            "changed_paths": [],
            "review_reasons": ["source-not-observable"],
            "disposition_required": True,
            "recommended_dispositions": ["defer"],
            "required_rechecks": RECHECKS,
            "warning": "source repository mapping is not available",
        }
    if not source_repo.is_dir():
        raise ValueError(f"source repository path does not exist: {source_repo}")
    origin = _git(source_repo, "config", "--get", "remote.origin.url")
    if _normalize_repository(origin) != _normalize_repository(repository):
        raise ValueError(
            f"source repository origin {origin!r} does not match {repository!r}"
        )
    _git(source_repo, "cat-file", "-e", f"{effective_revision}^{{commit}}")
    current_revision = _git(source_repo, "rev-parse", "HEAD")
    baseline_exists = _source_exists(source_repo, effective_revision, source_path)
    current_exists = _source_exists(source_repo, current_revision, source_path)
    changed = _changed_paths(
        source_repo, effective_revision, current_revision, source_path
    )
    if baseline_exists and not current_exists:
        status = "source_removed"
        dispositions = ["defer", "not-applicable", "preserve-local"]
    elif not baseline_exists and current_exists:
        status = "source_added"
        dispositions = ["adopt", "adapt", "defer", "not-applicable"]
    elif changed:
        status = "source_changed"
        dispositions = ["adopt", "adapt", "defer", "not-applicable", "preserve-local"]
    else:
        status = "source_unchanged"
        dispositions = []
    reasons: list[str] = []
    if status != "source_unchanged":
        reasons.append(status.replace("source_", "source-"))
    if workspace_status.startswith("diverged_from_"):
        reasons.append("workspace-diverged")
    elif workspace_status == "missing":
        reasons.append("workspace-missing")
    if not dispositions and reasons:
        dispositions = ["adapt", "defer", "preserve-local"]
    return {
        "skill_id": skill_id,
        "source_repository": repository,
        "source_path": source_path,
        "origin_reviewed_revision": reviewed_revision,
        "reviewed_revision": effective_revision,
        "current_revision": current_revision,
        "adopted_content_sha256": adopted_hash,
        "workspace_baseline_sha256": expected_workspace_hash,
        "workspace_content_sha256": workspace_hash,
        "workspace_status": workspace_status,
        "source_status": status,
        "status": status,
        "changed_paths": changed,
        "review_reasons": reasons,
        "disposition_required": bool(reasons),
        "recommended_dispositions": dispositions,
        "required_rechecks": RECHECKS if reasons else [],
        "warning": None,
    }


def _snapshot_tree_hash(skill_dir: Path) -> str:
    entries: list[tuple[str, str]] = []
    for path in _safe_files(skill_dir):
        relative = path.relative_to(skill_dir).as_posix()
        entries.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    entries.sort(key=lambda item: (item[0].casefold(), item[0]))
    digest = hashlib.sha256()
    for relative, file_hash in entries:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _refresh_record_item(
    path: Path,
    payload: Mapping[str, object],
    workspace: Path | None,
    baseline_override: Mapping[str, str] | None = None,
) -> dict[str, object]:
    skill_id = payload.get("skill_id")
    if not isinstance(skill_id, str) or not skill_id:
        raise ValueError(f"catalogue refresh record has invalid skill_id: {path}")
    source_baseline = payload.get("source_baseline")
    if not isinstance(source_baseline, dict):
        return {
            "skill_id": skill_id,
            "record_path": path.as_posix(),
            "comparison_mode": "not_observable",
            "status": "not_observable",
            "changed_source_skills": [],
            "disposition_required": True,
            "recommended_dispositions": ["defer"],
            "required_rechecks": RECHECKS,
            "warning": "refresh record has no machine-readable source_baseline",
        }
    baseline_skills = source_baseline.get("skills")
    if not isinstance(baseline_skills, dict) or not baseline_skills:
        return {
            "skill_id": skill_id,
            "record_path": path.as_posix(),
            "comparison_mode": "not_observable",
            "status": "not_observable",
            "changed_source_skills": [],
            "disposition_required": True,
            "recommended_dispositions": ["defer"],
            "required_rechecks": RECHECKS,
            "warning": "refresh record source_baseline has no tracked skills",
        }
    if workspace is None:
        return {
            "skill_id": skill_id,
            "record_path": path.as_posix(),
            "comparison_mode": "catalogue-source-snapshot",
            "status": "not_observable",
            "changed_source_skills": [],
            "disposition_required": True,
            "recommended_dispositions": ["defer"],
            "required_rechecks": RECHECKS,
            "warning": "catalogue root is required to compare source snapshots",
        }
    changed: list[str] = []
    details: list[dict[str, object]] = []
    for source_skill_id in sorted(baseline_skills, key=lambda value: (str(value).casefold(), str(value))):
        baseline = baseline_skills[source_skill_id]
        if not isinstance(source_skill_id, str) or not isinstance(baseline, dict):
            raise ValueError(f"invalid source baseline entry in {path}")
        expected_hash = (
            baseline_override.get(source_skill_id)
            if baseline_override and source_skill_id in baseline_override
            else baseline.get("tree_sha256")
        )
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise ValueError(f"invalid source baseline hash for {source_skill_id}")
        source_skill_dir = workspace / source_skill_id
        actual_hash = _snapshot_tree_hash(source_skill_dir) if source_skill_dir.is_dir() else None
        state = "unchanged" if actual_hash == expected_hash else ("missing" if actual_hash is None else "changed")
        if state != "unchanged":
            changed.append(source_skill_id)
        details.append(
            {
                "skill_id": source_skill_id,
                "baseline_tree_sha256": expected_hash,
                "current_tree_sha256": actual_hash,
                "status": state,
            }
        )
    status = "source_snapshot_changed" if changed else "source_snapshot_unchanged"
    return {
        "skill_id": skill_id,
        "record_path": path.as_posix(),
        "comparison_mode": "catalogue-source-snapshot",
        "status": status,
        "source_skills": details,
        "changed_source_skills": changed,
        "disposition_required": bool(changed),
        "recommended_dispositions": ["adopt", "adapt", "defer", "not-applicable", "preserve-local"] if changed else [],
        "required_rechecks": RECHECKS if changed else [],
        "warning": None,
    }


def _load_maintenance_baselines(
    repo: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    skill_baselines: dict[str, dict[str, str]] = {}
    refresh_baselines: dict[str, dict[str, str]] = {}
    paths = sorted(
        (repo / "config" / "catalogue-source-maintenance").glob("*.json"),
        key=lambda path: path.as_posix().casefold(),
    )
    for path in paths:
        payload = _load_json(path)
        if payload.get("schema_version") != 1:
            raise ValueError(f"unsupported maintenance baseline schema: {path}")
        raw_skills = payload.get("skill_baselines", {})
        raw_refresh = payload.get("refresh_baselines", {})
        if not isinstance(raw_skills, dict) or not isinstance(raw_refresh, dict):
            raise ValueError(f"maintenance baseline maps are invalid: {path}")
        for skill_id, baseline in raw_skills.items():
            if not isinstance(skill_id, str) or not isinstance(baseline, dict):
                raise ValueError(f"invalid skill baseline in {path}")
            revision = baseline.get("reviewed_source_revision")
            workspace_hash = baseline.get("workspace_content_sha256")
            if not isinstance(revision, str) or len(revision) not in {40, 64}:
                raise ValueError(f"invalid reviewed source revision for {skill_id}")
            if not isinstance(workspace_hash, str) or len(workspace_hash) != 64:
                raise ValueError(f"invalid workspace baseline hash for {skill_id}")
            skill_baselines[skill_id] = {
                "reviewed_source_revision": revision,
                "workspace_content_sha256": workspace_hash,
            }
        for skill_id, baseline in raw_refresh.items():
            if not isinstance(skill_id, str) or not isinstance(baseline, dict):
                raise ValueError(f"invalid refresh baseline in {path}")
            source_skills = baseline.get("source_skills", {})
            if not isinstance(source_skills, dict):
                raise ValueError(f"invalid refresh source skill baseline for {skill_id}")
            normalized: dict[str, str] = {}
            for source_skill_id, tree_hash in source_skills.items():
                if not isinstance(source_skill_id, str) or not isinstance(tree_hash, str) or len(tree_hash) != 64:
                    raise ValueError(f"invalid refresh tree hash for {skill_id}/{source_skill_id}")
                normalized[source_skill_id] = tree_hash
            refresh_baselines[skill_id] = normalized
    return skill_baselines, refresh_baselines


def build_report(
    repo_root: Path | str,
    source_repositories: Mapping[str, Path],
    *,
    catalog_root: Path | str | None = None,
) -> dict[str, object]:
    repo = Path(repo_root).expanduser().resolve()
    workspace = (
        Path(catalog_root).expanduser().resolve() if catalog_root is not None else None
    )
    skill_baselines, refresh_baselines = _load_maintenance_baselines(repo)
    manifests = sorted(
        (repo / "skills").glob("*/adoption-manifest.json"),
        key=lambda path: path.as_posix().casefold(),
    )
    skills: list[dict[str, object]] = []
    for manifest_path in manifests:
        skill_id, repository, revision, adopted_hash = _manifest_record(repo, manifest_path)
        baseline = skill_baselines.get(skill_id, {})
        skills.append(
            _source_item(
                skill_id,
                repository,
                revision,
                adopted_hash,
                source_repositories,
                workspace,
                reviewed_revision_override=baseline.get("reviewed_source_revision"),
                workspace_baseline_hash=baseline.get("workspace_content_sha256"),
            )
        )
    skills.sort(key=lambda item: (str(item["skill_id"]).casefold(), str(item["skill_id"])))
    refresh_paths = sorted(
        (repo / "config" / "catalogue-skill-updates").glob("*.json"),
        key=lambda path: path.as_posix().casefold(),
    )
    refresh_records = []
    for path in refresh_paths:
        payload = _load_json(path)
        skill_id = payload.get("skill_id")
        baseline_override = (
            refresh_baselines.get(skill_id, {}) if isinstance(skill_id, str) else {}
        )
        refresh_records.append(
            _refresh_record_item(path, payload, workspace, baseline_override)
        )
    refresh_records.sort(
        key=lambda item: (str(item["skill_id"]).casefold(), str(item["skill_id"]))
    )
    due = [item for item in skills if item["disposition_required"]]
    due_refresh = [item for item in refresh_records if item["disposition_required"]]
    return {
        "schema_version": 1,
        "skills": skills,
        "refresh_records": refresh_records,
        "summary": {
            "tracked_skill_count": len(skills),
            "tracked_refresh_count": len(refresh_records),
            "review_due_count": len(due) + len(due_refresh),
            "not_observable_count": sum(
                item["status"] == "not_observable" for item in skills + refresh_records
            ),
        },
        "checks": {
            "automatic_sync_applied": False,
            "source_repositories_mutated": False,
            "workspace_catalogue_mutated": False,
        },
    }


def _source_mapping(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--source-repo must use URL=PATH")
    repository, path = value.split("=", 1)
    if not repository or not path:
        raise argparse.ArgumentTypeError("--source-repo must use URL=PATH")
    return repository, Path(path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--catalog-root", type=Path)
    parser.add_argument(
        "--source-repo",
        action="append",
        default=[],
        type=_source_mapping,
        metavar="URL=PATH",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    mappings = {repository: path for repository, path in args.source_repo}
    try:
        payload = build_report(
            args.repo, mappings, catalog_root=args.catalog_root
        )
    except ValueError as exc:
        print(f"source delta check failed: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
