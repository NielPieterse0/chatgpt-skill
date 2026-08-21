from __future__ import annotations

import copy
import hashlib
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("trigger_optimization", SCRIPTS / "trigger_optimization.py")
assert SPEC and SPEC.loader
trigger_optimization = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trigger_optimization)
import skill_effectiveness


class TriggerOptimizationTests(unittest.TestCase):
    skill_id = "develop-code"

    def _result(self, case: dict) -> dict:
        return {
            "id": case["id"],
            "triggers": 3 if case["expected"] == "trigger" else 0,
            "runs": 3,
        }

    def _record(self) -> dict:
        definitions = skill_effectiveness.load_definitions(ROOT, self.skill_id)["trigger"]
        train = [case for case in definitions if case["split"] == "train"]
        validation = [case for case in definitions if case["split"] == "validation"]
        revision = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        return {
            "schema_version": 1,
            "skill_id": self.skill_id,
            "definition_revision": revision,
            "selected_iteration_id": "iteration-2",
            "iterations": [
                {
                    "id": "iteration-1",
                    "description": "Description one",
                    "description_sha256": hashlib.sha256(b"Description one").hexdigest(),
                    "train_results": [self._result(case) for case in train],
                },
                {
                    "id": "iteration-2",
                    "description": "Description two",
                    "description_sha256": hashlib.sha256(b"Description two").hexdigest(),
                    "train_results": [self._result(case) for case in train],
                },
            ],
            "validation": [
                {
                    "iteration_id": "iteration-1",
                    "results": [self._result(case) for case in validation],
                },
                {
                    "iteration_id": "iteration-2",
                    "results": [self._result(case) for case in validation],
                },
            ],
            "fresh_sanity": [
                {
                    "id": "fresh-001",
                    "query": "Implement the bounded parser fix and verify its tests.",
                    "expected": "trigger",
                    "rationale": "Fresh implementation case.",
                    "triggers": 3,
                    "runs": 3,
                },
                {
                    "id": "fresh-002",
                    "query": "Finish the approved cache invalidation code change.",
                    "expected": "trigger",
                    "rationale": "Fresh implementation case.",
                    "triggers": 2,
                    "runs": 3,
                },
                {
                    "id": "fresh-003",
                    "query": "Explain this parser bug without editing any files.",
                    "expected": "do_not_trigger",
                    "rationale": "Fresh read-only near miss.",
                    "triggers": 0,
                    "runs": 3,
                },
                {
                    "id": "fresh-004",
                    "query": "Review this cache change but do not modify it.",
                    "expected": "do_not_trigger",
                    "rationale": "Fresh review near miss.",
                    "triggers": 1,
                    "runs": 3,
                },
            ],
        }

    def test_valid_record_preserves_train_validation_and_fresh_cohorts(self) -> None:
        record = self._record()
        result = trigger_optimization.validate_record(ROOT, self.skill_id, record)
        self.assertEqual(result["selected_iteration_id"], "iteration-2")
        self.assertEqual(result["selected_description"], "Description two")
        self.assertEqual(result["iteration_count"], 2)
        self.assertEqual(len(result["validation_iterations"]), 2)
        self.assertEqual(result["train"]["total"], 10)
        self.assertEqual(result["validation"]["total"], 6)
        self.assertEqual(result["fresh_sanity"]["total"], 4)
        self.assertEqual(result["train"]["pass_rate"], 1.0)
        self.assertEqual(result["validation"]["pass_rate"], 1.0)
        self.assertEqual(result["fresh_sanity"]["pass_rate"], 1.0)

    def test_train_results_cannot_include_validation_ids(self) -> None:
        record = self._record()
        validation_id = record["validation"][0]["results"][0]["id"]
        record["iterations"][0]["train_results"][0]["id"] = validation_id
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

    def test_validation_must_cover_every_iteration(self) -> None:
        record = self._record()
        record["validation"].pop()
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

    def test_selected_iteration_must_have_best_validation_pass_rate(self) -> None:
        record = self._record()
        record["validation"][0]["results"][0]["triggers"] = 0
        trigger_optimization.validate_record(ROOT, self.skill_id, record)
        record["selected_iteration_id"] = "iteration-1"
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

    def test_iteration_description_hash_must_match_reviewable_text(self) -> None:
        record = self._record()
        record["iterations"][0]["description"] = "Changed without updating the hash"
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

    def test_iteration_description_must_be_releasable_text(self) -> None:
        record = self._record()
        record["iterations"][0]["description"] = " " + record["iterations"][0]["description"]
        record["iterations"][0]["description_sha256"] = hashlib.sha256(
            record["iterations"][0]["description"].encode("utf-8")
        ).hexdigest()
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

        record = self._record()
        record["iterations"][0]["description"] = "x" * 1025
        record["iterations"][0]["description_sha256"] = hashlib.sha256(
            record["iterations"][0]["description"].encode("utf-8")
        ).hexdigest()
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

    def test_fresh_sanity_rejects_tracked_or_duplicate_queries(self) -> None:
        record = self._record()
        tracked = skill_effectiveness.load_definitions(ROOT, self.skill_id)["trigger"][0]["query"]
        record["fresh_sanity"][0]["query"] = tracked
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

        record = self._record()
        record["fresh_sanity"][1]["query"] = record["fresh_sanity"][0]["query"]
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

    def test_fresh_sanity_requires_balanced_positive_and_negative_cases(self) -> None:
        record = self._record()
        for case in record["fresh_sanity"]:
            case["expected"] = "trigger"
            case["triggers"] = 3
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

    def test_unknown_fields_and_missing_iterations_fail_closed(self) -> None:
        record = self._record()
        record["unexpected"] = True
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)

        record = self._record()
        record["iterations"] = []
        with self.assertRaises(trigger_optimization.OptimizationError):
            trigger_optimization.validate_record(ROOT, self.skill_id, record)


if __name__ == "__main__":
    unittest.main()
