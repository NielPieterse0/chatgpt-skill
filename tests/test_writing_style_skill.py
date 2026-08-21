from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "writing-style"
EVAL_DIR = ROOT / "tests" / "skills" / "writing-style"


class WritingStyleSkillTests(unittest.TestCase):
    def test_adoption_contract_is_instruction_only(self) -> None:
        manifest = json.loads((SKILL_DIR / "adoption-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("writing-style", manifest["skill"])
        self.assertEqual("https://github.com/NielPieterse0/chatgpt-skill.git", manifest["source"]["repository"])
        self.assertEqual("trusted-local", manifest["source"]["provenance_type"])
        self.assertEqual(0, manifest["risk"]["tier"])
        self.assertEqual([], manifest["filesystem"]["read"])
        self.assertEqual([], manifest["filesystem"]["write"])
        self.assertEqual("model", manifest["activation"]["mode"])
        self.assertFalse(manifest["activation"]["requires_human_approval"])
        self.assertFalse((SKILL_DIR / "scripts").exists())

    def test_agents_requires_progressive_writing_style(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Apply `writing-style` to all LLM-written output", agents)
        self.assertIn(r"C:\Projects\References\google-developer-style-guide\000-index.md", agents)
        self.assertIn("read only the relevant page or pages", agents)

    def test_evaluation_definitions_cover_required_outputs(self) -> None:
        triggers = json.loads((EVAL_DIR / "trigger-cases.json").read_text(encoding="utf-8"))
        outputs = json.loads((EVAL_DIR / "output-evals.json").read_text(encoding="utf-8"))
        abuse = json.loads((EVAL_DIR / "abuse-cases.json").read_text(encoding="utf-8"))
        for case in triggers:
            self.assertEqual(
                {"id", "query", "expected", "category", "rationale", "split"},
                set(case),
            )
            self.assertTrue(all(isinstance(case[key], str) and case[key] for key in case))
        categories = [case["category"] for case in triggers]
        self.assertGreaterEqual(categories.count("positive"), 6)
        self.assertGreaterEqual(categories.count("near_miss"), 6)
        self.assertGreaterEqual(categories.count("conflict"), 2)
        self.assertGreaterEqual(categories.count("prompt_injection"), 2)
        self.assertEqual({"train", "validation"}, {case["split"] for case in triggers})
        self.assertEqual("writing-style", outputs["skill_name"])
        self.assertEqual("no-skill", outputs["baseline"])
        self.assertGreaterEqual(len(outputs["evals"]), 4)
        for case in outputs["evals"]:
            self.assertEqual(
                {"id", "prompt", "expected_outcome", "assertions", "human_review"},
                set(case),
            )
            self.assertTrue(case["id"] and case["prompt"] and case["expected_outcome"])
            self.assertTrue(case["assertions"])
            for assertion in case["assertions"]:
                self.assertEqual({"id", "text", "critical", "method"}, set(assertion))
                self.assertIsInstance(assertion["critical"], bool)
        prompts = " ".join(case["prompt"].lower() for case in outputs["evals"])
        for required in ("plan", "project-board", "issue comment", "repository documentation"):
            self.assertIn(required, prompts)
        self.assertEqual("writing-style", abuse["skill_name"])
        self.assertGreaterEqual(len(abuse["cases"]), 8)
        for case in abuse["cases"]:
            self.assertEqual({"id", "scenario", "expected"}, set(case))
            self.assertTrue(all(isinstance(case[key], str) and case[key] for key in case))


if __name__ == "__main__":
    unittest.main()
