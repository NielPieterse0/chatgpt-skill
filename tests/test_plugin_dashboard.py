from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skill_catalog_dashboard.report import build_report, report_to_dict, report_to_json
from skill_catalog_dashboard.web import render_html


def _skill(root: Path, name: str) -> None:
    target = root / name
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test {name}.\n---\n# {name}\n",
        encoding="utf-8",
    )


def _record(
    plugin_id: str,
    *,
    portfolio_status: str = "candidate",
    source_status: str = "verified",
    evaluation_status: str = "not_started",
    skills: tuple[str, ...] = ("alpha",),
    high_risk: bool = False,
    target_id: str | None = None,
    installation_status: str = "not_observed",
    activation_status: str = "not_observed",
    app_status: str | None = None,
    pending_delta: bool = False,
) -> dict[str, object]:
    revision = "a" * 40
    evidence = [f"evidence/{plugin_id}-eval.json"] if portfolio_status == "accepted" else []
    return {
        "schema_version": 1,
        "plugin_id": plugin_id,
        "display_name": plugin_id.replace("-", " ").title(),
        "plugin_kind": "codex-plugin",
        "portfolio_status": portfolio_status,
        "source_status": source_status,
        "source": {
            "provenance_type": "trusted-local",
            "owner": "example-org",
            "canonical_uri": f"https://example.test/{plugin_id}",
            "version": "1.2.3",
            "immutable_revision": revision,
            "retrieved_at": "2026-08-16",
            "artifact_sha256": "b" * 64,
            "license_or_terms": "MIT",
            "handoff": None,
        },
        "contents": {
            "skills": list(skills),
            "apps": ["github"] if app_status is not None else [],
            "app_templates": [],
            "mcp_or_tooling": ["helper"] if high_risk else [],
            "resources": ["README.md"],
        },
        "capabilities": {
            "filesystem_read": ["fixtures/"],
            "filesystem_write": ["outputs/"] if high_risk else [],
            "process_execution": high_risk,
            "network": high_risk,
            "credentials": False,
            "external_mutation": False,
        },
        "dependencies": (
            [{"id": "github", "kind": "app", "version": None, "required": True}]
            if app_status is not None
            else []
        ),
        "targets": (
            [{
                "target_id": target_id,
                "installation_status": installation_status,
                "activation_status": activation_status,
                "app_access": (
                    [{"app_id": "github", "access_status": app_status}]
                    if app_status is not None
                    else []
                ),
            }]
            if target_id is not None
            else []
        ),
        "evaluation": {
            "status": evaluation_status,
            "evidence": evidence,
            "baseline": "without-plugin" if portfolio_status == "accepted" else None,
            "reviewer": "reviewer" if portfolio_status == "accepted" else None,
            "reviewed_at": date.today().isoformat() if portfolio_status == "accepted" else None,
        },
        "update": {
            "last_accepted_revision": revision if portfolio_status == "accepted" else None,
            "last_checked_at": date.today().isoformat(),
            "delta_evidence": f"evidence/{plugin_id}-delta.json" if pending_delta else None,
        },
        "rollback": {
            "disable_method": "Disable integration." if portfolio_status == "accepted" else None,
            "uninstall_method": None,
            "retained_evidence": evidence,
        },
    }


def _write_plugin(repo: Path, record: dict[str, object]) -> None:
    plugin_id = str(record["plugin_id"])
    path = repo / "portfolio" / "plugins" / plugin_id / "plugin-record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    evidence = set(record["evaluation"]["evidence"])
    delta = record["update"]["delta_evidence"]
    if isinstance(delta, str):
        evidence.add(delta)
    for relative in evidence:
        target = repo / str(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n", encoding="utf-8")


class PluginDashboardTests(unittest.TestCase):
    def test_plugin_population_is_separate_from_skill_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            _skill(catalog, "alpha")
            records = (
                _record("candidate-plugin"),
                _record("accepted-plugin", portfolio_status="accepted", evaluation_status="passed"),
                _record("deferred-plugin", portfolio_status="deferred", evaluation_status="deferred"),
                _record("rejected-plugin", portfolio_status="rejected", source_status="unverified"),
                _record("suspended-plugin", portfolio_status="suspended", source_status="stale", evaluation_status="stale"),
            )
            for record in records:
                _write_plugin(repo, record)

            payload = report_to_dict(build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3"))

            self.assertEqual(1, payload["summary"]["total_catalogue_count"])
            self.assertEqual(1, payload["summary"]["active_count"])
            self.assertEqual(0, payload["summary"]["repo_evaluated_count"])
            self.assertEqual(0.0, payload["summary"]["evaluation_coverage"])
            summary = payload["summary"]
            self.assertEqual(5, summary["plugin_total_count"])
            self.assertEqual(1, summary["plugin_candidate_count"])
            self.assertEqual(1, summary["plugin_accepted_count"])
            self.assertEqual(1, summary["plugin_deferred_count"])
            self.assertEqual(1, summary["plugin_rejected_count"])
            self.assertEqual(1, summary["plugin_suspended_count"])
            self.assertEqual(3, summary["plugin_source_status_counts"]["verified"])
            self.assertEqual(1, summary["plugin_source_status_counts"]["stale"])
            self.assertEqual(1, summary["plugin_source_status_counts"]["unverified"])
            self.assertEqual(1, summary["plugin_evaluation_status_counts"]["passed"])
            self.assertEqual(1, summary["plugin_evaluation_status_counts"]["deferred"])
            self.assertEqual(1, summary["plugin_evaluation_status_counts"]["stale"])
            self.assertEqual(5, len(payload["plugins"]))
            self.assertEqual(
                sorted(record["plugin_id"] for record in records),
                payload["skills"][0]["provided_by_plugins"],
            )

    def test_plugin_rows_project_update_target_app_and_risk_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            _skill(catalog, "alpha")
            record = _record(
                "risky-plugin",
                portfolio_status="deferred",
                source_status="stale",
                evaluation_status="deferred",
                high_risk=True,
                target_id="codex",
                installation_status="installed",
                activation_status="inactive",
                app_status="not_connected",
                pending_delta=True,
            )
            _write_plugin(repo, record)

            payload = report_to_dict(build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3"))
            plugin = payload["plugins"][0]

            self.assertEqual("risky-plugin", plugin["plugin_id"])
            self.assertEqual("1.2.3", plugin["source"]["version"])
            self.assertEqual("a" * 40, plugin["source"]["immutable_revision"])
            self.assertEqual(0, plugin["update"]["check_age_days"])
            self.assertTrue(plugin["update"]["pending_delta"])
            self.assertTrue(plugin["high_risk"])
            self.assertEqual(["github"], plugin["targets"][0]["required_app_access_gaps"])
            self.assertEqual([], plugin["targets"][0]["required_app_access_unobserved"])
            summary = payload["summary"]
            self.assertEqual(1, summary["plugin_pending_delta_count"])
            self.assertEqual(1, summary["plugin_high_risk_without_current_evidence_count"])
            self.assertEqual(1, summary["plugin_target_installation_counts"]["codex"]["installed"])
            self.assertEqual(1, summary["plugin_target_activation_counts"]["codex"]["inactive"])
            self.assertEqual(1, summary["plugin_required_app_gap_count"])
            self.assertTrue(any("source status is stale" in warning for warning in plugin["warnings"]))
            self.assertTrue(any("update delta" in warning for warning in plugin["warnings"]))

    def test_invalid_portfolio_fails_closed_without_partial_projection(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            _skill(catalog, "alpha")
            _write_plugin(repo, _record("good-plugin"))
            bad = _record("bad-plugin")
            bad["unexpected"] = True
            _write_plugin(repo, bad)

            payload = report_to_dict(build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3"))

            self.assertEqual("invalid", payload["sources"]["plugins"]["status"])
            self.assertEqual([], payload["plugins"])
            self.assertEqual(0, payload["summary"]["plugin_total_count"])
            self.assertEqual([], payload["skills"][0]["provided_by_plugins"])
            self.assertTrue(any("RECORD_UNKNOWN" in warning for warning in payload["warnings"]))
            self.assertEqual(1, payload["summary"]["total_catalogue_count"])

    def test_empty_plugin_portfolio_is_observed_without_affecting_skills(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            (repo / "portfolio" / "plugins").mkdir(parents=True)
            _skill(catalog, "alpha")

            payload = report_to_dict(
                build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )

            self.assertEqual("observed", payload["sources"]["plugins"]["status"])
            self.assertEqual(0, payload["summary"]["plugin_total_count"])
            self.assertEqual([], payload["plugins"])
            self.assertEqual(1, payload["summary"]["total_catalogue_count"])
            self.assertEqual(1, payload["summary"]["active_count"])

    def test_plugin_projection_is_deterministic_and_visible_in_html(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            _skill(catalog, "alpha")
            _write_plugin(repo, _record("example-plugin", portfolio_status="deferred", evaluation_status="deferred"))

            report = build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")

            self.assertEqual(report_to_json(report), report_to_json(report))
            rendered = render_html(report)
            self.assertIn("<h2>Plugin portfolio</h2>", rendered)
            self.assertIn("Example Plugin", rendered)
            self.assertIn("Provided by plugins", rendered)


if __name__ == "__main__":
    unittest.main()
