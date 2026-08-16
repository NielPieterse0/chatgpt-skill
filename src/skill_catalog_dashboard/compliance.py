from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


_MATRIX = Path("docs/audits/agent-skills-compliance-matrix.json")
_STATUS_KEYS = {
    "compliant": "compliant",
    "partially_compliant": "partial",
    "non_compliant": "non_compliant",
    "not_evidenced": "unevidenced",
    "intentionally_divergent": "intentionally_divergent",
    "not_applicable": "not_applicable",
}


def _empty(status: str) -> dict[str, object]:
    return {
        "status": status,
        "counts": {},
        "audit_age_days": None,
        "source_drift_count": None,
    }


def _bounded(repo: Path, raw: object) -> Path | None:
    if not isinstance(raw, str):
        return None
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        return None
    resolved = (repo / path).resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        return None
    return resolved


def load_compliance_summary(repo_root: Path | str) -> dict[str, object]:
    repo = Path(repo_root).resolve()
    matrix_path = repo / _MATRIX
    if matrix_path.is_symlink():
        return _empty("invalid")
    if not matrix_path.is_file():
        return _empty("not_available")
    try:
        value: Any = json.loads(matrix_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _empty("invalid")
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        return _empty("invalid")
    requirements = value.get("requirements")
    sources = value.get("sources")
    reaudit = value.get("reaudit")
    if not isinstance(requirements, list) or not isinstance(sources, dict):
        return _empty("invalid")
    if not isinstance(reaudit, dict) or set(reaudit) != {"max_age_days", "triggers"}:
        return _empty("invalid")
    max_age_days = reaudit.get("max_age_days")
    triggers = reaudit.get("triggers")
    if (
        not isinstance(max_age_days, int)
        or isinstance(max_age_days, bool)
        or max_age_days < 1
        or not isinstance(triggers, list)
        or not triggers
        or not all(isinstance(trigger, str) and trigger.strip() for trigger in triggers)
    ):
        return _empty("invalid")
    counts = Counter(
        item.get("status")
        for item in requirements
        if isinstance(item, dict) and item.get("status") in _STATUS_KEYS
    )
    drift = 0
    for entry in sources.values():
        if not isinstance(entry, dict):
            return _empty("invalid")
        path = _bounded(repo, entry.get("path"))
        expected = entry.get("sha256")
        if path is None or not path.is_file() or not isinstance(expected, str):
            drift += 1
            continue
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            drift += 1
            continue
        if actual != expected:
            drift += 1
    try:
        audit_date = date.fromisoformat(str(value.get("audited_at")))
        age = (date.today() - audit_date).days
    except ValueError:
        return _empty("invalid")
    if age < 0:
        return _empty("invalid")
    status = "stale_source" if drift else ("stale_audit" if age > max_age_days else "observed")
    rendered = {output: counts.get(source, 0) for source, output in _STATUS_KEYS.items()}
    return {
        "status": status,
        "counts": rendered,
        "audit_age_days": age,
        "source_drift_count": drift,
    }
