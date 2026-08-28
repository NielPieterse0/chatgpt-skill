#!/usr/bin/env python3
"""Synchronize merged repository skills into the canonical workspace catalogue."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

DEFAULT_CATALOGUE_ROOT = Path(os.environ.get("CHATGPT_SKILL_CATALOGUE_ROOT", r"C:\Projects\.agents\skills"))


class SyncError(RuntimeError):
    """Raised when catalogue publication cannot be proven safe."""


@dataclass(frozen=True)
class TreeFile:
    path: PurePosixPath
    content: bytes


def _git(repo: Path, args: list[str], *, binary: bool = False) -> str | bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=not binary,
        timeout=30,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", "replace") if binary else completed.stderr
        raise SyncError(f"git {' '.join(args)} failed: {stderr.strip()}")
    return completed.stdout


def _resolve_ref(repo: Path, ref: str) -> str:
    return str(_git(repo, ["rev-parse", "--verify", f"{ref}^{{commit}}"])).strip()


def _first_parent(repo: Path, commit: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", f"{commit}^1"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def _tree_files(repo: Path, commit: str | None, skill: str) -> list[TreeFile]:
    if commit is None:
        return []
    prefix = PurePosixPath("skills") / skill
    raw = _git(repo, ["ls-tree", "-r", "-z", commit, "--", prefix.as_posix()], binary=True)
    assert isinstance(raw, bytes)
    files: list[TreeFile] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        if object_type != "blob" or mode == "120000":
            raise SyncError(f"Unsupported catalogue entry for {skill}: {raw_path.decode('utf-8', 'replace')}")
        full_path = PurePosixPath(raw_path.decode("utf-8"))
        try:
            relative = full_path.relative_to(prefix)
        except ValueError as exc:
            raise SyncError(f"Unsafe skill path in Git tree: {full_path}") from exc
        if not relative.parts or ".." in relative.parts:
            raise SyncError(f"Unsafe skill path in Git tree: {full_path}")
        content = _git(repo, ["cat-file", "blob", object_id], binary=True)
        assert isinstance(content, bytes)
        files.append(TreeFile(relative, content))
    return sorted(files, key=lambda item: item.path.as_posix())


def _runtime_files(files: Iterable[TreeFile]) -> list[TreeFile]:
    """Project a repository skill package to its runtime Agent Skill contents."""
    return [item for item in files if item.path.as_posix() != "adoption-manifest.json"]


def _digest_files(files: Iterable[TreeFile]) -> str:
    digest = hashlib.sha256()
    for item in sorted(files, key=lambda value: value.path.as_posix()):
        relative = item.path.as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(item.content).to_bytes(8, "big"))
        digest.update(item.content)
    return digest.hexdigest()


def _directory_files(path: Path) -> list[TreeFile]:
    if path.is_symlink():
        raise SyncError(f"Catalogue skill directory is a symlink: {path}")
    files: list[TreeFile] = []
    for candidate in sorted(path.rglob("*")):
        if candidate.is_symlink():
            raise SyncError(f"Catalogue skill contains a symlink: {candidate}")
        if candidate.is_file():
            relative = PurePosixPath(candidate.relative_to(path).as_posix())
            files.append(TreeFile(relative, candidate.read_bytes()))
    return files


def _accepted_skill_runtime_digests(repo: Path, after: str, skill: str) -> dict[str, str]:
    """Map runtime digests to accepted first-parent commits for one skill."""
    output = str(
        _git(repo, ["log", "--first-parent", "--format=%H", after, "--", f"skills/{skill}"])
    ).splitlines()
    accepted: dict[str, str] = {}
    for commit in output:
        files = _runtime_files(_tree_files(repo, commit.strip(), skill))
        if files and any(item.path.as_posix() == "SKILL.md" for item in files):
            accepted.setdefault(_digest_files(files), commit.strip())
    return accepted


def _changed_skills(repo: Path, before: str | None, after: str) -> list[str]:
    if before is None:
        paths = str(_git(repo, ["ls-tree", "-d", "--name-only", f"{after}:skills"])).splitlines()
        return sorted(path.strip() for path in paths if path.strip())
    output = str(_git(repo, ["diff", "--name-only", before, after, "--", "skills"])).splitlines()
    names = set()
    for raw_path in output:
        parts = PurePosixPath(raw_path).parts
        if len(parts) >= 2 and parts[0] == "skills":
            names.add(parts[1])
    return sorted(names)


def _write_tree(target: Path, files: list[TreeFile]) -> None:
    for item in files:
        destination = target.joinpath(*item.path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(item.content)


def _replace_directory(destination: Path, files: list[TreeFile], catalogue_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="chatgpt-skill-sync-", dir=str(catalogue_root.parent)) as temp_name:
        temp_root = Path(temp_name)
        staged = temp_root / destination.name
        staged.mkdir(parents=True)
        _write_tree(staged, files)
        if destination.exists():
            backup = temp_root / "previous"
            os.replace(destination, backup)
            try:
                os.replace(staged, destination)
            except Exception:
                os.replace(backup, destination)
                raise
        else:
            os.replace(staged, destination)


def _preflight_skill(repo: Path, catalogue_root: Path, before: str | None, after: str, skill: str) -> dict[str, object]:
    current_package_files = _tree_files(repo, after, skill)
    previous_package_files = _tree_files(repo, before, skill)
    destination = catalogue_root / skill

    if not current_package_files:
        if previous_package_files:
            return {"skill": skill, "action": "blocked", "reason": "repository deletion requires explicit manual catalogue retirement"}
        return {"skill": skill, "action": "blocked", "reason": "skill does not exist in the accepted source commit"}

    current_names = {item.path.as_posix() for item in current_package_files}
    if "SKILL.md" not in current_names or "adoption-manifest.json" not in current_names:
        return {"skill": skill, "action": "blocked", "reason": "accepted skill tree lacks SKILL.md or adoption-manifest.json"}

    current_files = _runtime_files(current_package_files)
    previous_files = _runtime_files(previous_package_files)
    current_digest = _digest_files(current_files)
    if not destination.exists():
        return {"skill": skill, "action": "create", "digest": current_digest, "files": current_files}
    if not destination.is_dir():
        return {"skill": skill, "action": "blocked", "reason": "catalogue destination exists but is not a directory"}

    destination_digest = _digest_files(_directory_files(destination))
    if destination_digest == current_digest:
        return {"skill": skill, "action": "unchanged", "digest": current_digest}

    previous_digest = _digest_files(previous_files) if previous_files else None
    accepted_digests = _accepted_skill_runtime_digests(repo, after, skill)
    matched_commit = accepted_digests.get(destination_digest)
    if matched_commit is None:
        return {
            "skill": skill,
            "action": "blocked",
            "reason": "catalogue content diverged from accepted runtime history for this skill",
            "catalogue_digest": destination_digest,
            "current_digest": current_digest,
            "previous_digest": previous_digest,
        }
    return {
        "skill": skill,
        "action": "update",
        "digest": current_digest,
        "matched_accepted_commit": matched_commit,
        "files": current_files,
    }


def sync_catalogue(
    repo_root: Path,
    catalogue_root: Path,
    source_ref: str = "origin/main",
    skills: list[str] | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, object]:
    repo_root = repo_root.resolve(strict=True)
    catalogue_root = catalogue_root.resolve(strict=True)
    if not catalogue_root.is_dir():
        raise SyncError(f"Catalogue root is not a directory: {catalogue_root}")

    source_commit = _resolve_ref(repo_root, source_ref)
    origin_main = _resolve_ref(repo_root, "refs/remotes/origin/main")
    if source_commit != origin_main:
        raise SyncError(
            f"Source ref {source_ref!r} resolves to {source_commit}, not accepted origin/main {origin_main}."
        )
    before = _first_parent(repo_root, source_commit)
    selected = sorted(set(skills if skills is not None else _changed_skills(repo_root, before, source_commit)))
    if any(not name or PurePosixPath(name).name != name or name in {".", ".."} for name in selected):
        raise SyncError("Skill names must be direct, traversal-free catalogue directory names.")

    plans = [_preflight_skill(repo_root, catalogue_root, before, source_commit, name) for name in selected]
    blocked = [plan for plan in plans if plan["action"] == "blocked"]
    public_plans = [{key: value for key, value in plan.items() if key != "files"} for plan in plans]
    result: dict[str, object] = {
        "ok": not blocked,
        "source_commit": source_commit,
        "previous_commit": before,
        "catalogue_root": str(catalogue_root),
        "skills": public_plans,
        "dry_run": dry_run,
    }
    if blocked or dry_run:
        return result

    for plan in plans:
        if plan["action"] in {"create", "update"}:
            _replace_directory(catalogue_root / str(plan["skill"]), plan["files"], catalogue_root)  # type: ignore[arg-type]
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish accepted origin/main skill packages to the canonical workspace catalogue."
    )
    parser.add_argument("--repo", default=".", help="Repository root (default: current directory).")
    parser.add_argument("--catalogue-root", default=str(DEFAULT_CATALOGUE_ROOT), help="Canonical workspace catalogue root.")
    parser.add_argument("--source-ref", default="origin/main", help="Accepted source ref; must resolve to origin/main.")
    parser.add_argument("--skill", action="append", dest="skills", help="Publish one named skill; repeat as needed. Default: skills changed by the accepted commit.")
    parser.add_argument("--dry-run", action="store_true", help="Preflight without writing the catalogue.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = sync_catalogue(Path(args.repo), Path(args.catalogue_root), args.source_ref, args.skills, dry_run=args.dry_run)
    except (OSError, SyncError, subprocess.SubprocessError) as exc:
        json.dump({"ok": False, "error": str(exc)}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 2
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
