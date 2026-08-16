#!/usr/bin/env python3
"""Validate non-runtime plugin portfolio records.

This validator uses only the Python standard library and never executes,
installs, activates, or connects plugin content.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

PLUGIN_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REVISION_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PORTFOLIO_ROOT = Path("portfolio/plugins")
RECORD_NAME = "plugin-record.json"

PORTFOLIO_STATUSES = {
    "candidate", "assessed", "pilot_ready", "accepted",
    "deferred", "rejected", "suspended",
}
SOURCE_STATUSES = {"unverified", "handoff_pending", "verified", "stale", "unavailable"}
PROVENANCE_TYPES = {"import-isolate", "trusted-local", "host-managed"}
PLUGIN_KINDS = {"codex-plugin", "claude-plugin", "host-managed", "other"}
EVALUATION_STATUSES = {"not_started", "partial", "passed", "failed", "deferred", "stale"}
INSTALLATION_STATUSES = {"not_observed", "not_installed", "installed", "unavailable", "disabled"}
ACTIVATION_STATUSES = {"not_observed", "inactive", "active", "blocked"}
APP_ACCESS_STATUSES = {"not_observed", "unavailable", "not_connected", "connected", "authorized", "blocked"}
DEPENDENCY_KINDS = {"executable", "library", "mcp-server", "service", "app", "other"}

TOP_LEVEL_FIELDS = {
    "schema_version", "plugin_id", "display_name", "plugin_kind",
    "portfolio_status", "source_status", "source", "contents",
    "capabilities", "dependencies", "targets", "evaluation", "update",
    "rollback",
}
SOURCE_FIELDS = {
    "provenance_type", "owner", "canonical_uri", "version",
    "immutable_revision", "retrieved_at", "artifact_sha256",
    "license_or_terms", "handoff",
}
CONTENTS_FIELDS = {"skills", "apps", "app_templates", "mcp_or_tooling", "resources"}
CAPABILITY_FIELDS = {
    "filesystem_read", "filesystem_write", "process_execution",
    "network", "credentials", "external_mutation",
}
EVALUATION_FIELDS = {"status", "evidence", "baseline", "reviewer", "reviewed_at"}
UPDATE_FIELDS = {"last_accepted_revision", "last_checked_at", "delta_evidence"}
ROLLBACK_FIELDS = {"disable_method", "uninstall_method", "retained_evidence"}
DEPENDENCY_FIELDS = {"id", "kind", "version", "required"}
TARGET_FIELDS = {"target_id", "installation_status", "activation_status", "app_access"}
APP_ACCESS_FIELDS = {"app_id", "access_status"}
HANDOFF_FIELDS = {"case_id", "artifact", "artifact_sha256"}


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass
class ValidationReport:
    repo_root: Path
    errors: list[Issue] = field(default_factory=list)
    records: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, code: str, message: str, path: Path) -> None:
        try:
            display = path.resolve(strict=False).relative_to(
                self.repo_root.resolve(strict=False)
            ).as_posix()
        except (OSError, ValueError):
            display = str(path)
        self.errors.append(Issue(code, message, display))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "valid": self.ok,
            "record_count": len(self.records),
            "records": sorted(self.records),
            "errors": [issue.to_dict() for issue in self.errors],
        }


def _exact_object(
    value: Any,
    fields: set[str],
    report: ValidationReport,
    code: str,
    path: Path,
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        report.add(f"{code}_TYPE", "Expected a JSON object.", path)
        return None
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing:
        report.add(f"{code}_MISSING", f"Missing fields: {', '.join(missing)}.", path)
    if unknown:
        report.add(f"{code}_UNKNOWN", f"Unknown fields: {', '.join(unknown)}.", path)
    return value


def _is_date(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_safe_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip() or "\\" in value or "\x00" in value:
        return False
    if re.match(r"^[A-Za-z]:", value) or value.startswith(("/", "//")):
        return False
    return ".." not in PurePosixPath(value).parts


def _is_link_like(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except OSError:
        return False
    if path.is_symlink():
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)

def _string_list(
    value: Any,
    report: ValidationReport,
    code: str,
    path: Path,
    *,
    repository_paths: bool = False,
) -> None:
    if not isinstance(value, list):
        report.add(f"{code}_TYPE", "Expected an array.", path)
        return
    if len(value) != len(set(item for item in value if isinstance(item, str))):
        report.add(f"{code}_DUPLICATE", "Array values must be unique.", path)
    for item in value:
        if not isinstance(item, str) or not item.strip():
            report.add(f"{code}_ITEM", "Array values must be non-empty strings.", path)
            continue
        if len(item) > 500:
            report.add(f"{code}_ITEM", "Array string values must not exceed 500 characters.", path)
            continue
        if repository_paths and not _is_safe_path(item):
            report.add(f"{code}_PATH", f"Unsafe repository-relative path: {item!r}.", path)


def _nullable_string(
    value: Any,
    report: ValidationReport,
    code: str,
    path: Path,
    *,
    max_length: int | None = None,
) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        report.add(code, "Value must be null or a non-empty string.", path)
    elif isinstance(value, str) and max_length is not None and len(value) > max_length:
        report.add(code, f"Value exceeds maximum length {max_length}.", path)


def _enum(value: Any, allowed: set[str], report: ValidationReport, code: str, path: Path) -> None:
    if not isinstance(value, str) or value not in allowed:
        report.add(code, f"Expected one of: {', '.join(sorted(allowed))}.", path)


def _validate_source(value: Any, report: ValidationReport, path: Path) -> None:
    source = _exact_object(value, SOURCE_FIELDS, report, "SOURCE", path)
    if source is None:
        return
    _enum(source.get("provenance_type"), PROVENANCE_TYPES, report, "PROVENANCE_TYPE_INVALID", path)
    source_limits = {"owner": 200, "canonical_uri": 1000, "version": 200, "license_or_terms": 500}
    for name, max_length in source_limits.items():
        _nullable_string(
            source.get(name),
            report,
            f"SOURCE_{name.upper()}_INVALID",
            path,
            max_length=max_length,
        )
    revision = source.get("immutable_revision")
    if revision is not None and (
        not isinstance(revision, str) or not REVISION_RE.fullmatch(revision)
    ):
        report.add("SOURCE_REVISION_INVALID", "immutable_revision must be null or exact lowercase hex.", path)
    artifact_hash = source.get("artifact_sha256")
    if artifact_hash is not None and (
        not isinstance(artifact_hash, str) or not SHA256_RE.fullmatch(artifact_hash)
    ):
        report.add("SOURCE_DIGEST_INVALID", "artifact_sha256 must be null or lowercase SHA-256 hex.", path)
    retrieved_at = source.get("retrieved_at")
    if retrieved_at is not None and not _is_date(retrieved_at):
        report.add("SOURCE_DATE_INVALID", "retrieved_at must be null or an ISO date.", path)
    canonical_uri = source.get("canonical_uri")
    if isinstance(canonical_uri, str):
        uri_valid = bool(
            re.fullmatch(r"[A-Za-z][A-Za-z0-9+.-]*://\S+", canonical_uri)
        )
        if uri_valid:
            try:
                parsed = urlparse(canonical_uri)
                uri_valid = bool(parsed.scheme and parsed.netloc)
            except ValueError:
                uri_valid = False
        if not uri_valid:
            report.add("SOURCE_URI_INVALID", "canonical_uri must be an absolute URI without whitespace.", path)

    handoff = source.get("handoff")
    if handoff is not None:
        record = _exact_object(handoff, HANDOFF_FIELDS, report, "HANDOFF", path)
        if record is not None:
            if not isinstance(record.get("case_id"), str) or not re.fullmatch(
                r"[A-Za-z0-9._-]{1,160}", record.get("case_id", "")
            ):
                report.add("HANDOFF_CASE_ID_INVALID", "handoff.case_id is invalid.", path)
            if not isinstance(record.get("artifact"), str) or not re.fullmatch(
                r"[A-Za-z0-9._-]{1,200}", record.get("artifact", "")
            ):
                report.add("HANDOFF_ARTIFACT_INVALID", "handoff.artifact is invalid.", path)
            handoff_hash = record.get("artifact_sha256")
            if not isinstance(handoff_hash, str) or not SHA256_RE.fullmatch(handoff_hash):
                report.add("HANDOFF_DIGEST_INVALID", "handoff.artifact_sha256 must be lowercase SHA-256 hex.", path)


def _validate_contents(value: Any, report: ValidationReport, path: Path) -> None:
    contents = _exact_object(value, CONTENTS_FIELDS, report, "CONTENTS", path)
    if contents is None:
        return
    for name in sorted(CONTENTS_FIELDS):
        _string_list(contents.get(name), report, f"CONTENTS_{name.upper()}", path)


def _validate_capabilities(value: Any, report: ValidationReport, path: Path) -> None:
    capabilities = _exact_object(value, CAPABILITY_FIELDS, report, "CAPABILITIES", path)
    if capabilities is None:
        return
    _string_list(capabilities.get("filesystem_read"), report, "FILESYSTEM_READ", path, repository_paths=True)
    _string_list(capabilities.get("filesystem_write"), report, "FILESYSTEM_WRITE", path, repository_paths=True)
    for name in ("process_execution", "network", "credentials", "external_mutation"):
        if not isinstance(capabilities.get(name), bool):
            report.add("CAPABILITY_TYPE", f"capabilities.{name} must be boolean.", path)


def _validate_dependencies(value: Any, report: ValidationReport, path: Path) -> None:
    if not isinstance(value, list):
        report.add("DEPENDENCIES_TYPE", "dependencies must be an array.", path)
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        dependency = _exact_object(item, DEPENDENCY_FIELDS, report, "DEPENDENCY", path)
        if dependency is None:
            continue
        dependency_id = dependency.get("id")
        if not isinstance(dependency_id, str) or not dependency_id.strip() or len(dependency_id) > 300:
            report.add("DEPENDENCY_ID_INVALID", f"dependencies[{index}].id must be non-empty.", path)
        elif dependency_id in seen:
            report.add("DEPENDENCY_DUPLICATE", f"Duplicate dependency id: {dependency_id}.", path)
        else:
            seen.add(dependency_id)
        _enum(dependency.get("kind"), DEPENDENCY_KINDS, report, "DEPENDENCY_KIND_INVALID", path)
        _nullable_string(dependency.get("version"), report, "DEPENDENCY_VERSION_INVALID", path, max_length=200)
        if not isinstance(dependency.get("required"), bool):
            report.add("DEPENDENCY_REQUIRED_TYPE", "dependency.required must be boolean.", path)


def _validate_targets(value: Any, report: ValidationReport, path: Path) -> None:
    if not isinstance(value, list):
        report.add("TARGETS_TYPE", "targets must be an array.", path)
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        target = _exact_object(item, TARGET_FIELDS, report, "TARGET", path)
        if target is None:
            continue
        target_id = target.get("target_id")
        if not isinstance(target_id, str) or not target_id.strip() or len(target_id) > 200:
            report.add("TARGET_ID_INVALID", f"targets[{index}].target_id must be non-empty.", path)
        elif target_id in seen:
            report.add("TARGET_DUPLICATE", f"Duplicate target id: {target_id}.", path)
        else:
            seen.add(target_id)
        _enum(target.get("installation_status"), INSTALLATION_STATUSES, report, "INSTALLATION_STATUS_INVALID", path)
        _enum(target.get("activation_status"), ACTIVATION_STATUSES, report, "ACTIVATION_STATUS_INVALID", path)
        app_access = target.get("app_access")
        if not isinstance(app_access, list):
            report.add("APP_ACCESS_TYPE", "target.app_access must be an array.", path)
            continue
        app_seen: set[str] = set()
        for app in app_access:
            access = _exact_object(app, APP_ACCESS_FIELDS, report, "APP_ACCESS", path)
            if access is None:
                continue
            app_id = access.get("app_id")
            if not isinstance(app_id, str) or not app_id.strip() or len(app_id) > 300:
                report.add("APP_ID_INVALID", "app_access.app_id must be non-empty.", path)
            elif app_id in app_seen:
                report.add("APP_ACCESS_DUPLICATE", f"Duplicate app id: {app_id}.", path)
            else:
                app_seen.add(app_id)
            _enum(access.get("access_status"), APP_ACCESS_STATUSES, report, "APP_ACCESS_STATUS_INVALID", path)


def _validate_evaluation(value: Any, report: ValidationReport, path: Path) -> None:
    evaluation = _exact_object(value, EVALUATION_FIELDS, report, "EVALUATION", path)
    if evaluation is None:
        return
    _enum(evaluation.get("status"), EVALUATION_STATUSES, report, "EVALUATION_STATUS_INVALID", path)
    _string_list(evaluation.get("evidence"), report, "EVALUATION_EVIDENCE", path, repository_paths=True)
    _nullable_string(evaluation.get("baseline"), report, "EVALUATION_BASELINE_INVALID", path, max_length=500)
    _nullable_string(evaluation.get("reviewer"), report, "EVALUATION_REVIEWER_INVALID", path, max_length=200)
    reviewed_at = evaluation.get("reviewed_at")
    if reviewed_at is not None and not _is_date(reviewed_at):
        report.add("EVALUATION_DATE_INVALID", "evaluation.reviewed_at must be null or an ISO date.", path)


def _validate_update(value: Any, report: ValidationReport, path: Path) -> None:
    update = _exact_object(value, UPDATE_FIELDS, report, "UPDATE", path)
    if update is None:
        return
    revision = update.get("last_accepted_revision")
    if revision is not None and (
        not isinstance(revision, str) or not REVISION_RE.fullmatch(revision)
    ):
        report.add("UPDATE_REVISION_INVALID", "last_accepted_revision must be null or exact lowercase hex.", path)
    checked_at = update.get("last_checked_at")
    if checked_at is not None and not _is_date(checked_at):
        report.add("UPDATE_DATE_INVALID", "last_checked_at must be null or an ISO date.", path)
    delta = update.get("delta_evidence")
    if delta is not None and (not _is_safe_path(delta) or len(delta) > 500):
        report.add("UPDATE_DELTA_PATH_INVALID", "delta_evidence must be a safe repository-relative path or null.", path)


def _validate_rollback(value: Any, report: ValidationReport, path: Path) -> None:
    rollback = _exact_object(value, ROLLBACK_FIELDS, report, "ROLLBACK", path)
    if rollback is None:
        return
    _nullable_string(rollback.get("disable_method"), report, "ROLLBACK_DISABLE_INVALID", path, max_length=1000)
    _nullable_string(rollback.get("uninstall_method"), report, "ROLLBACK_UNINSTALL_INVALID", path, max_length=1000)
    _string_list(rollback.get("retained_evidence"), report, "ROLLBACK_EVIDENCE", path, repository_paths=True)


def _validate_evidence_path(value: str, report: ValidationReport, path: Path) -> None:
    candidate = report.repo_root.joinpath(*PurePosixPath(value).parts)
    current = report.repo_root
    for part in PurePosixPath(value).parts:
        current = current / part
        if _is_link_like(current):
            report.add(
                "EVIDENCE_LINKED",
                "repository evidence paths must not traverse symlinks or reparse points.",
                current,
            )
            return
        if not current.exists():
            report.add("EVIDENCE_MISSING", f"Referenced repository evidence does not exist: {value}.", path)
            return
    try:
        resolved_candidate = candidate.resolve(strict=True)
        resolved_candidate.relative_to(report.repo_root)
    except (OSError, ValueError):
        report.add("EVIDENCE_OUTSIDE_REPOSITORY", "repository evidence must resolve inside the repository root.", path)
        return
    if resolved_candidate == path.resolve(strict=False):
        report.add("EVIDENCE_SELF_REFERENCE", "plugin-record.json cannot serve as its own evidence.", path)
        return
    if not resolved_candidate.is_file():
        report.add("EVIDENCE_NOT_FILE", f"Repository evidence must resolve to a regular file: {value}.", path)


def _validate_evidence_references(
    record: dict[str, Any], report: ValidationReport, path: Path
) -> None:
    values: list[str] = []
    evaluation = record.get("evaluation")
    if isinstance(evaluation, dict) and isinstance(evaluation.get("evidence"), list):
        values.extend(item for item in evaluation["evidence"] if isinstance(item, str) and _is_safe_path(item))
    rollback = record.get("rollback")
    if isinstance(rollback, dict) and isinstance(rollback.get("retained_evidence"), list):
        values.extend(item for item in rollback["retained_evidence"] if isinstance(item, str) and _is_safe_path(item))
    update = record.get("update")
    if isinstance(update, dict):
        delta = update.get("delta_evidence")
        if isinstance(delta, str) and _is_safe_path(delta):
            values.append(delta)
    for value in sorted(set(values)):
        _validate_evidence_path(value, report, path)

def _validate_cross_field_gates(
    record: dict[str, Any], report: ValidationReport, path: Path
) -> None:
    source = record.get("source") if isinstance(record.get("source"), dict) else {}
    provenance = source.get("provenance_type")
    handoff = source.get("handoff")
    artifact_sha256 = source.get("artifact_sha256")

    if provenance == "import-isolate":
        if handoff is None and record.get("source_status") == "verified":
            report.add("HANDOFF_REQUIRED", "import-isolate provenance requires a finalized handoff.", path)
        elif isinstance(handoff, dict):
            handoff_sha256 = handoff.get("artifact_sha256")
            if (
                isinstance(artifact_sha256, str)
                and isinstance(handoff_sha256, str)
                and artifact_sha256 != handoff_sha256
            ):
                report.add(
                    "HANDOFF_DIGEST_MISMATCH",
                    "source.artifact_sha256 must match the finalized handoff artifact digest.",
                    path,
                )
    elif provenance in {"trusted-local", "host-managed"} and handoff is not None:
        report.add(
            "HANDOFF_UNEXPECTED",
            f"{provenance} provenance must not claim an import-isolate handoff.",
            path,
        )

    if record.get("source_status") == "verified":
        required_identity = (
            "owner", "canonical_uri", "version", "immutable_revision",
            "retrieved_at", "artifact_sha256", "license_or_terms",
        )
        if any(
            source.get(name) is None
            or (isinstance(source.get(name), str) and not source.get(name).strip())
            for name in required_identity
        ):
            report.add(
                "VERIFIED_SOURCE_INCOMPLETE",
                "verified source_status requires complete immutable source identity and license/terms evidence.",
                path,
            )

    evaluation = record.get("evaluation") if isinstance(record.get("evaluation"), dict) else {}
    update = record.get("update") if isinstance(record.get("update"), dict) else {}
    rollback = record.get("rollback") if isinstance(record.get("rollback"), dict) else {}
    if record.get("portfolio_status") == "accepted":
        if record.get("source_status") != "verified":
            report.add("ACCEPTED_SOURCE_REQUIRED", "accepted plugins require verified source_status.", path)
        if evaluation.get("status") != "passed" or not evaluation.get("evidence"):
            report.add(
                "ACCEPTED_EVALUATION_REQUIRED",
                "accepted plugins require passed evaluation with repository evidence.",
                path,
            )
        if not evaluation.get("reviewer") or not evaluation.get("reviewed_at"):
            report.add(
                "ACCEPTED_REVIEW_REQUIRED",
                "accepted plugins require an explicit reviewer and review date.",
                path,
            )
        if (
            not source.get("immutable_revision")
            or update.get("last_accepted_revision") != source.get("immutable_revision")
        ):
            report.add(
                "ACCEPTED_UPDATE_BASELINE_REQUIRED",
                "accepted plugins require last_accepted_revision matching the verified source revision.",
                path,
            )
        if not rollback.get("disable_method") and not rollback.get("uninstall_method"):
            report.add(
                "ACCEPTED_ROLLBACK_REQUIRED",
                "accepted plugins require a disable or uninstall rollback method.",
                path,
            )

    targets = record.get("targets")
    if isinstance(targets, list):
        for target in targets:
            if not isinstance(target, dict):
                continue
            if (
                target.get("activation_status") == "active"
                and target.get("installation_status") != "installed"
            ):
                report.add(
                    "TARGET_ACTIVE_NOT_INSTALLED",
                    "an active target must also be recorded as installed.",
                    path,
                )

def validate_record(value: Any, record_path: Path, report: ValidationReport) -> None:
    record = _exact_object(value, TOP_LEVEL_FIELDS, report, "RECORD", record_path)
    if record is None:
        return
    if type(record.get("schema_version")) is not int or record.get("schema_version") != 1:
        report.add("SCHEMA_VERSION_INVALID", "schema_version must be 1.", record_path)
    plugin_id = record.get("plugin_id")
    if not isinstance(plugin_id, str) or len(plugin_id) > 100 or not PLUGIN_ID_RE.fullmatch(plugin_id):
        report.add("PLUGIN_ID_INVALID", "plugin_id must use lowercase alphanumeric hyphen notation.", record_path)
    elif record_path.parent.name != plugin_id:
        report.add("PLUGIN_ID_MISMATCH", "plugin_id must match the containing directory name.", record_path)
    display_name = record.get("display_name")
    if not isinstance(display_name, str) or not display_name.strip() or len(display_name) > 200:
        report.add("DISPLAY_NAME_INVALID", "display_name must be non-empty.", record_path)
    _enum(record.get("plugin_kind"), PLUGIN_KINDS, report, "PLUGIN_KIND_INVALID", record_path)
    _enum(record.get("portfolio_status"), PORTFOLIO_STATUSES, report, "PORTFOLIO_STATUS_INVALID", record_path)
    _enum(record.get("source_status"), SOURCE_STATUSES, report, "SOURCE_STATUS_INVALID", record_path)
    _validate_source(record.get("source"), report, record_path)
    _validate_contents(record.get("contents"), report, record_path)
    _validate_capabilities(record.get("capabilities"), report, record_path)
    _validate_dependencies(record.get("dependencies"), report, record_path)
    _validate_targets(record.get("targets"), report, record_path)
    _validate_evaluation(record.get("evaluation"), report, record_path)
    _validate_update(record.get("update"), report, record_path)
    _validate_rollback(record.get("rollback"), report, record_path)
    _validate_evidence_references(record, report, record_path)
    _validate_cross_field_gates(record, report, record_path)


def validate_repository(repo_root: Path) -> ValidationReport:
    root = repo_root.resolve()
    report = ValidationReport(root)
    portfolio_parent = root / "portfolio"
    portfolio_root = root / PORTFOLIO_ROOT
    for component in (portfolio_parent, portfolio_root):
        if component.exists() and _is_link_like(component):
            report.add(
                "PORTFOLIO_PATH_LINKED",
                "portfolio path components must be real repository directories, not symlinks or junctions.",
                component,
            )
            return report
    if not portfolio_root.is_dir():
        report.add(
            "PORTFOLIO_ROOT_MISSING",
            "portfolio/plugins must exist as the non-runtime plugin record root.",
            portfolio_root,
        )
        return report
    try:
        portfolio_root.resolve(strict=True).relative_to(root)
    except (OSError, ValueError):
        report.add(
            "PORTFOLIO_OUTSIDE_REPOSITORY",
            "portfolio/plugins must resolve inside the repository root.",
            portfolio_root,
        )
        return report

    plugin_dirs: list[Path] = []
    try:
        root_entries = sorted(portfolio_root.iterdir())
    except OSError as exc:
        report.add(
            "PORTFOLIO_ROOT_UNREADABLE",
            f"Unable to enumerate portfolio/plugins safely: {exc}",
            portfolio_root,
        )
        return report
    for entry in root_entries:
        if _is_link_like(entry):
            report.add(
                "PLUGIN_DIRECTORY_LINKED",
                "linked entries are not allowed directly under portfolio/plugins.",
                entry,
            )
            continue
        if entry.is_dir():
            plugin_dirs.append(entry)
        elif entry.name == RECORD_NAME:
            report.add(
                "PLUGIN_RECORD_MISPLACED",
                "plugin-record.json must be inside portfolio/plugins/<plugin-id>/.",
                entry,
            )

    for plugin_dir in plugin_dirs:
        record_path = plugin_dir / RECORD_NAME
        pending = [plugin_dir]
        while pending:
            current = pending.pop()
            try:
                entries = sorted(current.iterdir())
            except OSError as exc:
                report.add(
                    "PLUGIN_DIRECTORY_UNREADABLE",
                    f"Unable to inspect plugin directory safely: {exc}",
                    current,
                )
                continue
            for entry in entries:
                if entry == record_path:
                    continue
                if _is_link_like(entry):
                    report.add(
                        "PLUGIN_PATH_LINKED",
                        "linked or reparse-point paths are not allowed inside plugin record directories.",
                        entry,
                    )
                    continue
                if entry.is_dir():
                    pending.append(entry)
                elif entry.name == RECORD_NAME:
                    report.add(
                        "PLUGIN_RECORD_MISPLACED",
                        "plugin-record.json must be exactly one directory below portfolio/plugins.",
                        entry,
                    )
        if _is_link_like(record_path):
            report.add(
                "PLUGIN_RECORD_LINKED",
                "plugin-record.json must be a real repository file, not a symlink or junction.",
                record_path,
            )
            continue
        if not record_path.is_file():
            report.add(
                "PLUGIN_RECORD_MISSING",
                "every plugin directory must contain plugin-record.json.",
                plugin_dir,
            )
            continue
        report.records.append(plugin_dir.name)
        try:
            value = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            report.add("RECORD_INVALID_JSON", str(exc), record_path)
            continue
        validate_record(value, record_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate non-runtime plugin portfolio records.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="Validate every plugin record under portfolio/plugins.")
    validate.add_argument("--repo", type=Path, default=Path.cwd())
    validate.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = validate_repository(args.repo)
    payload = report.to_dict()
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif report.ok:
        print(f"Plugin portfolio: PASS ({len(report.records)} records)")
    else:
        for issue in report.errors:
            print(f"ERROR {issue.code}: {issue.message} [{issue.path}]", file=sys.stderr)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
