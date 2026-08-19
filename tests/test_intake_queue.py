from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skill_catalog_dashboard.intake import load_intake_queue, validate_intake_record
from skill_catalog_dashboard.report import build_report, report_to_dict
from skill_catalog_dashboard.web import render_html


def base_record(candidate_id: str = "sample-skill") -> dict[str, object]:
    return {
        "schema_version": 1,
        "candidate_id": candidate_id,
        "candidate_type": "skill",
        "requested_at": "2026-08-16",
        "source_issue": {
            "repository": "NielPieterse0/chatgpt-skill",
            "number": 82,
        },
        "work_management": {
            "state": "blocked",
            "record_id": None,
            "revision": None,
            "blocker_issue": 81,
        },
        "provenance": {
            "type": "trusted-local",
            "state": "verified",
            "source_locator": "C:\\Projects\\staged\\sample-skill",
            "revision": "a" * 40,
            "candidate_sha256": "b" * 64,
            "handoff": None,
        },
        "license": {"state": "pending", "identifier": None},
        "assessments": {
            "structural": "due",
            "security": "due",
            "capability": "due",
            "overlap": "due",
        },
        "adaptation": {"state": "pending"},
        "evaluation": {"state": "blocked"},
        "human_review": {"state": "pending"},
        "disposition": "pending",
        "targets": {
            "workspace_catalogue": "pending",
            "repository_admission": "pending",
            "runtime_enablement": "disabled",
            "plugin_installation": "not_applicable",
            "plugin_activation": "not_applicable",
        },
    }


class IntakeQueueTests(unittest.TestCase):
    def test_trusted_local_candidate_has_deterministic_next_action(self) -> None:
        result = validate_intake_record(base_record())
        self.assertEqual(result.next_action, "review_provenance_license")
        self.assertEqual(result.candidate_id, "sample-skill")
        self.assertEqual(result.work_management_state, "blocked")
        self.assertIn("Work Management projection blocked by issue #81", result.warnings)

    def test_import_isolate_pending_handoff_is_actionable_without_source_bytes(self) -> None:
        record = base_record("external-skill")
        record["provenance"] = {
            "type": "import-isolate",
            "state": "pending",
            "source_locator": "https://github.com/example/external-skill",
            "revision": None,
            "candidate_sha256": None,
            "handoff": None,
        }
        result = validate_intake_record(record)
        self.assertEqual(result.next_action, "await_import_isolate_handoff")

    def test_verified_import_isolate_requires_finalized_handoff_identity(self) -> None:
        record = base_record("external-skill")
        record["provenance"] = {
            "type": "import-isolate",
            "state": "verified",
            "source_locator": "https://github.com/example/external-skill",
            "revision": "c" * 40,
            "candidate_sha256": "d" * 64,
            "handoff": None,
        }
        with self.assertRaisesRegex(ValueError, "finalized import-isolate handoff"):
            validate_intake_record(record)

        record["provenance"]["handoff"] = {
            "case_id": "CASE-001",
            "artifact": "external-skill.tar.gz",
            "artifact_sha256": "d" * 64,
        }
        result = validate_intake_record(record)
        self.assertEqual(result.next_action, "review_provenance_license")

    def test_admit_fails_closed_until_review_and_evaluation_are_complete(self) -> None:
        record = base_record()
        record["license"] = {"state": "reviewed", "identifier": "MIT"}
        record["assessments"] = {
            "structural": "passed",
            "security": "passed",
            "capability": "passed",
            "overlap": "passed",
        }
        record["adaptation"] = {"state": "not_required"}
        record["evaluation"] = {"state": "complete"}
        record["disposition"] = "admit"
        with self.assertRaisesRegex(ValueError, "human review"):
            validate_intake_record(record)

        record["human_review"] = {"state": "complete"}
        record["targets"]["workspace_catalogue"] = "admitted"
        result = validate_intake_record(record)
        self.assertIsNone(result.next_action)
    def test_skill_candidate_cannot_gain_plugin_runtime_state(self) -> None:
        record = base_record()
        record["targets"]["plugin_installation"] = "installed"
        with self.assertRaisesRegex(ValueError, "skill candidate.*plugin"):
            validate_intake_record(record)

    def test_loader_surfaces_malformed_records_instead_of_hiding_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = root / "intake" / "candidates" / "good"
            bad = root / "intake" / "candidates" / "bad"
            good.mkdir(parents=True)
            bad.mkdir(parents=True)
            (good / "intake-record.json").write_text(
                json.dumps(base_record("good")), encoding="utf-8"
            )
            (bad / "intake-record.json").write_text("{bad", encoding="utf-8")
            snapshot = load_intake_queue(root)
        self.assertEqual(snapshot.status, "invalid")
        self.assertEqual([item.candidate_id for item in snapshot.records], ["good"])
        self.assertTrue(any("bad/intake-record.json" in warning for warning in snapshot.warnings))

    def test_loader_rejects_opened_record_outside_validated_queue_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "intake" / "candidates" / "candidate"
            candidate.mkdir(parents=True)
            record_path = candidate / "intake-record.json"
            record_path.write_text(json.dumps(base_record("candidate")), encoding="utf-8")
            with mock.patch(
                "skill_catalog_dashboard.intake.opened_path",
                return_value=root / "outside" / "intake-record.json",
            ):
                snapshot = load_intake_queue(root)
        self.assertEqual(snapshot.status, "invalid")
        self.assertEqual(snapshot.records, ())
        self.assertTrue(any("escaped validated intake path" in warning for warning in snapshot.warnings))

    def test_dashboard_keeps_intake_population_separate_from_skill_totals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "catalog"
            skill = catalog / "canonical-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: canonical-skill\ndescription: test\n---\n", encoding="utf-8"
            )
            intake = root / "repo" / "intake" / "candidates" / "candidate"
            intake.mkdir(parents=True)
            (intake / "intake-record.json").write_text(
                json.dumps(base_record("candidate")), encoding="utf-8"
            )
            report = build_report([catalog], repo_root=root / "repo", telemetry_json=None)
            payload = report_to_dict(report)
            html = render_html(report)
        self.assertEqual(payload["summary"]["total_catalogue_count"], 1)
        self.assertEqual(payload["summary"]["intake_candidate_count"], 1)
        self.assertEqual(payload["summary"]["intake_actionable_count"], 1)
        self.assertEqual(payload["intake"][0]["candidate_id"], "candidate")
        self.assertEqual(payload["intake"][0]["next_action"], "review_provenance_license")
        self.assertEqual(payload["sources"]["intake"]["status"], "observed")
        self.assertIn("Intake queue", html)
        self.assertIn("review_provenance_license", html)


if __name__ == "__main__":
    unittest.main()
