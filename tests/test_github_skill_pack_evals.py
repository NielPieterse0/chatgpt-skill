from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("github", "github-pr-maintenance", "github-delivery")


class GithubSkillPackEvaluationTests(unittest.TestCase):
    def test_evaluation_definitions_cover_required_minimums(self) -> None:
        for name in SKILLS:
            test_dir = ROOT / "tests" / "skills" / name
            triggers = json.loads((test_dir / "trigger-cases.json").read_text(encoding="utf-8"))
            outputs = json.loads((test_dir / "output-evals.json").read_text(encoding="utf-8"))
            abuse = json.loads((test_dir / "abuse-cases.json").read_text(encoding="utf-8"))

            categories = [case["category"] for case in triggers]
            self.assertGreaterEqual(categories.count("positive"), 6, name)
            self.assertGreaterEqual(categories.count("near_miss"), 6, name)
            self.assertGreaterEqual(categories.count("conflict"), 2, name)
            self.assertGreaterEqual(categories.count("prompt_injection"), 2, name)
            self.assertGreaterEqual(len(outputs["evals"]), 3, name)
            self.assertTrue(
                any(assertion["critical"] for case in outputs["evals"] for assertion in case["assertions"]),
                name,
            )
            self.assertGreaterEqual(len(abuse["cases"]), 8, name)

    def test_operational_pack_is_not_repository_runtime_admitted(self) -> None:
        for name in SKILLS:
            self.assertFalse((ROOT / "skills" / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
