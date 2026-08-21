#!/usr/bin/env python3
"""Validate and project authoritative KIS skill-delivery telemetry."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
DELIVERY_PATHS = {"kis_native", "mcp_resource"}
COUNT_FIELDS = (
    "loaded_count", "resource_read_count", "applied_count", "completed_count",
    "failed_count", "error_count", "digest_verified_count", "digest_failed_count",
)
GROUP_KEYS = {"skill_id", "content_sha256", "project_id", "delivery_path", *COUNT_FIELDS}
COMPARISON_KEYS = {"skill_id", "content_sha256", "project_id", "comparable", "reason"}
REPORT_KEYS = {
    "schema_version", "groups", "comparisons", "event_count",
    "catalogue_exposure_count", "truncated",
}
_UNSET_PROJECT = object()

class DeliveryTelemetryError(ValueError):
    """Raised when KIS delivery telemetry is malformed or internally inconsistent."""


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise DeliveryTelemetryError(message)


def _exact_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DeliveryTelemetryError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        unknown = sorted(actual - keys)
        raise DeliveryTelemetryError(
            f"{label} keys mismatch; missing={missing}, unknown={unknown}"
        )
    return value


def _identity_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or ID_RE.fullmatch(value) is None:
        raise DeliveryTelemetryError(f"{label} is invalid")
    return value


def _project_id(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _identity_text(value, label)

def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise DeliveryTelemetryError(f"{label} must be lowercase SHA-256 hex")
    return value


def _count(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DeliveryTelemetryError(f"{label} must be a non-negative integer")
    return value


def _identity(value: dict[str, Any]) -> tuple[str, str, str | None]:
    return value["skill_id"], value["content_sha256"], value["project_id"]


def _normalize_group(raw: Any) -> dict[str, Any]:
    value = _exact_object(raw, GROUP_KEYS, "delivery telemetry group")
    normalized = {
        "skill_id": _identity_text(value["skill_id"], "group.skill_id"),
        "content_sha256": _sha256(value["content_sha256"], "group.content_sha256"),
        "project_id": _project_id(value["project_id"], "group.project_id"),
    }
    path = value["delivery_path"]
    if path not in DELIVERY_PATHS:
        raise DeliveryTelemetryError("group.delivery_path is unsupported")
    normalized["delivery_path"] = path
    for field in COUNT_FIELDS:
        normalized[field] = _count(value[field], f"group.{field}")
    return normalized


def _normalize_comparison(raw: Any) -> dict[str, Any]:
    value = _exact_object(raw, COMPARISON_KEYS, "delivery telemetry comparison")
    comparable = value["comparable"]
    if not isinstance(comparable, bool):
        raise DeliveryTelemetryError("comparison.comparable must be boolean")
    reason = value["reason"]
    if not isinstance(reason, str) or not reason.strip():
        raise DeliveryTelemetryError("comparison.reason must be a non-empty string")
    return {
        "skill_id": _identity_text(value["skill_id"], "comparison.skill_id"),
        "content_sha256": _sha256(
            value["content_sha256"], "comparison.content_sha256"
        ),
        "project_id": _project_id(value["project_id"], "comparison.project_id"),
        "comparable": comparable,
        "reason": reason,
    }


def _expected_comparison(paths: set[str]) -> tuple[bool, str]:
    if paths == DELIVERY_PATHS:
        return True, "matched_content_sha256"
    if paths == {"kis_native"}:
        return False, "missing_mcp_resource"
    if paths == {"mcp_resource"}:
        raise DeliveryTelemetryError("mcp_resource identity lacks required kis_native group")
    raise DeliveryTelemetryError(f"invalid delivery-path set: {sorted(paths)}")


def validate_report(raw: Any) -> dict[str, Any]:
    report = _exact_object(raw, REPORT_KEYS, "delivery telemetry report")
    if report["schema_version"] != 1:
        raise DeliveryTelemetryError("delivery telemetry report schema_version must be 1")
    event_count = _count(report["event_count"], "report.event_count")
    exposure_count = _count(
        report["catalogue_exposure_count"], "report.catalogue_exposure_count"
    )
    if not isinstance(report["truncated"], bool):
        raise DeliveryTelemetryError("report.truncated must be boolean")
    if not isinstance(report["groups"], list):
        raise DeliveryTelemetryError("report.groups must be a list")
    if not isinstance(report["comparisons"], list):
        raise DeliveryTelemetryError("report.comparisons must be a list")

    groups = [_normalize_group(group) for group in report["groups"]]
    comparisons = [
        _normalize_comparison(comparison) for comparison in report["comparisons"]
    ]
    paths_by_identity: dict[tuple[str, str, str | None], set[str]] = defaultdict(set)
    groups_by_identity_path: dict[
        tuple[str, str, str | None], dict[str, dict[str, Any]]
    ] = defaultdict(dict)
    for group in groups:
        identity = _identity(group)
        path = group["delivery_path"]
        if path in paths_by_identity[identity]:
            raise DeliveryTelemetryError(
                f"duplicate delivery-path group for {identity}: {path}"
            )
        paths_by_identity[identity].add(path)
        groups_by_identity_path[identity][path] = group

    comparisons_by_identity: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for comparison in comparisons:
        identity = _identity(comparison)
        if identity in comparisons_by_identity:
            raise DeliveryTelemetryError(f"duplicate comparison for {identity}")
        comparisons_by_identity[identity] = comparison
    if set(comparisons_by_identity) != set(paths_by_identity):
        missing = sorted(set(paths_by_identity) - set(comparisons_by_identity), key=str)
        unknown = sorted(set(comparisons_by_identity) - set(paths_by_identity), key=str)
        raise DeliveryTelemetryError(
            f"comparison identities mismatch; missing={missing}, unknown={unknown}"
        )

    for identity, paths in paths_by_identity.items():
        expected_comparable, expected_reason = _expected_comparison(paths)
        supplied = comparisons_by_identity[identity]
        if supplied["comparable"] is not expected_comparable or supplied["reason"] != expected_reason:
            raise DeliveryTelemetryError(
                f"comparison disagrees with delivery groups for {identity}"
            )
        if expected_comparable:
            mcp_group = groups_by_identity_path[identity]["mcp_resource"]
            mcp_operations = mcp_group["loaded_count"] + mcp_group["resource_read_count"]
            digest_results = (
                mcp_group["digest_verified_count"] + mcp_group["digest_failed_count"]
            )
            if mcp_operations <= 0 or digest_results != mcp_operations:
                raise DeliveryTelemetryError(
                    f"comparable MCP delivery lacks complete digest coverage for {identity}"
                )
            if mcp_group["digest_failed_count"] != 0:
                raise DeliveryTelemetryError(
                    f"comparable MCP delivery has digest verification failures for {identity}"
                )

    return {
        "schema_version": 1,
        "groups": groups,
        "comparisons": comparisons,
        "event_count": event_count,
        "catalogue_exposure_count": exposure_count,
        "truncated": report["truncated"],
    }


def _matches(
    identity: tuple[str, str, str | None],
    *,
    skill_id: str | None,
    project_filter: object,
    content_sha256: str | None,
) -> bool:
    skill, digest, project = identity
    return (
        (skill_id is None or skill == skill_id)
        and (project_filter is _UNSET_PROJECT or project == project_filter)
        and (content_sha256 is None or digest == content_sha256)
    )


def project_report(
    raw: Any,
    *,
    skill_id: str | None = None,
    project_id: str | None | object = _UNSET_PROJECT,
    content_sha256: str | None = None,
) -> dict[str, Any]:
    if skill_id is not None:
        skill_id = _identity_text(skill_id, "filter.skill_id")
    if project_id is not _UNSET_PROJECT and project_id is not None:
        project_id = _identity_text(project_id, "filter.project_id")
    if content_sha256 is not None:
        content_sha256 = _sha256(content_sha256, "filter.content_sha256")
    report = validate_report(raw)

    selected_comparisons = [
        item for item in report["comparisons"]
        if _matches(
            _identity(item),
            skill_id=skill_id,
            project_filter=project_id,
            content_sha256=content_sha256,
        )
    ]
    selected_identities = {_identity(item) for item in selected_comparisons}
    selected_groups = [
        item for item in report["groups"] if _identity(item) in selected_identities
    ]
    path_totals: dict[str, dict[str, int]] = {
        path: {field: 0 for field in COUNT_FIELDS} for path in sorted(DELIVERY_PATHS)
    }
    path_group_counts = {path: 0 for path in sorted(DELIVERY_PATHS)}
    for group in selected_groups:
        path = group["delivery_path"]
        path_group_counts[path] += 1
        for field in COUNT_FIELDS:
            path_totals[path][field] += group[field]

    return {
        "schema_version": 1,
        "source_schema_version": report["schema_version"],
        "behavioral_effectiveness_evidence": False,
        "filters": {
            "skill_id": skill_id,
            "project": (
                {"mode": "all"}
                if project_id is _UNSET_PROJECT
                else {"mode": "exact", "value": project_id}
            ),
            "content_sha256": content_sha256,
        },
        "source_event_count": report["event_count"],
        "source_catalogue_exposure_count": report["catalogue_exposure_count"],
        "source_truncated": report["truncated"],
        "summary": {
            "identity_count": len(selected_comparisons),
            "comparable_identity_count": sum(
                1 for item in selected_comparisons if item["comparable"]
            ),
            "metric_comparison_eligible": not report["truncated"],
            "metric_comparison_status": (
                "complete" if not report["truncated"] else "truncated"
            ),
            "path_group_counts": path_group_counts,
            "path_totals": path_totals,
        },
        "groups": selected_groups,
        "comparisons": selected_comparisons,
    }


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DeliveryTelemetryError(f"invalid JSON at {path}: {exc}") from exc


def _clear_output(path: Path | None) -> None:
    if path is None:
        return
    try:
        if path.exists() or path.is_symlink():
            path.unlink()
    except OSError as exc:
        raise DeliveryTelemetryError(f"cannot clear stale output {path}: {exc}") from exc


def _write_atomic(path: Path, rendered: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            handle.write(rendered)
            temp_path = Path(handle.name)
        temp_path.replace(path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def _extract_path_arg(argv: Sequence[str], name: str) -> Path | None:
    value: Path | None = None
    prefix = f"{name}="
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--":
            break
        if token.startswith(prefix):
            value = Path(token[len(prefix):])
        elif token == name:
            if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
                value = None
            else:
                value = Path(argv[index + 1])
                index += 1
        index += 1
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(
        description="Validate and project KIS native-vs-MCP skill telemetry.",
        allow_abbrev=False,
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skill")
    project = parser.add_mutually_exclusive_group()
    project.add_argument("--project")
    project.add_argument(
        "--null-project", action="store_true",
        help="Select only telemetry whose project_id is null.",
    )
    parser.add_argument("--content-sha256")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    try:
        io_input = _extract_path_arg(raw_args, "--input")
        io_output = _extract_path_arg(raw_args, "--output")
        if io_output is not None and io_input is not None:
            same_file = io_input.resolve() == io_output.resolve()
            if not same_file and io_output.exists():
                try:
                    same_file = io_input.samefile(io_output)
                except OSError:
                    same_file = False
            if same_file:
                raise DeliveryTelemetryError("input and output paths must differ")
        _clear_output(io_output)
        args = build_parser().parse_args(raw_args)
        project_filter: str | None | object = _UNSET_PROJECT
        if args.null_project:
            project_filter = None
        elif args.project is not None:
            project_filter = args.project
        projection = project_report(
            _load_json(args.input),
            skill_id=args.skill,
            project_id=project_filter,
            content_sha256=args.content_sha256,
        )
        rendered = json.dumps(projection, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            print(rendered, end="")
        else:
            _write_atomic(args.output, rendered)
    except (DeliveryTelemetryError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
