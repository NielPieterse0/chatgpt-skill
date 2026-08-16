from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from .models import TelemetryEvidence, TelemetrySnapshot

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COUNT_FIELDS = (
    "discovered_count",
    "loaded_count",
    "resource_read_count",
    "evaluated_count",
    "mutation_count",
    "applied_count",
    "completed_count",
    "failed_count",
    "error_count",
)


def _empty(status: str, source: Path, warning: str) -> TelemetrySnapshot:
    return TelemetrySnapshot(groups=(), status=status, source=str(source), warnings=(warning,))


def _timestamp_instant(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


def load_telemetry_sqlite(path: Path | str) -> TelemetrySnapshot:
    source = Path(path).resolve()
    if not source.is_file():
        return _empty("not_available", source, f"KIS telemetry unavailable: {source}")
    uri = source.as_uri() + "?mode=ro"
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=2.0)
        event_count = int(connection.execute("SELECT COUNT(*) FROM skill_events").fetchone()[0])
        rows = connection.execute(
            """
            SELECT skill_id, content_sha256,
              SUM(CASE WHEN event_name='skill_discovered' AND outcome='success' THEN 1 ELSE 0 END),
              SUM(CASE WHEN event_name='skill_loaded' AND outcome='success' THEN 1 ELSE 0 END),
              SUM(CASE WHEN event_name='skill_resource_read' AND outcome='success' THEN 1 ELSE 0 END),
              SUM(CASE WHEN event_name='skill_evaluated' AND outcome='success' THEN 1 ELSE 0 END),
              SUM(CASE WHEN event_name IN ('skill_created','skill_improved') AND outcome='success' THEN 1 ELSE 0 END),
              SUM(CASE WHEN event_name='skill_applied' AND outcome='success' THEN 1 ELSE 0 END),
              SUM(CASE WHEN event_name='skill_completed' AND outcome='success' THEN 1 ELSE 0 END),
              SUM(CASE WHEN event_name='skill_failed' THEN 1 ELSE 0 END),
              SUM(CASE WHEN outcome!='success' THEN 1 ELSE 0 END),
              GROUP_CONCAT(DISTINCT project_id)
            FROM skill_events
            WHERE skill_id IS NOT NULL AND content_sha256 IS NOT NULL
            GROUP BY skill_id, content_sha256
            ORDER BY skill_id, content_sha256
            """
        ).fetchall()
        last_rows = connection.execute(
            """
            SELECT skill_id, content_sha256, occurred_at
            FROM skill_events
            WHERE skill_id IS NOT NULL
              AND content_sha256 IS NOT NULL
              AND event_name IN ('skill_loaded','skill_resource_read','skill_applied','skill_completed','skill_failed')
            ORDER BY skill_id, content_sha256, id
            """
        ).fetchall()
    except (sqlite3.Error, OSError) as exc:
        return _empty("invalid", source, f"KIS telemetry invalid: {exc}")
    finally:
        if connection is not None:
            connection.close()
    latest: dict[tuple[str, str], tuple[datetime, str]] = {}
    malformed_timestamps = 0
    for skill_id, digest, occurred_at in last_rows:
        instant = _timestamp_instant(occurred_at)
        if instant is None:
            malformed_timestamps += 1
            continue
        identity = (str(skill_id), str(digest))
        previous = latest.get(identity)
        if previous is None or instant > previous[0]:
            latest[identity] = (instant, str(occurred_at))
    groups = tuple(
        TelemetryEvidence(
            skill_id=str(row[0]),
            content_sha256=str(row[1]),
            discovered_count=int(row[2] or 0),
            loaded_count=int(row[3] or 0),
            resource_read_count=int(row[4] or 0),
            evaluated_count=int(row[5] or 0),
            mutation_count=int(row[6] or 0),
            applied_count=int(row[7] or 0),
            completed_count=int(row[8] or 0),
            failed_count=int(row[9] or 0),
            error_count=int(row[10] or 0),
            last_used_at=(latest.get((str(row[0]), str(row[1]))) or (None, None))[1],
            last_used_status=(
                "observed"
                if (str(row[0]), str(row[1])) in latest
                else "not_observed"
            ),
            projects=tuple(sorted(filter(None, str(row[11] or "").split(",")))),
        )
        for row in rows
    )
    warnings: list[str] = []
    if malformed_timestamps:
        warnings.append(
            f"KIS telemetry contains {malformed_timestamps} last-use event timestamp(s) that are not offset-aware ISO-8601"
        )
    retention_bound = event_count >= 20_000
    if retention_bound:
        warnings.append("KIS telemetry is at the documented 20,000-event retention bound; older usage may be incomplete")
    return TelemetrySnapshot(
        groups=groups,
        status="truncated" if retention_bound else "observed",
        source=str(source),
        event_count=event_count,
        warnings=tuple(warnings),
    )


def load_telemetry_json(path: Path | str) -> TelemetrySnapshot:
    source = Path(path).resolve()
    if not source.is_file():
        return _empty("not_available", source, f"KIS telemetry report unavailable: {source}")
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or not isinstance(raw.get("groups"), list):
            raise ValueError("report must contain a groups array")
        if raw.get("schema_version") != 1:
            raise ValueError("schema_version must be 1")
        truncated_value = raw.get("truncated")
        if not isinstance(truncated_value, bool):
            raise ValueError("truncated must be boolean")
        event_count = raw.get("event_count")
        if not isinstance(event_count, int) or isinstance(event_count, bool) or event_count < 0:
            raise ValueError("event_count must be a non-negative integer")
        totals: dict[tuple[str, str], dict[str, object]] = defaultdict(dict)
        for group in raw["groups"]:
            if not isinstance(group, dict):
                raise ValueError("telemetry group must be an object")
            skill_id = group.get("skill_id")
            digest = group.get("content_sha256")
            if not isinstance(skill_id, str) or not skill_id.strip():
                raise ValueError("telemetry group skill_id must be a non-empty string")
            if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
                raise ValueError("telemetry group content_sha256 must be lowercase SHA-256 hex")
            key = (skill_id, digest)
            record = totals[key]
            record.setdefault("projects", set())
            project = group.get("project_id")
            if isinstance(project, str):
                record["projects"].add(project)
            for field in _COUNT_FIELDS:
                value = group.get(field)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError(f"{field} must be a non-negative integer")
                record[field] = int(record.get(field, 0)) + value
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return _empty("invalid", source, f"KIS telemetry report invalid: {exc}")
    groups = tuple(
        TelemetryEvidence(
            skill_id=skill_id,
            content_sha256=digest,
            **{field: int(values.get(field, 0)) for field in _COUNT_FIELDS},
            last_used_at=None,
            last_used_status="not_observable",
            projects=tuple(sorted(values.get("projects", set()))),
        )
        for (skill_id, digest), values in sorted(totals.items())
    )
    truncated = truncated_value
    warnings = (
        ("KIS telemetry report is truncated; usage aggregates are incomplete",)
        if truncated
        else ()
    )
    return TelemetrySnapshot(
        groups=groups,
        status="truncated" if truncated else "observed",
        source=str(source),
        event_count=event_count,
        warnings=warnings,
    )
