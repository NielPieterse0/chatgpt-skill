#!/usr/bin/env python3
"""Generate and validate governed full-catalogue evaluation defer evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skill_catalog_dashboard.catalog import discover_catalog
from skill_catalog_dashboard.repo import (
    _programme_evaluations,
    _programme_snapshot_hash,
    collect_repository_evidence,
)


PROGRAMME_RELATIVE = Path("docs/testing/full-catalogue-skill-evaluation.json")
DEFINITION_FILES = ("trigger-cases.json", "output-evals.json", "abuse-cases.json")
GLOBAL_LIMITATIONS = [
    "isolated_candidate_vs_baseline_runner_unavailable",
    "activation_observability_unavailable",
    "human_review_pending",
]
REEVALUATION_TRIGGERS = [
    "canonical skill content hash changes",
    "canonical catalogue membership or active status changes",
    "isolated candidate-vs-baseline execution becomes available",
    "reliable activation observability becomes available",
    "human review is completed",
    "runtime adapter or target behavior materially changes",
    "security, quality, or operational regression evidence appears",
]


def _source_revision(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    revision = completed.stdout.strip()
    if completed.returncode != 0 or len(revision) not in {40, 64}:
        raise ValueError("cannot resolve full repository source revision")
    return revision


def _package_metrics(skill_dir: Path) -> dict[str, int]:
    file_count = 0
    total_bytes = 0
    symlink_count = 0
    for path in skill_dir.rglob("*"):
        if path.is_symlink():
            symlink_count += 1
            continue
        if path.is_file():
            file_count += 1
            total_bytes += path.stat().st_size
    skill_md = skill_dir / "SKILL.md"
    lines = len(skill_md.read_text(encoding="utf-8").splitlines())
    return {
        "file_count": file_count,
        "total_bytes": total_bytes,
        "skill_md_lines": lines,
        "symlink_count": symlink_count,
    }


def _definition_status(repo: Path, skill_id: str) -> str:
    root = repo / "tests" / "skills" / skill_id
    present = sum((root / name).is_file() for name in DEFINITION_FILES)
    if present == len(DEFINITION_FILES):
        return "complete"
    if present:
        return "partial"
    return "missing"


def _prior_top_five(repo: Path) -> dict[str, str]:
    path = repo / "docs" / "testing" / "top-five-skill-evaluation.json"
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    results = value.get("results") if isinstance(value, dict) else None
    if not isinstance(results, list):
        return {}
    output: dict[str, str] = {}
    for item in results:
        if not isinstance(item, dict):
            continue
        skill_id = item.get("skill_id")
        digest = item.get("content_sha256")
        if isinstance(skill_id, str) and isinstance(digest, str):
            output[skill_id] = digest
    return output


def _adoption_state(status: str, adopted_hash: str | None, current_hash: str) -> str:
    if status == "approved":
        return "approved_current" if adopted_hash == current_hash else "approved_stale"
    return "not_recorded"


def _blocking_reasons(
    *,
    definition_status: str,
    adoption_status: str,
    prior_status: str,
) -> list[str]:
    reasons = [*GLOBAL_LIMITATIONS]
    if definition_status == "missing":
        reasons.append("tracked_evaluation_definitions_missing")
    elif definition_status == "partial":
        reasons.append("tracked_evaluation_definitions_incomplete")
    if adoption_status == "not_recorded":
        reasons.append("repository_adoption_identity_not_recorded")
    elif adoption_status == "approved_stale":
        reasons.append("repository_adoption_identity_differs_from_current_catalogue_hash")
    if prior_status == "stale":
        reasons.append("prior_issue_54_evidence_hash_is_stale")
    return reasons


def generate_document(
    *,
    repo: Path,
    catalog_root: Path,
    evaluated_at: str,
    source_revision: str,
) -> dict[str, object]:
    inventory = discover_catalog([catalog_root])
    if inventory.root_statuses != ((str(catalog_root.resolve()), "observed"),):
        raise ValueError("catalogue root is not fully observable")
    active = tuple(entry for entry in inventory.entries if entry.status == "active")
    if not active:
        raise ValueError("canonical catalogue has no active skills")
    if len(active) != len(inventory.entries):
        raise ValueError("non-active or invalid catalogue entries require explicit programme handling")
    if any(entry.parse_status != "valid" or entry.content_sha256 is None for entry in active):
        raise ValueError("one or more active catalogue entries are structurally invalid")

    repository = collect_repository_evidence(repo, active)
    top_five = _prior_top_five(repo)
    rows: list[dict[str, object]] = []
    for entry in active:
        digest = entry.content_sha256 or ""
        metrics = _package_metrics(Path(entry.source_path))
        if metrics["file_count"] < 1 or metrics["skill_md_lines"] < 1 or metrics["symlink_count"]:
            raise ValueError(f"structural package check failed for {entry.name}")
        evidence = repository[entry.name]
        adoption_status = _adoption_state(
            evidence.adoption_status,
            evidence.adopted_content_sha256,
            digest,
        )
        definition_status = _definition_status(repo, entry.name)
        prior_hash = top_five.get(entry.name)
        if prior_hash is None:
            prior_status = "not_in_cohort"
        else:
            prior_status = "current" if prior_hash == digest else "stale"
        rows.append(
            {
                "skill_id": entry.name,
                "content_sha256": digest,
                "catalogue_status": "active",
                "structural_status": "pass",
                "structural_evidence": metrics,
                "repo_adoption_status": adoption_status,
                "tracked_definition_status": definition_status,
                "behavioral_status": "not_observable",
                "compatibility_status": "partial",
                "human_review_status": "pending",
                "recommendation": "defer",
                "blocking_reasons": _blocking_reasons(
                    definition_status=definition_status,
                    adoption_status=adoption_status,
                    prior_status=prior_status,
                ),
                "prior_issue_54_status": prior_status,
            }
        )
    count = len(rows)
    return {
        "schema_version": 1,
        "issue": 55,
        "evaluated_at": evaluated_at,
        "source_revision": source_revision,
        "catalogue_root": str(catalog_root.resolve()),
        "catalogue_snapshot_sha256": _programme_snapshot_hash(rows),
        "owner": "chatgpt-skill evaluation programme",
        "evaluation_standard": "docs/testing/skill-evaluation-standard.md",
        "global_limitations": list(GLOBAL_LIMITATIONS),
        "coverage": {
            "total_catalogue_count": count,
            "active_count": count,
            "current_covered_count": count,
            "current_coverage": 1.0,
            "defer_count": count,
            "suspend_count": 0,
        },
        "skills": rows,
        "re_evaluation": {
            "owner": "chatgpt-skill evaluation programme",
            "max_age_days": 90,
            "triggers": list(REEVALUATION_TRIGGERS),
        },
    }


def validate_record(
    *, repo: Path, record: Path, catalog_root: Path | None
) -> dict[str, object]:
    expected = (repo / PROGRAMME_RELATIVE).resolve()
    errors: list[dict[str, str]] = []
    if record.resolve() != expected:
        errors.append({"code": "RECORD_PATH_INVALID", "message": f"record must be {expected}"})
        return {"ok": False, "current_covered_count": 0, "errors": errors}
    mapping, _, evaluated_at, expired, warnings = _programme_evaluations(repo)
    for warning in warnings:
        errors.append({"code": "RECORD_INVALID", "message": warning})
    if expired:
        errors.append({"code": "EVALUATION_STALE", "message": "programme evidence exceeds re-evaluation age"})
    if catalog_root is not None and mapping:
        inventory = discover_catalog([catalog_root])
        active = {
            entry.name: entry.content_sha256
            for entry in inventory.entries
            if entry.status == "active" and entry.parse_status == "valid"
        }
        recorded = {name: row.get("content_sha256") for name, row in mapping.items()}
        if active != recorded:
            errors.append(
                {
                    "code": "CATALOGUE_DRIFT",
                    "message": "live active catalogue identity/hash set differs from tracked programme evidence",
                }
            )
    return {
        "ok": not errors and bool(mapping),
        "evaluated_at": evaluated_at,
        "current_covered_count": len(mapping) if not errors else 0,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate or validate the governed full-catalogue evaluation record."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate")
    generate.add_argument("--repo", type=Path, default=Path.cwd())
    generate.add_argument("--catalog-root", type=Path, required=True)
    generate.add_argument("--output", type=Path)
    generate.add_argument("--evaluated-at", required=True)
    generate.add_argument("--source-revision")

    validate = sub.add_parser("validate")
    validate.add_argument("--repo", type=Path, default=Path.cwd())
    validate.add_argument("--record", type=Path)
    validate.add_argument("--catalog-root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = args.repo.resolve()
    if args.command == "generate":
        output = (args.output or (repo / PROGRAMME_RELATIVE)).resolve()
        expected = (repo / PROGRAMME_RELATIVE).resolve()
        if output != expected:
            print(json.dumps({"ok": False, "error": f"output must be {expected}"}))
            return 2
        revision = args.source_revision or _source_revision(repo)
        try:
            document = generate_document(
                repo=repo,
                catalog_root=args.catalog_root.resolve(),
                evaluated_at=args.evaluated_at,
                source_revision=revision,
            )
        except (OSError, UnicodeError, ValueError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}))
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = validate_record(repo=repo, record=output, catalog_root=args.catalog_root.resolve())
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 2

    record = (args.record or (repo / PROGRAMME_RELATIVE)).resolve()
    result = validate_record(
        repo=repo,
        record=record,
        catalog_root=args.catalog_root.resolve() if args.catalog_root else None,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
