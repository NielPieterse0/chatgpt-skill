from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Mapping, Sequence

try:
    from scripts.skill_security import parse_skill_frontmatter
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from skill_security import parse_skill_frontmatter

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_sha256(value: str, label: str) -> str:
    if _SHA256.fullmatch(value) is None:
        raise ValueError(f"{label} must be a lowercase 64-character SHA-256 value")
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


def _collect_files(skill_dir: Path) -> list[Path]:
    if not skill_dir.is_dir():
        raise ValueError("skill directory does not exist")
    if _is_link_like(skill_dir):
        raise ValueError("skill directory must not be a linked or reparse path")

    def fail_walk(error: OSError) -> None:
        raise ValueError(f"unable to enumerate skill package: {skill_dir}") from error

    files: list[Path] = []
    for current, directories, names in os.walk(
        skill_dir, topdown=True, onerror=fail_walk, followlinks=False
    ):
        current_path = Path(current)
        for directory in list(directories):
            child = current_path / directory
            if _is_link_like(child):
                raise ValueError(
                    f"skill contains linked or reparse path: {child.relative_to(skill_dir).as_posix()}"
                )
        for name in names:
            path = current_path / name
            if _is_link_like(path):
                raise ValueError(
                    f"skill contains linked or reparse path: {path.relative_to(skill_dir).as_posix()}"
                )
            if path.is_file():
                files.append(path)
    files.sort(key=lambda item: (item.relative_to(skill_dir).as_posix().casefold(), item.as_posix()))
    return files


def build_projection(
    skill_dir: Path,
    *,
    expected_skill_id: str,
    expected_entrypoint_sha256: str,
    expected_file_count: int,
    expected_snapshot_id: str | None = None,
    expected_resource_hashes: Mapping[str, str] | None = None,
) -> dict:
    """Project one KIS-verified local skill into a draft SEP-2640 evidence envelope.

    This function is deliberately read-only. It produces transport-shape evidence and
    does not register an MCP extension, activate a skill, grant permissions, or mutate
    the canonical workspace catalogue.
    """

    expected_entrypoint_sha256 = _require_sha256(
        expected_entrypoint_sha256, "expected entrypoint SHA-256"
    )
    if isinstance(expected_file_count, bool) or not isinstance(expected_file_count, int):
        raise ValueError("expected file count must be an integer")
    if expected_file_count < 1:
        raise ValueError("expected file count must be positive")

    skill_dir = Path(skill_dir)
    files = _collect_files(skill_dir)
    skill_md = skill_dir / "SKILL.md"
    if skill_md not in files:
        raise ValueError("skill does not contain SKILL.md")

    frontmatter, _ = parse_skill_frontmatter(skill_md)
    skill_id = frontmatter.get("name")
    if skill_id != expected_skill_id:
        raise ValueError(
            f"skill identity mismatch: KIS expected {expected_skill_id!r}, frontmatter has {skill_id!r}"
        )
    if skill_dir.name != expected_skill_id:
        raise ValueError("skill directory name does not match KIS skill identity")

    entrypoint_sha256 = _sha256(skill_md)
    if entrypoint_sha256 != expected_entrypoint_sha256:
        raise ValueError(
            "entrypoint SHA-256 does not match KIS evidence: "
            f"expected {expected_entrypoint_sha256}, observed {entrypoint_sha256}"
        )
    if len(files) != expected_file_count:
        raise ValueError(
            "file count does not match KIS evidence: "
            f"expected {expected_file_count}, observed {len(files)}"
        )

    observed_hashes: dict[str, str] = {}
    resources: list[dict[str, str]] = []
    for path in files:
        relative = path.relative_to(skill_dir).as_posix()
        digest = _sha256(path)
        observed_hashes[relative] = digest
        resources.append(
            {
                "uri": f"skill://{expected_skill_id}/{relative}",
                "digest": f"sha256:{digest}",
            }
        )

    verified_resources: list[dict[str, str | bool]] = []
    for relative, expected_hash in sorted((expected_resource_hashes or {}).items()):
        expected_hash = _require_sha256(expected_hash, f"resource SHA-256 for {relative}")
        normalized = Path(relative).as_posix()
        observed = observed_hashes.get(normalized)
        if observed is None:
            raise ValueError(f"resource from KIS evidence is absent from projection: {normalized}")
        if observed != expected_hash:
            raise ValueError(
                "resource SHA-256 does not match KIS evidence for "
                f"{normalized}: expected {expected_hash}, observed {observed}"
            )
        verified_resources.append(
            {
                "path": normalized,
                "sha256": observed,
                "matched": True,
            }
        )

    resources.sort(key=lambda item: item["uri"].casefold())
    return {
        "schema_version": 1,
        "status": "experimental",
        "sep": "SEP-2640-draft",
        "source": {
            "authority": "kis",
            "skill_id": expected_skill_id,
            "snapshot_id": expected_snapshot_id,
            "entrypoint_sha256": entrypoint_sha256,
            "file_count": len(files),
        },
        "skill_entry": {
            "uri": f"skill://{expected_skill_id}/SKILL.md",
            "frontmatter": frontmatter,
            "resources": resources,
        },
        "checks": {
            "skill_id_match": True,
            "entrypoint_sha256_match": True,
            "file_count_match": True,
            "verified_resources": verified_resources,
            "all_identity_checks_passed": True,
            "permission_grants_applied": False,
        },
    }


def _resource_hashes(values: Sequence[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--resource-hash must use PATH=SHA256")
        path, digest = value.split("=", 1)
        normalized = Path(path.strip()).as_posix()
        if not normalized or normalized.startswith("../") or normalized == "..":
            raise ValueError("--resource-hash path must be relative to the skill root")
        if normalized in result:
            raise ValueError(f"duplicate --resource-hash path: {normalized}")
        result[normalized] = _require_sha256(digest.strip(), f"resource SHA-256 for {normalized}")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Project KIS-verified skill bytes into a read-only draft SEP-2640 evidence envelope."
    )
    parser.add_argument("--skill-dir", required=True, type=Path)
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--entrypoint-sha256", required=True)
    parser.add_argument("--file-count", required=True, type=int)
    parser.add_argument("--snapshot-id")
    parser.add_argument(
        "--resource-hash",
        action="append",
        default=[],
        metavar="PATH=SHA256",
        help="Optional KIS read_skill_file digest to verify against the local projection.",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_projection(
        args.skill_dir,
        expected_skill_id=args.skill_id,
        expected_entrypoint_sha256=args.entrypoint_sha256,
        expected_file_count=args.file_count,
        expected_snapshot_id=args.snapshot_id,
        expected_resource_hashes=_resource_hashes(args.resource_hash),
    )
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
