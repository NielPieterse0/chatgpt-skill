from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_effectiveness.py"
spec = importlib.util.spec_from_file_location("skill_effectiveness", SCRIPT)
assert spec and spec.loader
skill_effectiveness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_effectiveness)


class SkillEffectivenessTests(unittest.TestCase):
    skill_id = "develop-code"

    def _definitions(self) -> dict:
        return skill_effectiveness.load_definitions(ROOT, self.skill_id)

    def _record(self) -> dict:
        definitions = self._definitions()
        manifest = json.loads(
            (ROOT / "skills" / self.skill_id / "adoption-manifest.json").read_text()
        )
        skill_md = (ROOT / "skills" / self.skill_id / "SKILL.md").read_bytes()
        trigger_cases = []
        for case in definitions["trigger"]:
            expected = case["expected"]
            trigger_cases.append(
                {
                    "id": case["id"],
                    "triggers": 3 if expected == "trigger" else 0,
                    "runs": 3,
                }
            )

        output_runs = []
        for eval_case in definitions["output"]:
            for configuration, passed, duration in (
                ("with_skill", True, 100),
                ("baseline", False, 80),
            ):
                output_runs.append(
                    {
                        "eval_id": eval_case["id"],
                        "configuration": configuration,
                        "run": 1,
                        "assertions": [
                            {
                                "id": assertion["id"],
                                "passed": passed,
                                "evidence": f"{configuration}:{assertion['id']}",
                            }
                            for assertion in eval_case["assertions"]
                        ],
                        "metrics": {
                            "duration_ms": duration,
                            "input_tokens": 0 if configuration == "with_skill" else 20,
                            "output_tokens": 10,
                            "tool_calls": 2 if configuration == "with_skill" else 1,
                            "retries": 0,
                        },
                        "not_observable": {},
                    }
                )

        return {
            "schema_version": 1,
            "skill_id": self.skill_id,
            "adopted_content_sha256": manifest["source"]["adopted_content_sha256"],
            "runtime_content_sha256": hashlib.sha256(skill_md).hexdigest(),
            "adapter": "chatgpt",
            "target_verified_at": "2026-08-14",
            "eval_definition_revision": subprocess.run(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                capture_output=True,
                check=True,
                text=True,
            ).stdout.strip(),
            "baseline": {"kind": "no-skill", "identity": "no-skill"},
            "isolation_method": "fresh isolated agent context per run",
            "trigger": {
                "observability": "observed",
                "reason": None,
                "cases": trigger_cases,
            },
            "output_observability": {"status": "observed", "reason": None},
            "output_runs": output_runs,
            "verification": [
                {"id": "repo-verify", "passed": True, "evidence": "verification passed"}
            ],
            "abuse_observability": {"status": "observed", "reason": None},
            "abuse": [
                {"id": case["id"], "passed": True, "evidence": "control held"}
                for case in definitions["abuse"]
            ],
            "compatibility": {"status": "pass", "evidence": "adapter contract passed"},
            "human_review": {
                "status": "pass",
                "reviewer": "repository-owner",
                "date": "2026-08-14",
                "feedback": [],
            },
            "rollback": {"verified": True, "evidence": "disablement verified"},
            "production_regressions": [],
        }

    def _telemetry_group(self, record: dict) -> dict:
        return {
            "skill_id": self.skill_id,
            "content_sha256": record["runtime_content_sha256"],
            "project_id": "chatgpt-skill",
            "discovered_count": 4,
            "loaded_count": 3,
            "resource_read_count": 2,
            "evaluated_count": 1,
            "mutation_count": 0,
            "applied_count": 2,
            "completed_count": 1,
            "failed_count": 1,
            "error_count": 0,
            "duration_samples": 2,
            "total_duration_ms": 30,
            "token_samples": 0,
            "total_tokens": None,
            "tool_call_samples": 0,
            "total_tool_calls": None,
            "retry_samples": 0,
            "total_retries": None,
            "verification_samples": 1,
            "verification_passes": 1,
        }

    def test_passing_observed_record_recommends_admit(self) -> None:
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, self._record())
        self.assertEqual(scorecard["recommended_disposition"], "admit")
        self.assertEqual(scorecard["blocking_reasons"], [])
        self.assertEqual(scorecard["dimensions"]["trigger"]["status"], "pass")
        self.assertEqual(scorecard["dimensions"]["output_quality"]["status"], "pass")
        self.assertTrue(scorecard["dimensions"]["output_quality"]["material_improvements"])
        self.assertEqual(
            scorecard["dimensions"]["efficiency"]["metrics"]["input_tokens"]["with_skill"]["mean"],
            0.0,
        )

    def test_trigger_three_run_boundaries(self) -> None:
        definitions = self._definitions()["trigger"]
        positive_id = next(item["id"] for item in definitions if item["category"] == "positive")
        near_miss_id = next(item["id"] for item in definitions if item["category"] == "near_miss")

        for case_id, triggers, expected_pass in (
            (positive_id, 2, True),
            (positive_id, 1, False),
            (near_miss_id, 1, True),
            (near_miss_id, 2, False),
        ):
            with self.subTest(case_id=case_id, triggers=triggers):
                record = self._record()
                result = next(item for item in record["trigger"]["cases"] if item["id"] == case_id)
                result["triggers"] = triggers
                scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
                case = next(
                    item for item in scorecard["dimensions"]["trigger"]["cases"]
                    if item["id"] == case_id
                )
                self.assertEqual(case["passed"], expected_pass)
                if expected_pass:
                    self.assertEqual(scorecard["dimensions"]["trigger"]["status"], "pass")
                else:
                    self.assertEqual(scorecard["dimensions"]["trigger"]["status"], "fail")
                    self.assertEqual(scorecard["recommended_disposition"], "revise")
                    self.assertIn("trigger:boundary_failure", scorecard["blocking_reasons"])

    def test_conflict_and_injection_trigger_boundaries_are_strict(self) -> None:
        definitions = [
            item
            for item in self._definitions()["trigger"]
            if item["category"] in {"conflict", "prompt_injection"}
        ]
        for definition in definitions:
            passing_triggers = 3 if definition["expected"] == "trigger" else 0
            failing_triggers = 2 if definition["expected"] == "trigger" else 1
            for triggers, expected_pass in ((passing_triggers, True), (failing_triggers, False)):
                with self.subTest(case_id=definition["id"], triggers=triggers):
                    record = self._record()
                    result = next(
                        item for item in record["trigger"]["cases"]
                        if item["id"] == definition["id"]
                    )
                    result["triggers"] = triggers
                    scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
                    case = next(
                        item for item in scorecard["dimensions"]["trigger"]["cases"]
                        if item["id"] == definition["id"]
                    )
                    self.assertEqual(case["passed"], expected_pass)
                    if expected_pass:
                        self.assertEqual(scorecard["dimensions"]["trigger"]["status"], "pass")
                    else:
                        self.assertEqual(scorecard["dimensions"]["trigger"]["status"], "fail")
                        self.assertEqual(scorecard["recommended_disposition"], "revise")
                        self.assertIn("trigger:boundary_failure", scorecard["blocking_reasons"])

    def test_unobservable_trigger_defers_without_inventing_result(self) -> None:
        record = self._record()
        record["trigger"] = {
            "observability": "not_observable",
            "reason": "target exposes no activation trace",
            "cases": [],
        }
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        self.assertEqual(scorecard["recommended_disposition"], "defer")
        self.assertEqual(scorecard["dimensions"]["trigger"]["status"], "not_observable")
        self.assertIn("trigger:not_observable", scorecard["blocking_reasons"])

    def test_unobservable_output_and_abuse_defer_without_fabricated_runs(self) -> None:
        record = self._record()
        record["output_observability"] = {
            "status": "not_observable",
            "reason": "raw candidate/baseline run artifacts are unavailable",
        }
        record["output_runs"] = []
        record["abuse_observability"] = {
            "status": "not_observable",
            "reason": "scenario execution evidence is unavailable",
        }
        record["abuse"] = []
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        self.assertEqual(scorecard["recommended_disposition"], "defer")
        self.assertEqual(scorecard["dimensions"]["output_quality"]["status"], "not_observable")
        self.assertEqual(scorecard["dimensions"]["abuse"]["status"], "not_observable")
        self.assertIn("output:not_observable", scorecard["blocking_reasons"])
        self.assertIn("abuse:not_observable", scorecard["blocking_reasons"])

    def test_failed_critical_assertion_recommends_revise(self) -> None:
        record = self._record()
        candidate = next(
            run for run in record["output_runs"] if run["configuration"] == "with_skill"
        )
        candidate["assertions"][0]["passed"] = False
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        self.assertEqual(scorecard["recommended_disposition"], "revise")
        self.assertTrue(scorecard["dimensions"]["output_quality"]["critical_failures"])

    def test_baseline_critical_regression_is_explicit(self) -> None:
        record = self._record()
        candidate = next(
            run for run in record["output_runs"] if run["configuration"] == "with_skill"
        )
        baseline = next(
            run
            for run in record["output_runs"]
            if run["configuration"] == "baseline"
            and run["eval_id"] == candidate["eval_id"]
        )
        candidate["assertions"][0]["passed"] = False
        baseline["assertions"][0]["passed"] = True
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        regressions = scorecard["dimensions"]["output_quality"]["baseline_critical_regressions"]
        self.assertTrue(regressions)
        self.assertIn("output:baseline_critical_regression", scorecard["blocking_reasons"])

    def test_missing_metric_requires_not_observable_reason(self) -> None:
        record = self._record()
        run = record["output_runs"][0]
        run["metrics"]["tool_calls"] = None
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        run["not_observable"]["tool_calls"] = "tool trace unavailable"
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        metric = scorecard["dimensions"]["efficiency"]["metrics"]["tool_calls"]
        self.assertEqual(metric["with_skill"]["status"], "partial")

    def test_telemetry_is_non_causal_and_version_filtered(self) -> None:
        record = self._record()
        telemetry = {
            "schema_version": 1,
            "event_count": 99,
            "truncated": True,
            "groups": [
                {
                    "skill_id": self.skill_id,
                    "content_sha256": record["runtime_content_sha256"],
                    "project_id": "chatgpt-skill",
                    "discovered_count": 4,
                    "loaded_count": 3,
                    "resource_read_count": 2,
                    "evaluated_count": 1,
                    "mutation_count": 0,
                    "applied_count": 2,
                    "completed_count": 1,
                    "failed_count": 1,
                    "error_count": 0,
                    "duration_samples": 2,
                    "total_duration_ms": 30,
                    "token_samples": 0,
                    "total_tokens": None,
                    "tool_call_samples": 0,
                    "total_tool_calls": None,
                    "retry_samples": 0,
                    "total_retries": None,
                    "verification_samples": 1,
                    "verification_passes": 1,
                },
            ],
        }
        other_group = copy.deepcopy(telemetry["groups"][0])
        other_group.update(
            {"content_sha256": "f" * 64, "project_id": "other", "loaded_count": 50}
        )
        telemetry["groups"].append(other_group)
        scorecard = skill_effectiveness.evaluate_record(
            ROOT, self.skill_id, record, telemetry=telemetry
        )
        operational = scorecard["dimensions"]["operational_telemetry"]
        self.assertEqual(operational["status"], "truncated")
        self.assertEqual(operational["totals"]["loaded_count"], 3)
        self.assertEqual(scorecard["recommended_disposition"], "admit")
        self.assertFalse(operational["behavioral_effectiveness_evidence"])

    def test_unknown_field_and_version_mismatch_fail_closed(self) -> None:
        record = self._record()
        record["unexpected"] = True
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        record = self._record()
        record["adopted_content_sha256"] = "0" * 64
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_missing_definition_result_fails_closed(self) -> None:
        record = self._record()
        record["abuse"] = record["abuse"][:-1]
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_no_material_improvement_recommends_revise(self) -> None:
        record = self._record()
        for run in record["output_runs"]:
            if run["configuration"] == "baseline":
                for assertion in run["assertions"]:
                    assertion["passed"] = True
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        self.assertEqual(scorecard["recommended_disposition"], "revise")
        self.assertEqual(scorecard["dimensions"]["output_quality"]["status"], "fail")
        self.assertIn("output:no_material_improvement", scorecard["blocking_reasons"])

    def test_material_improvement_two_thirds_boundary(self) -> None:
        def repeated_record() -> dict:
            record = self._record()
            expanded = []
            for run in record["output_runs"]:
                for run_no in (1, 2, 3):
                    item = copy.deepcopy(run)
                    item["run"] = run_no
                    expanded.append(item)
            record["output_runs"] = expanded
            return record

        target = ("output-001", "classification")

        record = repeated_record()
        for run in record["output_runs"]:
            if run["eval_id"] != target[0]:
                continue
            assertion = next(item for item in run["assertions"] if item["id"] == target[1])
            if run["configuration"] == "with_skill":
                assertion["passed"] = run["run"] <= 2
            else:
                assertion["passed"] = run["run"] == 1
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        improvements = scorecard["dimensions"]["output_quality"]["material_improvements"]
        target_improvements = [
            item for item in improvements
            if (item["eval_id"], item["assertion_id"]) == target
        ]
        self.assertEqual(len(target_improvements), 1)
        self.assertAlmostEqual(target_improvements[0]["candidate_pass_rate"], 2 / 3)
        self.assertAlmostEqual(target_improvements[0]["baseline_pass_rate"], 1 / 3)
        self.assertEqual(scorecard["dimensions"]["output_quality"]["run_counts"][target[0]], 3)

        record = repeated_record()
        for run in record["output_runs"]:
            if run["eval_id"] != target[0]:
                continue
            assertion = next(item for item in run["assertions"] if item["id"] == target[1])
            if run["configuration"] == "baseline":
                assertion["passed"] = run["run"] <= 2
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        improvements = scorecard["dimensions"]["output_quality"]["material_improvements"]
        self.assertFalse(
            any((item["eval_id"], item["assertion_id"]) == target for item in improvements)
        )

        record = repeated_record()
        for run in record["output_runs"]:
            if run["eval_id"] != target[0] or run["configuration"] != "with_skill":
                continue
            assertion = next(item for item in run["assertions"] if item["id"] == target[1])
            assertion["passed"] = run["run"] == 1
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        improvements = scorecard["dimensions"]["output_quality"]["material_improvements"]
        self.assertFalse(
            any((item["eval_id"], item["assertion_id"]) == target for item in improvements)
        )

    def test_independent_disposition_gates(self) -> None:
        cases = (
            (
                "verification-failed",
                lambda record: record["verification"][0].__setitem__("passed", False),
                "revise",
                "verification:failed",
            ),
            (
                "abuse-failed",
                lambda record: record["abuse"][0].__setitem__("passed", False),
                "revise",
                "abuse:failed",
            ),
            (
                "compatibility-failed",
                lambda record: record["compatibility"].__setitem__("status", "fail"),
                "revise",
                "compatibility:failed",
            ),
            (
                "compatibility-unobservable",
                lambda record: record["compatibility"].__setitem__("status", "not_observable"),
                "defer",
                "compatibility:not_observable",
            ),
            (
                "human-review-failed",
                lambda record: record["human_review"].__setitem__("status", "fail"),
                "revise",
                "human_review:failed",
            ),
            (
                "human-review-pending",
                lambda record: (
                    record["human_review"].__setitem__("status", "pending"),
                    record["human_review"].__setitem__("reviewer", None),
                    record["human_review"].__setitem__("date", None),
                ),
                "defer",
                "human_review:pending",
            ),
            (
                "rollback-failed",
                lambda record: record["rollback"].__setitem__("verified", False),
                "revise",
                "rollback:failed",
            ),
        )
        for label, mutate, expected_disposition, expected_reason in cases:
            with self.subTest(label=label):
                record = self._record()
                mutate(record)
                scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
                self.assertEqual(scorecard["recommended_disposition"], expected_disposition)
                self.assertIn(expected_reason, scorecard["blocking_reasons"])

    def test_record_contract_failures_are_rejected(self) -> None:
        mutations = [
            lambda record: record.__setitem__("schema_version", 2),
            lambda record: record["baseline"].__setitem__("kind", "unknown"),
            lambda record: record.pop("isolation_method"),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                record = self._record()
                mutate(record)
                with self.assertRaises(skill_effectiveness.EvaluationError):
                    skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_observability_contract_failures_are_rejected(self) -> None:
        record = self._record()
        record["output_observability"] = {"status": "observed", "reason": "unexpected"}
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

        record = self._record()
        record["abuse_observability"] = {"status": "not_observable", "reason": ""}
        record["abuse"] = []
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

        record = self._record()
        record["trigger"] = {
            "observability": "not_observable",
            "reason": "activation trace unavailable",
            "cases": record["trigger"]["cases"],
        }
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_duplicate_abuse_result_is_rejected(self) -> None:
        record = self._record()
        record["abuse"].append(copy.deepcopy(record["abuse"][0]))
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_invalid_telemetry_contract_is_rejected(self) -> None:
        record = self._record()
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(
                ROOT,
                self.skill_id,
                record,
                telemetry={"schema_version": 2, "groups": []},
            )

    def test_definition_documents_fail_closed_on_unknown_or_missing_fields(self) -> None:
        base = ROOT / "tests" / "skills" / self.skill_id
        raw_trigger = json.loads((base / "trigger-cases.json").read_text(encoding="utf-8"))
        raw_output = json.loads((base / "output-evals.json").read_text(encoding="utf-8"))
        raw_abuse = json.loads((base / "abuse-cases.json").read_text(encoding="utf-8"))

        def trigger_unknown(trigger, output, abuse):
            trigger[0]["unknown"] = True

        def trigger_missing(trigger, output, abuse):
            trigger[0].pop("id")

        def output_doc_unknown(trigger, output, abuse):
            output["unknown"] = True

        def output_eval_missing(trigger, output, abuse):
            output["evals"][0].pop("id")

        def output_assertion_unknown(trigger, output, abuse):
            output["evals"][0]["assertions"][0]["unknown"] = True

        def output_assertion_missing(trigger, output, abuse):
            output["evals"][0]["assertions"][0].pop("id")

        def abuse_doc_unknown(trigger, output, abuse):
            abuse["unknown"] = True

        def abuse_case_missing(trigger, output, abuse):
            abuse["cases"][0].pop("id")

        mutations = (
            trigger_unknown,
            trigger_missing,
            output_doc_unknown,
            output_eval_missing,
            output_assertion_unknown,
            output_assertion_missing,
            abuse_doc_unknown,
            abuse_case_missing,
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate.__name__):
                trigger = copy.deepcopy(raw_trigger)
                output = copy.deepcopy(raw_output)
                abuse = copy.deepcopy(raw_abuse)
                mutate(trigger, output, abuse)
                with self.assertRaises(skill_effectiveness.EvaluationError):
                    skill_effectiveness._validate_definition_documents(
                        self.skill_id, trigger, output, abuse
                    )

    def test_definition_revision_is_resolved_and_hashed(self) -> None:
        record = self._record()
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        provenance = scorecard["evaluation"]["definition_provenance"]
        self.assertEqual(provenance["revision"], record["eval_definition_revision"])
        paths = (
            "tests/skills/develop-code/trigger-cases.json",
            "tests/skills/develop-code/output-evals.json",
            "tests/skills/develop-code/abuse-cases.json",
        )
        expected_hashes = {}
        for path in paths:
            blob = subprocess.run(
                ["git", "-C", str(ROOT), "show", f"{record['eval_definition_revision']}:{path}"],
                capture_output=True,
                check=True,
            ).stdout
            expected_hashes[path] = hashlib.sha256(blob).hexdigest()
        self.assertEqual(provenance["sha256"], expected_hashes)

        record["eval_definition_revision"] = "f" * 40
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_asymmetric_output_run_sets_are_rejected(self) -> None:
        record = self._record()
        extra = copy.deepcopy(
            next(run for run in record["output_runs"] if run["configuration"] == "with_skill")
        )
        extra["run"] = 2
        record["output_runs"].append(extra)
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_skill_path_and_abbreviated_revision_are_rejected(self) -> None:
        record = self._record()
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, "../develop-code", record)

        record = self._record()
        record["eval_definition_revision"] = record["eval_definition_revision"][:12]
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_telemetry_unknown_fields_and_invalid_metrics_are_rejected(self) -> None:
        record = self._record()
        mutations = (
            ("unknown-field", lambda group: group.__setitem__("secret_payload", "must-not-propagate")),
            ("bad-skill-id", lambda group: group.__setitem__("skill_id", "bad id")),
            ("bad-project-id", lambda group: group.__setitem__("project_id", "bad id")),
            ("bad-content-hash", lambda group: group.__setitem__("content_sha256", "not-a-hash")),
            ("boolean-count", lambda group: group.__setitem__("loaded_count", True)),
            ("negative-count", lambda group: group.__setitem__("loaded_count", -1)),
            ("negative-sum", lambda group: group.__setitem__("total_duration_ms", -1)),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                group = self._telemetry_group(record)
                mutate(group)
                report = {
                    "schema_version": 1,
                    "event_count": 1,
                    "truncated": False,
                    "groups": [group],
                }
                with self.assertRaises(skill_effectiveness.EvaluationError):
                    skill_effectiveness.evaluate_record(
                        ROOT, self.skill_id, record, telemetry=report
                    )

        other_skill = self._telemetry_group(record)
        other_skill["skill_id"] = "other-skill"
        report = {
            "schema_version": 1,
            "event_count": 1,
            "truncated": False,
            "groups": [other_skill],
        }
        scorecard = skill_effectiveness.evaluate_record(
            ROOT, self.skill_id, record, telemetry=report
        )
        operational = scorecard["dimensions"]["operational_telemetry"]
        self.assertEqual(operational["groups"], [])
        self.assertEqual(operational["totals"]["loaded_count"], 0)

    def test_nullable_telemetry_aggregation_preserves_observability(self) -> None:
        record = self._record()
        unobserved = self._telemetry_group(record)
        unobserved["verification_passes"] = None
        report = {
            "schema_version": 1,
            "event_count": 1,
            "truncated": False,
            "groups": [unobserved],
        }
        scorecard = skill_effectiveness.evaluate_record(
            ROOT, self.skill_id, record, telemetry=report
        )
        operational = scorecard["dimensions"]["operational_telemetry"]
        self.assertIsNone(operational["totals"]["verification_passes"])
        self.assertEqual(
            operational["field_observability"]["verification_passes"]["status"],
            "not_observable",
        )

        observed = self._telemetry_group(record)
        observed["verification_passes"] = 1
        report["event_count"] = 2
        report["groups"] = [unobserved, observed]
        scorecard = skill_effectiveness.evaluate_record(
            ROOT, self.skill_id, record, telemetry=report
        )
        operational = scorecard["dimensions"]["operational_telemetry"]
        self.assertEqual(operational["totals"]["verification_passes"], 1)
        self.assertEqual(
            operational["field_observability"]["verification_passes"]["status"],
            "partial",
        )
        self.assertEqual(
            operational["field_observability"]["verification_passes"]["not_observable_groups"],
            1,
        )

    def test_pending_human_review_requires_null_identity_fields(self) -> None:
        record = self._record()
        record["human_review"]["status"] = "pending"
        record["human_review"]["reviewer"] = {"unexpected": "object"}
        record["human_review"]["date"] = None
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

        record = self._record()
        record["human_review"]["status"] = "pending"
        record["human_review"]["reviewer"] = None
        record["human_review"]["date"] = ["unexpected"]
        with self.assertRaises(skill_effectiveness.EvaluationError):
            skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)

    def test_production_regressions_become_fixture_candidates(self) -> None:
        record = self._record()
        record["production_regressions"] = [
            {
                "id": "reg-001",
                "summary": "Skill selected an unsafe absolute path during a real task.",
                "fixture_candidate": "Add a path-boundary abuse case covering this pattern.",
            }
        ]
        scorecard = skill_effectiveness.evaluate_record(ROOT, self.skill_id, record)
        self.assertEqual(
            scorecard["fixture_candidates"], record["production_regressions"]
        )

    def test_cli_writes_scorecard_json(self) -> None:
        record = self._record()
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "record.json"
            output = Path(tmp) / "scorecard.json"
            evidence.write_text(json.dumps(record), encoding="utf-8")
            exit_code = skill_effectiveness.main(
                [
                    "--repo",
                    str(ROOT),
                    "--skill",
                    self.skill_id,
                    "--record",
                    str(evidence),
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(exit_code, 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["recommended_disposition"], "admit")

    def test_cli_fails_closed_without_writing_scorecard(self) -> None:
        record = self._record()
        record["unexpected"] = True
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "record.json"
            output = Path(tmp) / "scorecard.json"
            evidence.write_text(json.dumps(record), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_effectiveness.main(
                    [
                        "--repo", str(ROOT),
                        "--skill", self.skill_id,
                        "--record", str(evidence),
                        "--output", str(output),
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("ERROR:", stderr.getvalue())
            self.assertFalse(output.exists())

    def test_cli_stdout_emits_complete_json(self) -> None:
        record = self._record()
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "record.json"
            evidence.write_text(json.dumps(record), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = skill_effectiveness.main(
                    ["--repo", str(ROOT), "--skill", self.skill_id, "--record", str(evidence)]
                )
            self.assertEqual(exit_code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["recommended_disposition"], "admit")
            self.assertEqual(result["skill_id"], self.skill_id)
            self.assertIn("definition_provenance", result["evaluation"])


if __name__ == "__main__":
    unittest.main()
