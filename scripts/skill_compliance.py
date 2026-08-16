#!/usr/bin/env python3
"""Validate the repository Agent Skills compliance audit and emit JSON evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


CLASSIFICATIONS = {"normative", "recommended", "contextual"}
STATUSES = {
    "compliant",
    "partially_compliant",
    "non_compliant",
    "not_applicable",
    "intentionally_divergent",
    "not_evidenced",
}
REQ_KEYS = {
    "id", "source_id", "section", "classification", "status",
    "repository_control", "evidence", "gap", "remediation_or_justification",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQ_ID_RE = re.compile(r"^[A-Z]+-[0-9]{3}$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EXPECTED_SOURCES = {
    "AS-01": "references/agent-skills-specification.md",
    "AS-08": "references/agents-skills-support.md",
    "AS-05": "references/optimising-skill-description.md",
    "AS-06": "references/evaluating-skills.md",
    "AS-07": "references/using-scripts-skills.md",
    "AS-04": "references/skills-best-practice.md",
}


def _error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def _load_matrix(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid compliance matrix: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("compliance matrix root must be an object")
    return value


def _repo_path(repo: Path, raw: str) -> Path | None:
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (repo / candidate).resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        return None
    return resolved


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_sources(
    repo: Path, sources: Any, errors: list[dict[str, str]]
) -> int:
    if not isinstance(sources, dict) or not sources:
        _error(errors, "SOURCES_INVALID", "sources must be a non-empty object")
        return 0
    if set(sources) != set(EXPECTED_SOURCES):
        _error(errors, "SOURCE_IDENTITY_MISMATCH", "audited source IDs do not match the required baseline")
    drift = 0
    for source_id, entry in sorted(sources.items()):
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "title"}:
            _error(errors, "SOURCE_INVALID", f"{source_id} has invalid source metadata")
            continue
        raw_path = entry.get("path")
        expected = entry.get("sha256")
        if raw_path != EXPECTED_SOURCES.get(source_id):
            _error(errors, "SOURCE_IDENTITY_MISMATCH", f"{source_id} path does not match the required baseline")
        if not isinstance(raw_path, str) or not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            _error(errors, "SOURCE_INVALID", f"{source_id} path/hash is invalid")
            continue
        path = _repo_path(repo, raw_path)
        if path is None or not path.is_file():
            _error(errors, "SOURCE_MISSING", f"{source_id} source missing: {raw_path}")
            drift += 1
            continue
        actual = _sha256(path)
        if actual != expected:
            _error(errors, "SOURCE_HASH_MISMATCH", f"{source_id} source fingerprint changed")
            drift += 1
    return drift


def _validate_requirements(
    repo: Path,
    requirements: Any,
    source_ids: set[str],
    errors: list[dict[str, str]],
) -> dict[str, Counter[str]]:
    summary: dict[str, Counter[str]] = defaultdict(Counter)
    if not isinstance(requirements, list) or not requirements:
        _error(errors, "REQUIREMENTS_INVALID", "requirements must be a non-empty list")
        return summary
    seen: set[str] = set()
    for index, item in enumerate(requirements):
        if not isinstance(item, dict) or set(item) != REQ_KEYS:
            _error(errors, "REQUIREMENT_INVALID", f"requirement[{index}] has invalid fields")
            continue
        req_id = item.get("id")
        classification = item.get("classification")
        status = item.get("status")
        if not isinstance(req_id, str) or REQ_ID_RE.fullmatch(req_id) is None or req_id in seen:
            _error(errors, "REQUIREMENT_ID_INVALID", f"invalid or duplicate requirement id: {req_id}")
            continue
        seen.add(req_id)
        if classification not in CLASSIFICATIONS or status not in STATUSES:
            _error(errors, "REQUIREMENT_INVALID", f"{req_id} classification/status is invalid")
            continue
        summary[classification][status] += 1
        if item.get("source_id") not in source_ids:
            _error(errors, "SOURCE_ID_UNKNOWN", f"{req_id} references unknown source")
        for field in ("section", "repository_control"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                _error(errors, "REQUIREMENT_INVALID", f"{req_id} requires {field}")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(isinstance(v, str) and v for v in evidence):
            _error(errors, "EVIDENCE_INVALID", f"{req_id} evidence must be a non-empty path list")
            continue
        for raw_path in evidence:
            path = _repo_path(repo, raw_path)
            if path is None or not path.exists():
                _error(errors, "EVIDENCE_MISSING", f"{req_id} evidence missing: {raw_path}")
        if status == "compliant" and not evidence:
            _error(errors, "EVIDENCE_MISSING", f"{req_id} compliant claim lacks evidence")
        if status == "intentionally_divergent" and not str(item.get("remediation_or_justification", "")).strip():
            _error(errors, "DIVERGENCE_UNJUSTIFIED", f"{req_id} divergence lacks justification")
        if classification == "normative" and status != "compliant":
            _error(errors, "NORMATIVE_GAP", f"{req_id} normative requirement is {status}")
    return summary


def _package_checks(repo: Path) -> dict[str, int]:
    skills_root = repo / "skills"
    skill_count = 0
    invalid_reference_count = 0
    over_500_line_count = 0
    if not skills_root.is_dir():
        return {
            "skill_count": 0,
            "invalid_reference_count": 0,
            "over_500_line_count": 0,
        }
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        skill_count += 1
        text = skill_md.read_text(encoding="utf-8")
        if len(text.splitlines()) > 500:
            over_500_line_count += 1
        for target in LINK_RE.findall(text):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("#"):
                continue
            raw = target[2:] if target.startswith("./") else target
            path = (skill_dir / raw).resolve()
            try:
                path.relative_to(skill_dir.resolve())
            except ValueError:
                invalid_reference_count += 1
                continue
            if not path.is_file():
                invalid_reference_count += 1
    return {
        "skill_count": skill_count,
        "invalid_reference_count": invalid_reference_count,
        "over_500_line_count": over_500_line_count,
    }


def validate(repo: Path, matrix_path: Path) -> dict[str, Any]:
    repo = repo.resolve()
    errors: list[dict[str, str]] = []
    try:
        matrix = _load_matrix(matrix_path)
    except ValueError as exc:
        return {"ok": False, "errors": [{"code": "MATRIX_INVALID", "message": str(exc)}]}
    required_root = {"schema_version", "audit_id", "audited_at", "sources", "requirements", "divergences", "reaudit"}
    if set(matrix) != required_root or matrix.get("schema_version") != 1:
        _error(errors, "MATRIX_INVALID", "matrix root fields/schema_version are invalid")
    if matrix.get("audit_id") != "agent-skills-compliance":
        _error(errors, "MATRIX_INVALID", "audit_id is invalid")
    sources = matrix.get("sources")
    source_ids = set(sources) if isinstance(sources, dict) else set()
    source_drift_count = _validate_sources(repo, sources, errors)
    summary = _validate_requirements(repo, matrix.get("requirements"), source_ids, errors)
    divergences = matrix.get("divergences")
    divergent_ids = {
        item["id"]
        for item in matrix.get("requirements", [])
        if isinstance(item, dict) and item.get("status") == "intentionally_divergent" and isinstance(item.get("id"), str)
    }
    registered: set[str] = set()
    if not isinstance(divergences, list):
        _error(errors, "DIVERGENCE_INVALID", "divergences must be a list")
    else:
        for item in divergences:
            if not isinstance(item, dict) or set(item) != {"id", "requirement_ids", "policy", "rationale", "evidence"}:
                _error(errors, "DIVERGENCE_INVALID", "divergence record has invalid fields")
                continue
            req_ids = item.get("requirement_ids")
            if isinstance(req_ids, list):
                registered.update(value for value in req_ids if isinstance(value, str))
            for raw_path in item.get("evidence", []):
                path = _repo_path(repo, raw_path) if isinstance(raw_path, str) else None
                if path is None or not path.exists():
                    _error(errors, "EVIDENCE_MISSING", f"divergence evidence missing: {raw_path}")
    for req_id in sorted(divergent_ids - registered):
        _error(errors, "DIVERGENCE_UNREGISTERED", f"{req_id} lacks divergence register entry")

    reaudit = matrix.get("reaudit")
    max_age_days: int | None = None
    if not isinstance(reaudit, dict) or set(reaudit) != {"max_age_days", "triggers"}:
        _error(errors, "REAUDIT_INVALID", "reaudit must define max_age_days and triggers")
    else:
        candidate_age = reaudit.get("max_age_days")
        triggers = reaudit.get("triggers")
        if not isinstance(candidate_age, int) or isinstance(candidate_age, bool) or candidate_age < 1:
            _error(errors, "REAUDIT_INVALID", "reaudit max_age_days must be a positive integer")
        else:
            max_age_days = candidate_age
        if not isinstance(triggers, list) or not triggers or not all(
            isinstance(trigger, str) and trigger.strip() for trigger in triggers
        ):
            _error(errors, "REAUDIT_INVALID", "reaudit triggers must be a non-empty string list")

    try:
        audited_at = date.fromisoformat(str(matrix.get("audited_at")))
        audit_age_days = (date.today() - audited_at).days
        if audit_age_days < 0:
            _error(errors, "MATRIX_INVALID", "audited_at cannot be in the future")
        elif max_age_days is not None and audit_age_days > max_age_days:
            _error(errors, "AUDIT_STALE", f"audit age {audit_age_days} exceeds {max_age_days} days")
    except ValueError:
        audit_age_days = -1
        _error(errors, "MATRIX_INVALID", "audited_at must be ISO date")
    package_checks = _package_checks(repo)
    if package_checks["invalid_reference_count"]:
        _error(errors, "PACKAGE_REFERENCE_INVALID", "one or more adopted SKILL.md references are invalid")
    if package_checks["over_500_line_count"]:
        _error(errors, "PACKAGE_SIZE_RECOMMENDATION", "one or more adopted SKILL.md files exceed 500 lines")

    rendered_summary = {
        classification: {status: counts.get(status, 0) for status in sorted(STATUSES)}
        for classification, counts in sorted(summary.items())
    }
    return {
        "ok": not errors,
        "audit_id": matrix.get("audit_id"),
        "audited_at": matrix.get("audited_at"),
        "audit_age_days": audit_age_days,
        "source_drift_count": source_drift_count,
        "summary": rendered_summary,
        "package_checks": package_checks,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate repository Agent Skills compliance evidence.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_cmd = sub.add_parser("validate")
    validate_cmd.add_argument("--repo", type=Path, default=Path.cwd())
    validate_cmd.add_argument("--matrix", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = args.repo.resolve()
    matrix = args.matrix or (repo / "docs" / "audits" / "agent-skills-compliance-matrix.json")
    result = validate(repo, matrix.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
