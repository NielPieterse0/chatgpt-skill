#!/usr/bin/env python3
"""Project the active canonical skill catalogue into read-only MCP resource evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for candidate in (ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from skill_catalog_dashboard.catalog import discover_catalog
from scripts.skills_over_mcp_compat import (
    _collect_files,
    _is_link_like,
    build_projection,
)


def _snapshot_sha256(skills: list[dict[str, object]]) -> str:
    digest = hashlib.sha256()
    for skill in skills:
        digest.update(str(skill["skill_id"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(skill["content_sha256"]).encode("ascii"))
        digest.update(b"\n")
        entry = skill["skill_entry"]
        assert isinstance(entry, dict)
        resources = entry["resources"]
        assert isinstance(resources, list)
        for resource in resources:
            assert isinstance(resource, dict)
            digest.update(str(resource["uri"]).encode("utf-8"))
            digest.update(b"\0")
            digest.update(str(resource["digest"]).encode("ascii"))
            digest.update(b"\n")
    return digest.hexdigest()


def _require_unique_resource_uris(uris: Sequence[str]) -> None:
    seen: dict[str, str] = {}
    for uri in uris:
        folded = uri.casefold()
        prior = seen.get(folded)
        if prior is not None:
            raise ValueError(f"resource URI collision: {prior!r} and {uri!r}")
        seen[folded] = uri


def build_catalogue_projection(
    catalog_root: Path, *, source_snapshot_id: str | None = None
) -> dict[str, object]:
    root = Path(catalog_root)
    if not root.is_dir():
        raise ValueError("catalogue root does not exist")
    if _is_link_like(root):
        raise ValueError("catalogue root must not be a linked or reparse path")

    inventory = discover_catalog([root])
    expected_root = str(root.resolve())
    if inventory.root_statuses != ((expected_root, "observed"),):
        raise ValueError("catalogue root is not fully observable")
    if inventory.warnings:
        raise ValueError("catalogue projection incomplete: " + "; ".join(inventory.warnings))
    invalid = [entry.name for entry in inventory.entries if entry.parse_status != "valid"]
    if invalid:
        raise ValueError("catalogue contains invalid skill entries: " + ", ".join(invalid))

    active = [entry for entry in inventory.entries if entry.status == "active"]
    if not active:
        raise ValueError("catalogue has no active skills")

    skills: list[dict[str, object]] = []
    resource_uris: list[str] = []
    resource_count = 0
    for entry in active:
        if entry.content_sha256 is None:
            raise ValueError(f"active skill lacks content hash: {entry.name}")
        skill_dir = Path(entry.source_path)
        files = _collect_files(skill_dir)
        projection = build_projection(
            skill_dir,
            expected_skill_id=entry.name,
            expected_entrypoint_sha256=entry.content_sha256,
            expected_file_count=len(files),
        )
        resources = projection["skill_entry"]["resources"]
        resource_uris.extend(resource["uri"] for resource in resources)
        _require_unique_resource_uris(resource_uris)
        resource_count += len(resources)
        skills.append(
            {
                "skill_id": entry.name,
                "content_sha256": entry.content_sha256,
                "entrypoint_sha256": projection["source"]["entrypoint_sha256"],
                "file_count": projection["source"]["file_count"],
                "skill_entry": projection["skill_entry"],
            }
        )

    skills.sort(key=lambda item: (str(item["skill_id"]).casefold(), str(item["skill_id"])))
    return {
        "schema_version": 1,
        "status": "experimental",
        "sep": "SEP-2640-draft",
        "catalogue": {
            "authority": "workspace-canonical-catalogue",
            "source_snapshot_id": source_snapshot_id,
            "skill_count": len(skills),
            "resource_count": resource_count,
            "snapshot_sha256": _snapshot_sha256(skills),
        },
        "skills": skills,
        "checks": {
            "all_skills_projected": True,
            "permission_grants_applied": False,
            "catalogue_warnings": [],
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Project an active canonical Agent Skills catalogue into MCP resource evidence."
    )
    parser.add_argument("--catalog-root", required=True, type=Path)
    parser.add_argument("--source-snapshot-id")
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_catalogue_projection(
        args.catalog_root, source_snapshot_id=args.source_snapshot_id
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
