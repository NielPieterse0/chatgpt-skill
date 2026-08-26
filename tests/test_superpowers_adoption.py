import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import skill_security


class SuperpowersAdoptionTests(unittest.TestCase):
    ALL_BUNDLE_SKILLS = {
        "brainstorming",
        "dispatching-parallel-agents",
        "executing-plans",
        "finishing-a-development-branch",
        "receiving-code-review",
        "requesting-code-review",
        "subagent-driven-development",
        "systematic-debugging",
        "test-driven-development",
        "using-git-worktrees",
        "using-superpowers",
        "verification-before-completion",
        "writing-plans",
        "writing-skills",
    }

    ADOPTED = ALL_BUNDLE_SKILLS

    REQUIRED_METHOD_CONCEPTS = {
        "brainstorming": ("approval", "trade-off", "design"),
        "dispatching-parallel-agents": ("independent", "bounded", "combined verification"),
        "executing-plans": ("plan defect", "task", "verification"),
        "finishing-a-development-branch": ("exact current head", "integration", "cleanup"),
        "receiving-code-review": ("verify", "push back", "scope"),
        "requesting-code-review": ("review scope", "independent", "re-review"),
        "subagent-driven-development": ("implementer", "requirements review", "quality review"),
        "systematic-debugging": ("root cause", "hypothesis", "three"),
        "test-driven-development": ("red", "green", "refactor"),
        "using-git-worktrees": ("existing isolation", "repository-authorized", "baseline"),
        "using-superpowers": ("relevant skill", "higher authority", "current skill"),
        "verification-before-completion": ("fresh", "claim", "evidence"),
        "writing-plans": ("requirements", "exact", "self-review"),
        "writing-skills": ("baseline", "red-green-refactor", "create-skill"),
    }

    def test_decisions_cover_bundle_and_adapted_skills_pass_security_gate(self) -> None:
        decision_path = ROOT / "portfolio/plugins/superpowers/evidence/adoption-decisions.json"
        decisions = json.loads(decision_path.read_text(encoding="utf-8"))

        entries = decisions["skills"]
        self.assertEqual({entry["skill"] for entry in entries}, self.ALL_BUNDLE_SKILLS)
        self.assertEqual(
            {entry["skill"] for entry in entries if entry["decision"] == "adapt"},
            self.ADOPTED,
        )
        self.assertEqual(
            {entry["skill"] for entry in entries if entry["decision"] != "adapt"},
            set(),
        )

        report = skill_security.validate_repository(ROOT, require_git=False)
        self.assertTrue(report.ok, [issue.to_dict() for issue in report.errors])
        admitted = {entry["name"] for entry in report.skills}
        self.assertTrue(self.ADOPTED.issubset(admitted))

    def test_adopted_packages_exclude_plugin_harness_and_executables(self) -> None:
        for skill in sorted(self.ADOPTED):
            skill_dir = ROOT / "skills" / skill
            self.assertTrue((skill_dir / "SKILL.md").is_file(), skill)
            self.assertTrue((skill_dir / "adoption-manifest.json").is_file(), skill)
            self.assertFalse((skill_dir / "agents").exists(), skill)
            self.assertFalse((skill_dir / "scripts").exists(), skill)
            forbidden_suffixes = {".sh", ".ps1", ".js", ".cjs", ".mjs", ".ts"}
            shipped = [
                path.relative_to(skill_dir).as_posix()
                for path in skill_dir.rglob("*")
                if path.is_file() and path.suffix.lower() in forbidden_suffixes
            ]
            self.assertEqual(shipped, [], skill)

    def test_each_adaptation_preserves_unique_method_and_higher_authority(self) -> None:
        for skill, concepts in self.REQUIRED_METHOD_CONCEPTS.items():
            body = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").lower()
            for concept in concepts:
                self.assertIn(concept, body, f"{skill} lost method concept: {concept}")
            self.assertIn("repository", body, f"{skill} must preserve repository authority")

        for skill in ("using-git-worktrees", "using-superpowers", "finishing-a-development-branch"):
            body = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").lower()
            self.assertIn("kis", body, f"{skill} must defer governed KIS behavior to live KIS authority")

    def test_evaluation_definitions_cover_each_adopted_skill(self) -> None:
        for skill in sorted(self.ADOPTED):
            root = ROOT / "tests" / "skills" / skill
            triggers = json.loads((root / "trigger-cases.json").read_text(encoding="utf-8"))
            outputs = json.loads((root / "output-evals.json").read_text(encoding="utf-8"))
            abuse = json.loads((root / "abuse-cases.json").read_text(encoding="utf-8"))
            self.assertEqual(len(triggers), 16, skill)
            self.assertGreaterEqual(sum(case["category"] == "positive" for case in triggers), 6, skill)
            self.assertGreaterEqual(sum(case["category"] == "near_miss" for case in triggers), 6, skill)
            self.assertGreaterEqual(sum(case["category"] == "conflict" for case in triggers), 2, skill)
            self.assertGreaterEqual(sum(case["category"] == "prompt_injection" for case in triggers), 2, skill)
            self.assertGreaterEqual(len(outputs["evals"]), 3, skill)
            self.assertGreaterEqual(len(abuse["cases"]), 8, skill)

        summary = json.loads((ROOT / "portfolio/plugins/superpowers/evidence/adoption-evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["decision"], "defer_behavioral_effectiveness")
        self.assertEqual({entry["skill"] for entry in summary["skills"]}, self.ADOPTED)


if __name__ == "__main__":
    unittest.main()
