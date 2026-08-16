from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Mapping

from .fs import opened_path
from .models import IntakeRecord, IntakeSnapshot

_CANDIDATE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_REVISION = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_REPOSITORY = "NielPieterse0/chatgpt-skill"

_TOP_LEVEL = {
    "schema_version", "candidate_id", "candidate_type", "requested_at",
    "source_issue", "work_management", "provenance", "license",
    "assessments", "adaptation", "evaluation", "human_review",
    "disposition", "targets",
}
_ASSESSMENT_STATES = {"due", "passed", "failed", "not_applicable"}
_DISPOSITIONS = {"pending", "admit", "defer", "reject"}


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _closed(value: Mapping[str, object], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"{label} has unknown fields: {', '.join(unknown)}")


def _enum(value: object, allowed: set[str], label: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{label} must be one of: {', '.join(sorted(allowed))}")
    return value


def _nullable_pattern(value: object, pattern: re.Pattern[str], label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"{label} is invalid")
    return value


def _date(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO date")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO date") from exc
    return value


def _require_fields(value: Mapping[str, object], fields: set[str], label: str) -> None:
    missing = sorted(fields - set(value))
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(missing)}")


def _validate_source_issue(record: Mapping[str, object]) -> tuple[str, int]:
    value = _mapping(record["source_issue"], "source_issue")
    _closed(value, {"repository", "number"}, "source_issue")
    _require_fields(value, {"repository", "number"}, "source_issue")
    repository = value["repository"]
    number = value["number"]
    if repository != _SOURCE_REPOSITORY:
        raise ValueError(f"source_issue.repository must be {_SOURCE_REPOSITORY}")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError("source_issue.number must be a positive integer")
    return repository, number


def _validate_work_management(record: Mapping[str, object]) -> tuple[str, tuple[str, ...]]:
    value = _mapping(record["work_management"], "work_management")
    allowed = {"state", "record_id", "revision", "blocker_issue"}
    _closed(value, allowed, "work_management")
    _require_fields(value, allowed, "work_management")
    state = _enum(value["state"], {"projected", "not_observed", "blocked"}, "work_management.state")
    warnings: list[str] = []
    record_id, revision, blocker = value["record_id"], value["revision"], value["blocker_issue"]
    if state == "projected":
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("projected Work Management state requires record_id")
        if not isinstance(revision, str) or not revision.strip():
            raise ValueError("projected Work Management state requires revision")
        if blocker is not None:
            raise ValueError("projected Work Management state cannot carry blocker_issue")
    elif record_id is not None or revision is not None:
        raise ValueError("unobserved/blocked Work Management state cannot claim record identity")
    if state == "blocked":
        if not isinstance(blocker, int) or isinstance(blocker, bool) or blocker < 1:
            raise ValueError("blocked Work Management state requires blocker_issue")
        warnings.append(f"Work Management projection blocked by issue #{blocker}")
    elif blocker is not None:
        raise ValueError("not_observed Work Management state cannot carry blocker_issue")
    return state, tuple(warnings)


def _validate_handoff(value: object) -> Mapping[str, object]:
    handoff = _mapping(value, "provenance.handoff")
    allowed = {"case_id", "artifact", "artifact_sha256"}
    _closed(handoff, allowed, "provenance.handoff")
    _require_fields(handoff, allowed, "provenance.handoff")
    for field in ("case_id", "artifact"):
        candidate = handoff[field]
        if not isinstance(candidate, str) or not candidate or len(candidate) > 200:
            raise ValueError(f"provenance.handoff.{field} is invalid")
    _nullable_pattern(handoff["artifact_sha256"], _SHA256, "provenance.handoff.artifact_sha256")
    return handoff


def _validate_provenance(record: Mapping[str, object]) -> tuple[str, str]:
    value = _mapping(record["provenance"], "provenance")
    allowed = {"type", "state", "source_locator", "revision", "candidate_sha256", "handoff"}
    _closed(value, allowed, "provenance")
    _require_fields(value, allowed, "provenance")
    kind = _enum(value["type"], {"import-isolate", "trusted-local"}, "provenance.type")
    state = _enum(value["state"], {"pending", "verified", "blocked"}, "provenance.state")
    locator = value["source_locator"]
    if not isinstance(locator, str) or not locator.strip():
        raise ValueError("provenance.source_locator is required")
    revision = _nullable_pattern(value["revision"], _REVISION, "provenance.revision")
    digest = _nullable_pattern(value["candidate_sha256"], _SHA256, "provenance.candidate_sha256")
    handoff = value["handoff"]
    if kind == "trusted-local":
        if handoff is not None:
            raise ValueError("trusted-local provenance cannot carry import-isolate handoff")
        if state == "verified" and (revision is None or digest is None):
            raise ValueError("verified trusted-local provenance requires revision and candidate_sha256")
    elif state == "verified":
        if revision is None or digest is None or handoff is None:
            raise ValueError("verified provenance requires a finalized import-isolate handoff")
        parsed_handoff = _validate_handoff(handoff)
        if parsed_handoff["artifact_sha256"] != digest:
            raise ValueError("candidate_sha256 must match finalized import-isolate artifact_sha256")
    elif handoff is not None:
        raise ValueError("pending/blocked import-isolate provenance cannot claim finalized handoff")
    if state != "verified" and (revision is not None or digest is not None):
        raise ValueError("pending/blocked provenance cannot claim immutable revision or candidate hash")
    return kind, state


def _validate_license(record: Mapping[str, object]) -> str:
    value = _mapping(record["license"], "license")
    _closed(value, {"state", "identifier"}, "license")
    _require_fields(value, {"state", "identifier"}, "license")
    state = _enum(value["state"], {"pending", "reviewed", "blocked"}, "license.state")
    identifier = value["identifier"]
    if state == "reviewed":
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("reviewed license requires identifier")
    elif identifier is not None:
        raise ValueError("pending/blocked license must not claim reviewed identifier")
    return state


def _validate_assessments(record: Mapping[str, object]) -> dict[str, str]:
    value = _mapping(record["assessments"], "assessments")
    fields = {"structural", "security", "capability", "overlap"}
    _closed(value, fields, "assessments")
    _require_fields(value, fields, "assessments")
    return {
        field: _enum(value[field], _ASSESSMENT_STATES, f"assessments.{field}")
        for field in sorted(fields)
    }


def _single_state(
    record: Mapping[str, object], field: str, allowed: set[str]
) -> str:
    value = _mapping(record[field], field)
    _closed(value, {"state"}, field)
    _require_fields(value, {"state"}, field)
    return _enum(value["state"], allowed, f"{field}.state")


def _validate_targets(record: Mapping[str, object], candidate_type: str) -> dict[str, str]:
    value = _mapping(record["targets"], "targets")
    fields = {
        "workspace_catalogue", "repository_admission", "runtime_enablement",
        "plugin_installation", "plugin_activation",
    }
    _closed(value, fields, "targets")
    _require_fields(value, fields, "targets")
    targets = {
        "workspace_catalogue": _enum(value["workspace_catalogue"], {"pending", "admitted", "rejected", "not_applicable"}, "targets.workspace_catalogue"),
        "repository_admission": _enum(value["repository_admission"], {"pending", "admitted", "rejected", "not_applicable"}, "targets.repository_admission"),
        "runtime_enablement": _enum(value["runtime_enablement"], {"disabled", "pending", "enabled", "not_applicable"}, "targets.runtime_enablement"),
    }
    installation = _enum(
        value["plugin_installation"],
        {"not_installed", "pending", "installed", "not_applicable"},
        "targets.plugin_installation",
    )
    activation = _enum(
        value["plugin_activation"],
        {"inactive", "pending", "active", "not_applicable"},
        "targets.plugin_activation",
    )
    if candidate_type == "skill" and (
        installation != "not_applicable" or activation != "not_applicable"
    ):
        raise ValueError("skill candidate cannot claim plugin installation or activation state")
    if activation == "active" and installation != "installed":
        raise ValueError("plugin activation requires installed plugin state")
    targets["plugin_installation"] = installation
    targets["plugin_activation"] = activation
    return targets


def _next_action(
    provenance_type: str,
    provenance_state: str,
    license_state: str,
    assessments: Mapping[str, str],
    adaptation_state: str,
    evaluation_state: str,
    human_review_state: str,
    disposition: str,
) -> str | None:
    if disposition in {"admit", "defer", "reject"}:
        return None
    if provenance_state == "pending":
        return (
            "await_import_isolate_handoff"
            if provenance_type == "import-isolate"
            else "verify_trusted_local_provenance"
        )
    if provenance_state == "blocked":
        return "resolve_provenance_blocker"
    if license_state == "pending":
        return "review_provenance_license"
    if license_state == "blocked":
        return "resolve_license_blocker"
    if any(state == "failed" for state in assessments.values()):
        return "review_assessment_failure"
    if any(state == "due" for state in assessments.values()):
        return "run_candidate_assessments"
    if adaptation_state in {"required", "in_progress"}:
        return "adapt_candidate"
    if adaptation_state == "pending":
        return "decide_adaptation"
    if adaptation_state == "rejected":
        return "record_disposition"
    if evaluation_state == "blocked":
        return "prepare_evaluation"
    if evaluation_state in {"ready", "in_progress"}:
        return "evaluate_candidate"
    if evaluation_state == "deferred":
        return "record_disposition"
    if human_review_state == "pending":
        return "complete_human_review"
    return "record_disposition"


def _validate_admit_gate(
    disposition: str,
    provenance_state: str,
    license_state: str,
    assessments: Mapping[str, str],
    adaptation_state: str,
    evaluation_state: str,
    human_review_state: str,
) -> None:
    if disposition != "admit":
        return
    if provenance_state != "verified":
        raise ValueError("admit requires verified provenance")
    if license_state != "reviewed":
        raise ValueError("admit requires reviewed license")
    if any(state not in {"passed", "not_applicable"} for state in assessments.values()):
        raise ValueError("admit requires completed candidate assessments")
    if adaptation_state not in {"not_required", "complete"}:
        raise ValueError("admit requires completed adaptation decision")
    if evaluation_state != "complete":
        raise ValueError("admit requires completed evaluation")
    if human_review_state != "complete":
        raise ValueError("admit requires completed human review")


def validate_intake_record(
    payload: Mapping[str, object], *, source_path: str | None = None
) -> IntakeRecord:
    _closed(payload, _TOP_LEVEL, "intake record")
    _require_fields(payload, _TOP_LEVEL, "intake record")
    if payload["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    candidate_id = payload["candidate_id"]
    if not isinstance(candidate_id, str) or not _CANDIDATE_ID.fullmatch(candidate_id):
        raise ValueError("candidate_id is invalid")
    candidate_type = _enum(payload["candidate_type"], {"skill", "plugin"}, "candidate_type")
    requested_at = _date(payload["requested_at"], "requested_at")
    repository, issue_number = _validate_source_issue(payload)
    wm_state, wm_warnings = _validate_work_management(payload)
    provenance_type, provenance_state = _validate_provenance(payload)
    license_state = _validate_license(payload)
    assessments = _validate_assessments(payload)
    adaptation_state = _single_state(
        payload, "adaptation", {"pending", "not_required", "required", "in_progress", "complete", "rejected"}
    )
    evaluation_state = _single_state(
        payload, "evaluation", {"blocked", "ready", "in_progress", "complete", "deferred"}
    )
    human_review_state = _single_state(
        payload, "human_review", {"pending", "complete", "not_required"}
    )
    disposition = _enum(payload["disposition"], _DISPOSITIONS, "disposition")
    targets = _validate_targets(payload, candidate_type)
    _validate_admit_gate(
        disposition,
        provenance_state,
        license_state,
        assessments,
        adaptation_state,
        evaluation_state,
        human_review_state,
    )
    next_action = _next_action(
        provenance_type,
        provenance_state,
        license_state,
        assessments,
        adaptation_state,
        evaluation_state,
        human_review_state,
        disposition,
    )
    return IntakeRecord(
        candidate_id=candidate_id,
        candidate_type=candidate_type,
        requested_at=requested_at,
        source_repository=repository,
        source_issue_number=issue_number,
        work_management_state=wm_state,
        provenance_type=provenance_type,
        provenance_state=provenance_state,
        license_state=license_state,
        adaptation_state=adaptation_state,
        evaluation_state=evaluation_state,
        human_review_state=human_review_state,
        disposition=disposition,
        next_action=next_action,
        assessment_states=assessments,
        targets=targets,
        source_path=source_path,
        warnings=wm_warnings,
    )


def _read_record_json(path: Path) -> Mapping[str, object]:
    with path.open("rb") as handle:
        actual = opened_path(handle)
        expected = Path(os.path.abspath(path))
        if os.path.normcase(str(actual)) != os.path.normcase(str(expected)):
            raise ValueError(f"opened intake record escaped validated intake path: {actual}")
        initial = os.fstat(handle.fileno())
        raw = handle.read()
        final = os.fstat(handle.fileno())
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
        if identity(initial) != identity(final):
            raise ValueError("intake record changed while being read")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("intake record root must be an object")
    return payload


def load_intake_queue(repo_root: Path | str) -> IntakeSnapshot:
    root = Path(repo_root).expanduser().resolve() / "intake" / "candidates"
    if not root.exists():
        return IntakeSnapshot(records=(), status="not_available", source=str(root))
    if not root.is_dir():
        return IntakeSnapshot(
            records=(), status="invalid", source=str(root),
            warnings=(f"intake queue root is not a directory: {root}",),
        )
    records: list[IntakeRecord] = []
    warnings: list[str] = []
    for path in sorted(root.glob("*/intake-record.json"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(root).as_posix()
        try:
            payload = _read_record_json(path)
            record = validate_intake_record(payload, source_path=str(path))
            if path.parent.name != record.candidate_id:
                raise ValueError("candidate_id must match intake directory name")
            records.append(record)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            warnings.append(f"{relative}: {exc}")
    records.sort(key=lambda item: (item.candidate_id.casefold(), item.candidate_id))
    status = "invalid" if warnings else "observed"
    return IntakeSnapshot(
        records=tuple(records),
        status=status,
        source=str(root),
        warnings=tuple(warnings),
    )


def validate_intake_root(repo_root: Path | str) -> IntakeSnapshot:
    snapshot = load_intake_queue(repo_root)
    if snapshot.status == "not_available":
        raise ValueError("intake queue root is not available")
    if snapshot.status == "invalid":
        raise ValueError("intake queue is invalid: " + "; ".join(snapshot.warnings))
    return snapshot
