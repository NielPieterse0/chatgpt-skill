from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_lifecycle.py"
spec = importlib.util.spec_from_file_location("skill_lifecycle", SCRIPT)
assert spec and spec.loader
skill_lifecycle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_lifecycle)


class SkillLifecycleContractTests(unittest.TestCase):
    def _write_skill(self, root: Path, skill_id: str, terms: list[str]) -> None:
        directory = root / skill_id
        directory.mkdir(parents=True)
        description = f"Use when governing {skill_id} work."
        body = "\n".join(["# Skill", "Governing authority applies.", *terms])
        (directory / "SKILL.md").write_text(
            f"---\nname: {skill_id}\ndescription: {description}\n---\n\n{body}\n",
            encoding="utf-8",
        )

    def _valid_catalog(self, root: Path) -> None:
        contract = skill_lifecycle.load_contract(ROOT)
        common_terms = contract["common"]["required_authority_terms"]
        for skill_id, rules in contract["skills"].items():
            self._write_skill(root, skill_id, common_terms + rules["required_terms"])

    def test_valid_catalog_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._valid_catalog(root)
            self.assertEqual(skill_lifecycle.validate_catalog(ROOT, root), [])

    def test_missing_required_term_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._valid_catalog(root)
            path = root / "evaluate-skill" / "SKILL.md"
            text = path.read_text(encoding="utf-8").replace("held-out", "removed")
            path.write_text(text, encoding="utf-8")
            errors = skill_lifecycle.validate_catalog(ROOT, root)
            self.assertTrue(any("held-out" in error for error in errors))

    def test_prohibited_frontmatter_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._valid_catalog(root)
            path = root / "create-skill" / "SKILL.md"
            text = path.read_text(encoding="utf-8").replace(
                "description:", "allowed-tools: Bash\ndescription:", 1
            )
            path.write_text(text, encoding="utf-8")
            errors = skill_lifecycle.validate_catalog(ROOT, root)
            self.assertTrue(any("allowed-tools" in error for error in errors))

    def test_mandatory_optional_tool_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._valid_catalog(root)
            path = root / "improve-skill" / "SKILL.md"
            text = path.read_text(encoding="utf-8") + "plugin-eval analyze <skill-path>\n"
            path.write_text(text, encoding="utf-8")
            errors = skill_lifecycle.validate_catalog(ROOT, root)
            self.assertTrue(any("optional-tool command" in error for error in errors))

    def test_missing_skill_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._valid_catalog(root)
            (root / "improve-skill" / "SKILL.md").unlink()
            errors = skill_lifecycle.validate_catalog(ROOT, root)
            self.assertIn("improve-skill: missing SKILL.md", errors)


if __name__ == "__main__":
    unittest.main()
