from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("develop-code", "develop-docs")
SOURCE_REVISION = "5ab2aa1e71852363b0a872e1d9a44f3c70298a42"

class DevelopWorkflowSkillTests(unittest.TestCase):
    def test_adoption_contracts_match_approved_workflow_scope(self) -> None:
        for name in SKILLS:
            skill_dir = ROOT / "skills" / name
            manifest = json.loads((skill_dir / "adoption-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("https://github.com/NielPieterse0/kis-mcp.git", manifest["source"]["repository"])
            self.assertEqual(SOURCE_REVISION, manifest["source"]["revision"])
            self.assertEqual(2, manifest["risk"]["tier"])
            self.assertEqual(["."], manifest["filesystem"]["write"])
            self.assertEqual("explicit", manifest["activation"]["mode"])
            self.assertTrue(manifest["activation"]["requires_human_approval"])
            self.assertFalse((skill_dir / "scripts").exists())

    def test_evaluation_definitions_cover_required_minimums(self) -> None:
        for name in SKILLS:
            test_dir = ROOT / "tests" / "skills" / name
            triggers = json.loads((test_dir / "trigger-cases.json").read_text(encoding="utf-8"))
            outputs = json.loads((test_dir / "output-evals.json").read_text(encoding="utf-8"))
            abuse = json.loads((test_dir / "abuse-cases.json").read_text(encoding="utf-8"))
            categories = [case["category"] for case in triggers]
            self.assertGreaterEqual(categories.count("positive"), 6)
            self.assertGreaterEqual(categories.count("near_miss"), 6)
            self.assertGreaterEqual(categories.count("conflict"), 2)
            self.assertGreaterEqual(categories.count("prompt_injection"), 2)
            self.assertGreaterEqual(len(outputs["evals"]), 3)
            self.assertTrue(any(assertion["critical"] for case in outputs["evals"] for assertion in case["assertions"]))
            self.assertGreaterEqual(len(abuse["cases"]), 8)

if __name__ == "__main__":
    unittest.main()
