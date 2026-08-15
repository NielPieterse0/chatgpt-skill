from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skills_over_mcp_compat.py"
spec = importlib.util.spec_from_file_location("skills_over_mcp_compat", SCRIPT)
assert spec and spec.loader
skills_over_mcp_compat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skills_over_mcp_compat)


class SkillsOverMcpCompatibilityTests(unittest.TestCase):
    def _skill(self, root: Path, *, allowed_tools: bool = False) -> Path:
        skill = root / "sample-skill"
        (skill / "references").mkdir(parents=True)
        (skill / "scripts").mkdir()
        (skill / "assets").mkdir()
        allowed = "allowed-tools: Bash(git:*)\n" if allowed_tools else ""
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            "description: Use this skill for compatibility testing.\n"
            f"{allowed}"
            "metadata:\n"
            "  version: \"1.2.3\"\n"
            "---\n\n"
            "# Sample\n\nRead references/guide.md when needed.\n",
            encoding="utf-8",
        )
        (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        (skill / "scripts" / "check.py").write_text("print('ok')\n", encoding="utf-8")
        (skill / "assets" / "template.txt").write_text("template\n", encoding="utf-8")
        return skill

    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_projects_complete_draft_sep_resource_set_without_granting_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), allowed_tools=True)
            entrypoint_sha = self._sha(skill / "SKILL.md")
            guide_sha = self._sha(skill / "references" / "guide.md")

            result = skills_over_mcp_compat.build_projection(
                skill,
                expected_skill_id="sample-skill",
                expected_entrypoint_sha256=entrypoint_sha,
                expected_file_count=4,
                expected_snapshot_id="snapshot-1",
                expected_resource_hashes={"references/guide.md": guide_sha},
            )

            self.assertEqual(result["schema_version"], 1)
            self.assertEqual(result["status"], "experimental")
            self.assertEqual(result["sep"], "SEP-2640-draft")
            self.assertEqual(result["source"]["authority"], "kis")
            self.assertEqual(result["source"]["snapshot_id"], "snapshot-1")
            self.assertEqual(result["source"]["entrypoint_sha256"], entrypoint_sha)
            self.assertEqual(result["source"]["file_count"], 4)
            entry = result["skill_entry"]
            self.assertEqual(entry["uri"], "skill://sample-skill/SKILL.md")
            self.assertEqual(entry["frontmatter"]["name"], "sample-skill")
            self.assertEqual(entry["frontmatter"]["metadata"]["version"], "1.2.3")
            self.assertEqual(entry["frontmatter"]["allowed-tools"], "Bash(git:*)")
            resource_list = entry["resources"]
            self.assertEqual(
                resource_list, sorted(resource_list, key=lambda item: item["uri"].casefold())
            )
            for item in resource_list:
                self.assertTrue(item["uri"].startswith("skill://sample-skill/"))
                self.assertTrue(item["digest"].startswith("sha256:"))
                digest = item["digest"].removeprefix("sha256:")
                self.assertEqual(len(digest), 64)
                self.assertTrue(all(character in "0123456789abcdef" for character in digest))
            resources = {item["uri"]: item["digest"] for item in resource_list}
            self.assertEqual(
                set(resources),
                {
                    "skill://sample-skill/SKILL.md",
                    "skill://sample-skill/references/guide.md",
                    "skill://sample-skill/scripts/check.py",
                    "skill://sample-skill/assets/template.txt",
                },
            )
            self.assertEqual(resources["skill://sample-skill/SKILL.md"], f"sha256:{entrypoint_sha}")
            checks = result["checks"]
            self.assertTrue(checks["skill_id_match"])
            self.assertTrue(checks["entrypoint_sha256_match"])
            self.assertTrue(checks["file_count_match"])
            self.assertTrue(checks["all_identity_checks_passed"])
            self.assertEqual(
                checks["verified_resources"],
                [{"path": "references/guide.md", "sha256": guide_sha, "matched": True}],
            )
            self.assertFalse(checks["permission_grants_applied"])

    def test_rejects_kis_entrypoint_identity_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp))
            with self.assertRaisesRegex(ValueError, "entrypoint SHA-256"):
                skills_over_mcp_compat.build_projection(
                    skill,
                    expected_skill_id="sample-skill",
                    expected_entrypoint_sha256="0" * 64,
                    expected_file_count=4,
                )

    def test_rejects_kis_file_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp))
            with self.assertRaisesRegex(ValueError, "file count"):
                skills_over_mcp_compat.build_projection(
                    skill,
                    expected_skill_id="sample-skill",
                    expected_entrypoint_sha256=self._sha(skill / "SKILL.md"),
                    expected_file_count=99,
                )

    def test_rejects_supporting_resource_digest_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp))
            with self.assertRaisesRegex(ValueError, "resource SHA-256"):
                skills_over_mcp_compat.build_projection(
                    skill,
                    expected_skill_id="sample-skill",
                    expected_entrypoint_sha256=self._sha(skill / "SKILL.md"),
                    expected_file_count=4,
                    expected_resource_hashes={"references/guide.md": "f" * 64},
                )

    def test_cli_emits_json_evidence_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = self._skill(root)
            output = root / "projection.json"
            exit_code = skills_over_mcp_compat.main(
                [
                    "--skill-dir",
                    str(skill),
                    "--skill-id",
                    "sample-skill",
                    "--entrypoint-sha256",
                    self._sha(skill / "SKILL.md"),
                    "--file-count",
                    "4",
                    "--snapshot-id",
                    "snapshot-2",
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(exit_code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["source"]["snapshot_id"], "snapshot-2")
            self.assertEqual(len(payload["skill_entry"]["resources"]), 4)

    def test_rejects_nonexistent_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-skill"
            with self.assertRaisesRegex(ValueError, "skill directory does not exist"):
                skills_over_mcp_compat.build_projection(
                    missing,
                    expected_skill_id="sample-skill",
                    expected_entrypoint_sha256="0" * 64,
                    expected_file_count=1,
                )

    def test_rejects_directory_without_skill_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "sample-skill"
            skill.mkdir()
            (skill / "reference.txt").write_text("reference\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "skill does not contain SKILL.md"):
                skills_over_mcp_compat.build_projection(
                    skill,
                    expected_skill_id="sample-skill",
                    expected_entrypoint_sha256="0" * 64,
                    expected_file_count=1,
                )

    @unittest.skipIf(os.name == "nt", "Windows symlink creation may require developer privileges")
    def test_rejects_linked_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = self._skill(root / "target")
            linked = root / "sample-skill"
            linked.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "skill directory must not be a linked path"):
                skills_over_mcp_compat.build_projection(
                    linked,
                    expected_skill_id="sample-skill",
                    expected_entrypoint_sha256=self._sha(target / "SKILL.md"),
                    expected_file_count=4,
                )

    @unittest.skipIf(os.name == "nt", "Windows symlink creation may require developer privileges")
    def test_rejects_linked_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = self._skill(root)
            target = root / "outside.txt"
            target.write_text("outside\n", encoding="utf-8")
            (skill / "references" / "linked.txt").symlink_to(target)
            with self.assertRaisesRegex(ValueError, "linked path"):
                skills_over_mcp_compat.build_projection(
                    skill,
                    expected_skill_id="sample-skill",
                    expected_entrypoint_sha256=self._sha(skill / "SKILL.md"),
                    expected_file_count=5,
                )


if __name__ == "__main__":
    unittest.main()
