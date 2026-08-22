from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .catalog import discover_catalog
from .compliance import load_compliance_summary
from .intake import load_intake_queue
from .models import DashboardReport, PluginReportRow, RepoEvidence, SkillReportRow, TelemetryEvidence
from .plugins import load_plugin_portfolio
from .repo import collect_repository_evidence
from .telemetry import load_telemetry_json, load_telemetry_sqlite

_EVALUATED_STATES = {"admit", "revise", "defer", "suspend"}


def _plugin_value_counts(
    plugins: tuple[PluginReportRow, ...], field: str
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for plugin in plugins:
        value = plugin.record.get(field)
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _plugin_target_counts(
    plugins: tuple[PluginReportRow, ...], field: str
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for plugin in plugins:
        for target in plugin.target_observations:
            target_id = target.get("target_id")
            state = target.get(field)
            if not isinstance(target_id, str) or not isinstance(state, str):
                continue
            target_counts = counts.setdefault(target_id, {})
            target_counts[state] = target_counts.get(state, 0) + 1
    return {
        target_id: dict(sorted(states.items()))
        for target_id, states in sorted(counts.items())
    }


def _default_telemetry_path(catalog_roots: list[Path | str]) -> Path | None:
    if not catalog_roots:
        return None
    root = Path(catalog_roots[0]).expanduser().resolve()
    if len(root.parents) < 2:
        return None
    projects_root = root.parent.parent
    return projects_root / ".kis-mcp" / "telemetry" / "skills.sqlite3"


def build_report(
    catalog_roots: Iterable[Path | str],
    *,
    repo_root: Path | str,
    telemetry_db: Path | str | None = None,
    telemetry_json: Path | str | None = None,
) -> DashboardReport:
    roots = list(catalog_roots)
    if telemetry_db is not None and telemetry_json is not None:
        raise ValueError("telemetry_db and telemetry_json are mutually exclusive")
    inventory = discover_catalog(roots)
    repo_path = Path(repo_root).expanduser().resolve()
    repository = collect_repository_evidence(repo_path, inventory.entries)
    intake = load_intake_queue(repo_path)
    plugins = load_plugin_portfolio(repo_path)
    if telemetry_json is not None:
        telemetry = load_telemetry_json(telemetry_json)
    else:
        selected_db = Path(telemetry_db) if telemetry_db is not None else _default_telemetry_path(roots)
        if selected_db is None:
            from .models import TelemetrySnapshot

            telemetry = TelemetrySnapshot(
                groups=(),
                status="not_available",
                source=None,
                warnings=("KIS telemetry location could not be inferred",),
            )
        else:
            telemetry = load_telemetry_sqlite(selected_db)
    by_identity = telemetry.by_identity
    rows: list[SkillReportRow] = []
    for entry in inventory.entries:
        repo_evidence = repository.get(entry.name, RepoEvidence(skill_id=entry.name))
        current = (
            by_identity.get((entry.name, entry.content_sha256))
            if entry.content_sha256 is not None
            else None
        )
        row_warnings = [*entry.warnings, *repo_evidence.warnings]
        version_mismatch = current is None and any(
            group.skill_id == entry.name for group in telemetry.groups
        )
        if version_mismatch:
            row_warnings.append("telemetry exists only for other content hash version(s)")
        if current is not None:
            telemetry_status = (
                "observed_incomplete" if telemetry.status == "truncated" else "observed"
            )
        elif telemetry.status == "truncated":
            telemetry_status = "not_observable_due_to_truncation"
        elif telemetry.status in {"not_available", "invalid"}:
            telemetry_status = telemetry.status
        elif version_mismatch:
            telemetry_status = "hash_version_not_observed"
        else:
            telemetry_status = "not_observed"
        rows.append(
            SkillReportRow(
                catalog=entry,
                repository=repo_evidence,
                telemetry=current,
                telemetry_status=telemetry_status,
                warnings=tuple(row_warnings),
            )
        )
    total = len(rows)
    active = sum(1 for row in rows if row.catalog.status == "active")
    evaluated = sum(
        1 for row in rows if row.repository.evaluation_status in _EVALUATED_STATES
    )
    warnings = list(inventory.warnings)
    if not repo_path.is_dir():
        warnings.append(f"repository evidence unavailable: {repo_path}")
    warnings.extend(telemetry.warnings)
    warnings.extend(intake.warnings)
    warnings.extend(plugins.warnings)
    plugin_portfolio_counts = _plugin_value_counts(plugins.records, "portfolio_status")
    plugin_source_counts = _plugin_value_counts(plugins.records, "source_status")
    plugin_evaluation_counts: dict[str, int] = {}
    for plugin in plugins.records:
        evaluation = plugin.record.get("evaluation")
        if isinstance(evaluation, dict):
            status = evaluation.get("status")
            if isinstance(status, str):
                plugin_evaluation_counts[status] = plugin_evaluation_counts.get(status, 0) + 1
    plugin_evaluation_counts = dict(sorted(plugin_evaluation_counts.items()))
    summary: dict[str, object] = {
        "total_catalogue_count": total,
        "active_count": active,
        "repo_evaluated_count": evaluated,
        "unevaluated_count": total - evaluated,
        "evaluation_coverage": round(evaluated / total, 4) if total else 0.0,
        "admit_count": sum(1 for row in rows if row.repository.evaluation_disposition == "admit"),
        "revise_count": sum(1 for row in rows if row.repository.evaluation_disposition == "revise"),
        "defer_count": sum(1 for row in rows if row.repository.evaluation_disposition == "defer"),
        "suspended_count": sum(1 for row in rows if row.repository.evaluation_disposition == "suspend"),
        "stale_evaluation_count": sum(1 for row in rows if row.repository.evaluation_status == "stale"),
        "intake_candidate_count": len(intake.records),
        "intake_actionable_count": sum(1 for item in intake.records if item.next_action is not None),
        "intake_deferred_count": sum(1 for item in intake.records if item.disposition == "defer"),
        "intake_work_management_blocked_count": sum(1 for item in intake.records if item.work_management_state == "blocked"),
        "plugin_total_count": len(plugins.records),
        "plugin_candidate_count": plugin_portfolio_counts.get("candidate", 0),
        "plugin_accepted_count": plugin_portfolio_counts.get("accepted", 0),
        "plugin_deferred_count": plugin_portfolio_counts.get("deferred", 0),
        "plugin_rejected_count": plugin_portfolio_counts.get("rejected", 0),
        "plugin_suspended_count": plugin_portfolio_counts.get("suspended", 0),
        "plugin_source_status_counts": plugin_source_counts,
        "plugin_evaluation_status_counts": plugin_evaluation_counts,
        "plugin_pending_delta_count": sum(
            1
            for plugin in plugins.records
            if isinstance(plugin.record.get("update"), dict)
            and plugin.record["update"].get("delta_evidence") is not None
        ),
        "plugin_high_risk_without_current_evidence_count": sum(
            1
            for plugin in plugins.records
            if plugin.high_risk
            and (
                plugin.record.get("source_status") != "verified"
                or not isinstance(plugin.record.get("evaluation"), dict)
                or plugin.record["evaluation"].get("status") != "passed"
            )
        ),
        "plugin_target_installation_counts": _plugin_target_counts(
            plugins.records, "installation_status"
        ),
        "plugin_target_activation_counts": _plugin_target_counts(
            plugins.records, "activation_status"
        ),
        "plugin_required_app_gap_count": sum(
            len(target.get("required_app_access_gaps", []))
            for plugin in plugins.records
            for target in plugin.target_observations
        ),
        "compliance": load_compliance_summary(repo_path),
    }
    root_states = [status for _, status in inventory.root_statuses]
    if root_states and all(status == "observed" for status in root_states):
        catalogue_status = "observed" if inventory.entries else "empty"
    elif "observed" in root_states:
        catalogue_status = "partial"
    elif "invalid" in root_states:
        catalogue_status = "invalid"
    else:
        catalogue_status = "not_available"
    sources: dict[str, object] = {
        "catalogue": {
            "roots": [
                {"path": path, "status": status}
                for path, status in inventory.root_statuses
            ],
            "status": catalogue_status,
        },
        "repository": {"root": str(repo_path), "status": "observed" if repo_path.is_dir() else "not_available"},
        "intake": {"source": intake.source, "status": intake.status},
        "plugins": {"source": plugins.source, "status": plugins.status},
        "telemetry": {
            "source": telemetry.source,
            "status": telemetry.status,
            "event_count": telemetry.event_count,
        },
    }
    return DashboardReport(
        summary=summary,
        sources=sources,
        skills=tuple(rows),
        intake=intake.records,
        plugins=plugins.records,
        warnings=tuple(warnings),
    )


def _telemetry_dict(value: TelemetryEvidence | None, status: str) -> dict[str, object]:
    if value is None:
        not_observable_statuses = {
            "not_available",
            "invalid",
            "not_observable_due_to_truncation",
        }
        return {
            "status": status,
            "last_used_at": None,
            "last_used_status": (
                "not_observable" if status in not_observable_statuses else "not_observed"
            ),
        }
    return {
        "status": status,
        "content_sha256": value.content_sha256,
        "discovered_count": value.discovered_count,
        "loaded_count": value.loaded_count,
        "resource_read_count": value.resource_read_count,
        "evaluated_count": value.evaluated_count,
        "mutation_count": value.mutation_count,
        "applied_count": value.applied_count,
        "completed_count": value.completed_count,
        "failed_count": value.failed_count,
        "error_count": value.error_count,
        "last_used_at": value.last_used_at,
        "last_used_status": value.last_used_status,
        "projects": list(value.projects),
    }


def _plugin_dict(plugin: PluginReportRow) -> dict[str, object]:
    record = plugin.record
    update = dict(record.get("update", {})) if isinstance(record.get("update"), dict) else {}
    update["check_age_days"] = plugin.update_check_age_days
    update["pending_delta"] = update.get("delta_evidence") is not None
    return {
        "plugin_id": plugin.plugin_id,
        "display_name": record.get("display_name"),
        "plugin_kind": record.get("plugin_kind"),
        "portfolio_status": record.get("portfolio_status"),
        "source_status": record.get("source_status"),
        "source": dict(record.get("source", {})) if isinstance(record.get("source"), dict) else {},
        "contents": dict(record.get("contents", {})) if isinstance(record.get("contents"), dict) else {},
        "capabilities": dict(record.get("capabilities", {})) if isinstance(record.get("capabilities"), dict) else {},
        "dependencies": list(record.get("dependencies", [])) if isinstance(record.get("dependencies"), list) else [],
        "targets": [dict(target) for target in plugin.target_observations],
        "evaluation": dict(record.get("evaluation", {})) if isinstance(record.get("evaluation"), dict) else {},
        "update": update,
        "high_risk": plugin.high_risk,
        "source_path": plugin.source_path,
        "warnings": list(plugin.warnings),
    }


def report_to_dict(report: DashboardReport) -> dict[str, object]:
    providers_by_skill: dict[str, list[str]] = {}
    for plugin in report.plugins:
        contents = plugin.record.get("contents")
        provided = contents.get("skills") if isinstance(contents, dict) else None
        if isinstance(provided, list):
            for skill_id in provided:
                if isinstance(skill_id, str):
                    providers_by_skill.setdefault(skill_id, []).append(plugin.plugin_id)
    skills: list[dict[str, object]] = []
    for row in report.skills:
        catalog = row.catalog
        repository = row.repository
        skills.append(
            {
                "name": catalog.name,
                "description": catalog.description,
                "source_path": catalog.source_path,
                "modified_at": catalog.modified_at,
                "content_sha256": catalog.content_sha256,
                "status": catalog.status,
                "category": catalog.category,
                "parse_status": catalog.parse_status,
                "adoption_status": repository.adoption_status,
                "adopted_content_sha256": repository.adopted_content_sha256,
                "adoption_path": repository.adoption_path,
                "evaluation_status": repository.evaluation_status,
                "evaluation_disposition": repository.evaluation_disposition,
                "evaluation_path": repository.evaluation_path,
                "evaluation_runtime_sha256": repository.evaluation_runtime_sha256,
                "last_evaluated_at": repository.last_evaluated_at,
                "telemetry": _telemetry_dict(row.telemetry, row.telemetry_status),
                "provided_by_plugins": sorted(providers_by_skill.get(catalog.name, [])),
                "warnings": list(row.warnings),
            }
        )
    intake = [
        {
            "candidate_id": item.candidate_id,
            "candidate_type": item.candidate_type,
            "requested_at": item.requested_at,
            "source_issue": {
                "repository": item.source_repository,
                "number": item.source_issue_number,
            },
            "work_management_state": item.work_management_state,
            "provenance_type": item.provenance_type,
            "provenance_state": item.provenance_state,
            "license_state": item.license_state,
            "assessment_states": dict(item.assessment_states),
            "adaptation_state": item.adaptation_state,
            "evaluation_state": item.evaluation_state,
            "human_review_state": item.human_review_state,
            "disposition": item.disposition,
            "next_action": item.next_action,
            "targets": dict(item.targets),
            "source_path": item.source_path,
            "warnings": list(item.warnings),
        }
        for item in report.intake
    ]
    plugins = [_plugin_dict(plugin) for plugin in report.plugins]
    return {
        "schema_version": report.schema_version,
        "summary": dict(report.summary),
        "sources": dict(report.sources),
        "warnings": list(report.warnings),
        "skills": skills,
        "intake": intake,
        "plugins": plugins,
    }


def report_to_json(report: DashboardReport) -> str:
    return json.dumps(report_to_dict(report), indent=2, sort_keys=True) + "\n"
