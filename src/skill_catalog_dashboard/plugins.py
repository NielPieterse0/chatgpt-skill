from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Mapping

from scripts.plugin_portfolio import validate_repository

from .models import PluginReportRow, PluginSnapshot


_HIGH_RISK_FLAGS = (
    "process_execution",
    "network",
    "credentials",
    "external_mutation",
)
_APP_GAP_STATES = {"unavailable", "not_connected", "blocked"}


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, dict) else {}


def _age_days(value: object) -> int | None:
    if not isinstance(value, str):
        return None
    try:
        return (date.today() - date.fromisoformat(value)).days
    except ValueError:
        return None


def _high_risk(record: Mapping[str, Any]) -> bool:
    capabilities = _mapping(record.get("capabilities"))
    if any(capabilities.get(name) is True for name in _HIGH_RISK_FLAGS):
        return True
    writes = capabilities.get("filesystem_write")
    return isinstance(writes, list) and bool(writes)


def _required_apps(record: Mapping[str, Any]) -> set[str]:
    required: set[str] = set()
    dependencies = record.get("dependencies")
    if not isinstance(dependencies, list):
        return required
    for dependency in dependencies:
        value = _mapping(dependency)
        if value.get("kind") == "app" and value.get("required") is True:
            app_id = value.get("id")
            if isinstance(app_id, str):
                required.add(app_id)
    return required


def _target_observations(
    record: Mapping[str, Any], required_apps: set[str]
) -> tuple[Mapping[str, object], ...]:
    observations: list[Mapping[str, object]] = []
    targets = record.get("targets")
    if not isinstance(targets, list):
        return ()
    for target_value in targets:
        target = dict(_mapping(target_value))
        access = target.get("app_access")
        by_app: dict[str, str] = {}
        if isinstance(access, list):
            for app_value in access:
                app = _mapping(app_value)
                app_id = app.get("app_id")
                status = app.get("access_status")
                if isinstance(app_id, str) and isinstance(status, str):
                    by_app[app_id] = status
        target["required_app_access_gaps"] = sorted(
            app_id
            for app_id in required_apps
            if by_app.get(app_id) in _APP_GAP_STATES
        )
        target["required_app_access_unobserved"] = sorted(
            app_id
            for app_id in required_apps
            if by_app.get(app_id) in {None, "not_observed"}
        )
        observations.append(target)
    return tuple(observations)


def _warnings(
    record: Mapping[str, Any],
    *,
    high_risk: bool,
    targets: tuple[Mapping[str, object], ...],
) -> tuple[str, ...]:
    warnings: list[str] = []
    source_status = record.get("source_status")
    if source_status != "verified":
        warnings.append(f"source status is {source_status}")
    evaluation = _mapping(record.get("evaluation"))
    evaluation_status = evaluation.get("status")
    if evaluation_status in {"failed", "stale"}:
        warnings.append(f"evaluation status is {evaluation_status}")
    update = _mapping(record.get("update"))
    if update.get("delta_evidence") is not None:
        warnings.append("update delta awaits review")
    if high_risk and (
        source_status != "verified" or evaluation_status != "passed"
    ):
        warnings.append("high-risk plugin lacks current verified/passed evidence")
    for target in targets:
        gaps = target.get("required_app_access_gaps")
        target_id = target.get("target_id")
        if isinstance(gaps, list) and gaps:
            warnings.append(
                f"required app access gap on {target_id}: {', '.join(gaps)}"
            )
    return tuple(warnings)


def load_plugin_portfolio(repo_root: Path | str) -> PluginSnapshot:
    root = Path(repo_root).expanduser().resolve()
    portfolio_root = root / "portfolio" / "plugins"
    validation = validate_repository(root)
    if not validation.ok:
        warnings = tuple(
            f"{issue.code}: {issue.message} [{issue.path}]"
            for issue in validation.errors
        )
        return PluginSnapshot(
            records=(), status="invalid", source=str(portfolio_root), warnings=warnings
        )

    rows: list[PluginReportRow] = []
    for source_path, value in sorted(
        validation.validated_records, key=lambda item: str(item[1].get("plugin_id", ""))
    ):
        required_apps = _required_apps(value)
        targets = _target_observations(value, required_apps)
        high_risk = _high_risk(value)
        update = _mapping(value.get("update"))
        rows.append(
            PluginReportRow(
                plugin_id=str(value["plugin_id"]),
                source_path=source_path,
                record=value,
                update_check_age_days=_age_days(update.get("last_checked_at")),
                high_risk=high_risk,
                target_observations=targets,
                warnings=_warnings(value, high_risk=high_risk, targets=targets),
            )
        )
    return PluginSnapshot(
        records=tuple(rows),
        status="observed",
        source=str(portfolio_root),
    )
