from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.plugin_portfolio import validate_repository
from skill_catalog_dashboard.intake import validate_intake_record


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "portfolio" / "plugins" / "superpowers"
INTAKE = ROOT / "intake" / "candidates" / "superpowers" / "intake-record.json"
BUNDLE_SHA256 = "a1cbc2e46d5c2709c5827fe28296a8dbcb972509e71cb3f2567295377d6f0430"
SKILLS = {
    "brainstorming", "dispatching-parallel-agents", "executing-plans",
    "finishing-a-development-branch", "receiving-code-review",
    "requesting-code-review", "subagent-driven-development",
    "systematic-debugging", "test-driven-development", "using-git-worktrees",
    "using-superpowers", "verification-before-completion", "writing-plans",
    "writing-skills",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class SuperpowersPluginPilotTests(unittest.TestCase):
    def test_intake_and_portfolio_records_are_non_runtime_and_valid(self) -> None:
        intake = validate_intake_record(read_json(INTAKE))
        self.assertEqual("plugin", intake.candidate_type)
        self.assertEqual("defer", intake.disposition)
        self.assertEqual("disabled", intake.targets["runtime_enablement"])
        self.assertEqual("not_installed", intake.targets["plugin_installation"])
        self.assertEqual("inactive", intake.targets["plugin_activation"])

        report = validate_repository(ROOT)
        self.assertTrue(report.ok, [issue.to_dict() for issue in report.errors])
        record = read_json(PLUGIN / "plugin-record.json")
        self.assertEqual("deferred", record["portfolio_status"])
        self.assertEqual("unverified", record["source_status"])
        self.assertEqual(BUNDLE_SHA256, record["source"]["artifact_sha256"])
        self.assertEqual("deferred", record["evaluation"]["status"])
        self.assertTrue(all(target["activation_status"] != "active" for target in record["targets"]))

    def test_aggregate_evidence_covers_authority_host_and_telemetry_risks(self) -> None:
        aggregate = read_json(PLUGIN / "evidence" / "bundle-assessment.json")
        self.assertEqual(BUNDLE_SHA256, aggregate["bundle_sha256"])
        self.assertEqual(72, aggregate["file_count"])
        self.assertEqual(14, aggregate["skill_count"])
        self.assertEqual(SKILLS, set(aggregate["skills"]))
        self.assertEqual([], aggregate["exact_workspace_skill_overlap"])
        self.assertEqual("not_observed", aggregate["upstream_authentication_status"])
        self.assertEqual("defer_runtime_evaluation", aggregate["disposition"])
        self.assertIn("authority_conflict", aggregate["runtime_blockers"])
        self.assertIn("process_execution", aggregate["runtime_blockers"])
        self.assertIn("network_telemetry", aggregate["runtime_blockers"])
        self.assertEqual(
            {"AGENTS.md", "KIS Work Management", "repository verification/closeout", "canonical skill governance"},
            set(aggregate["higher_authorities"]),
        )
        telemetry = aggregate["visual_companion_telemetry"]
        self.assertEqual("optional_remote_logo_load", telemetry["behavior"])
        self.assertIn("SUPERPOWERS_DISABLE_TELEMETRY", telemetry["opt_out_environment_variables"])
        self.assertGreaterEqual(len(aggregate["host_harnesses"]), 10)
        self.assertTrue(aggregate["conceptual_workspace_overlap"])

    def test_every_plugin_skill_has_bound_static_evidence(self) -> None:
        record = read_json(PLUGIN / "plugin-record.json")
        self.assertEqual(SKILLS, set(record["contents"]["skills"]))
        expected = {"portfolio/plugins/superpowers/evidence/bundle-assessment.json"}
        for skill_id in SKILLS:
            path = PLUGIN / "evidence" / "skills" / f"{skill_id}.json"
            evidence = read_json(path)
            self.assertEqual(skill_id, evidence["entry_id"])
            self.assertEqual(skill_id, evidence["frontmatter_name"])
            self.assertRegex(evidence["source_skill_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual("passed", evidence["structural_status"])
            self.assertEqual("deferred", evidence["runtime_evaluation_status"])
            expected.add(path.relative_to(ROOT).as_posix())
        self.assertEqual(expected, set(record["evaluation"]["evidence"]))

    def test_plugin_is_absent_from_repository_runtime_discovery(self) -> None:
        runtime_control = read_json(ROOT / "config" / "runtime-control.json")
        self.assertFalse(runtime_control["skills_enabled"])
        adopted_names = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertTrue(SKILLS.isdisjoint(adopted_names))
        self.assertNotIn("superpowers", adopted_names)
        self.assertFalse((ROOT / "skills" / "superpowers").exists())


if __name__ == "__main__":
    unittest.main()
