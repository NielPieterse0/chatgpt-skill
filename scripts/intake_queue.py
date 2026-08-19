#!/usr/bin/env python3
"""Validate and report the repository-owned candidate intake queue."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skill_catalog_dashboard.intake import load_intake_queue, validate_intake_root


def _record_dict(item) -> dict[str, object]:
    return {
        "candidate_id": item.candidate_id,
        "candidate_type": item.candidate_type,
        "source_issue": f"{item.source_repository}#{item.source_issue_number}",
        "work_management_state": item.work_management_state,
        "provenance": f"{item.provenance_type}:{item.provenance_state}",
        "license_state": item.license_state,
        "evaluation_state": item.evaluation_state,
        "disposition": item.disposition,
        "next_action": item.next_action,
        "warnings": list(item.warnings),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "report"))
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        snapshot = (
            validate_intake_root(args.repo_root)
            if args.command == "validate"
            else load_intake_queue(args.repo_root)
        )
        if args.command == "report" and snapshot.status == "invalid":
            raise ValueError("intake queue is invalid: " + "; ".join(snapshot.warnings))
    except ValueError as exc:
        print(f"intake queue validation failed: {exc}", file=sys.stderr)
        return 1
    payload = {
        "schema_version": 1,
        "status": snapshot.status,
        "candidate_count": len(snapshot.records),
        "actionable_count": sum(item.next_action is not None for item in snapshot.records),
        "candidates": [_record_dict(item) for item in snapshot.records],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
