from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skills_over_mcp_catalogue.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_skill(root: Path, name: str) -> Path:
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "scripts").mkdir()
    (skill / "assets").mkdir()
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Use this skill for catalogue projection tests.\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (skill / "scripts" / "check.py").write_text("print('ok')\n", encoding="utf-8")
    (skill / "assets" / "template.txt").write_text("template\n", encoding="utf-8")
    return skill


def load_module():
    if not SCRIPT.is_file():
        return None
    spec = importlib.util.spec_from_file_location("skills_over_mcp_catalogue", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillsOverMcpCatalogueTests(unittest.TestCase):
    def test_projects_complete_active_catalogue_deterministically(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "catalogue projector script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            alpha = make_skill(root, "alpha-skill")
            beta = make_skill(root, "beta-skill")
            first = module.build_catalogue_projection(root)
            second = module.build_catalogue_projection(root)
            self.assertEqual(first, second)
            self.assertEqual(first["catalogue"]["skill_count"], 2)
            self.assertEqual(first["catalogue"]["resource_count"], 8)
            self.assertRegex(first["catalogue"]["snapshot_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual([item["skill_id"] for item in first["skills"]], ["alpha-skill", "beta-skill"])
            for item, directory in ((first["skills"][0], alpha), (first["skills"][1], beta)):
                self.assertEqual(item["content_sha256"], sha(directory / "SKILL.md"))
                resources = item["skill_entry"]["resources"]
                self.assertEqual(len(resources), 4)
                for resource in resources:
                    relative = resource["uri"].split(f"skill://{item['skill_id']}/", 1)[1]
                    self.assertEqual(resource["digest"], f"sha256:{sha(directory / relative)}")
            self.assertTrue(first["checks"]["all_skills_projected"])
            self.assertFalse(first["checks"]["permission_grants_applied"])
            self.assertNotIn("root", first["catalogue"])

    def test_package_resource_change_changes_catalogue_snapshot(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "catalogue projector script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            skill = make_skill(root, "sample-skill")
            before = module.build_catalogue_projection(root)
            (skill / "references" / "guide.md").write_text("changed\n", encoding="utf-8")
            after = module.build_catalogue_projection(root)
        self.assertNotEqual(before["catalogue"]["snapshot_sha256"], after["catalogue"]["snapshot_sha256"])
    def test_fails_closed_when_catalogue_contains_unprojectable_entry(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "catalogue projector script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            make_skill(root, "good-skill")
            bad = root / "bad-skill"
            bad.mkdir()
            (bad / "README.md").write_text("missing SKILL.md\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "catalogue.*incomplete|missing SKILL.md"):
                module.build_catalogue_projection(root)

    def test_rejects_casefold_resource_uri_collision(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "catalogue projector script is missing")
        with self.assertRaisesRegex(ValueError, "resource URI collision"):
            module._require_unique_resource_uris(
                [
                    "skill://sample-skill/assets/A.txt",
                    "skill://sample-skill/assets/a.txt",
                ]
            )

    def test_runtime_snapshot_is_provenance_not_content_identity(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "catalogue projector script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            make_skill(root, "sample-skill")
            without_runtime = module.build_catalogue_projection(root)
            with_runtime = module.build_catalogue_projection(
                root, source_snapshot_id="runtime-snapshot-1"
            )
        self.assertEqual(with_runtime["catalogue"]["source_snapshot_id"], "runtime-snapshot-1")
        self.assertEqual(
            without_runtime["catalogue"]["snapshot_sha256"],
            with_runtime["catalogue"]["snapshot_sha256"],
        )

    def test_cli_writes_bounded_catalogue_manifest(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "catalogue projector script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            make_skill(root, "sample-skill")
            output = Path(tmp) / "projection.json"
            exit_code = module.main(["--catalog-root", str(root), "--output", str(output)])
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["catalogue"]["skill_count"], 1)
        self.assertEqual(payload["skills"][0]["skill_id"], "sample-skill")

    @unittest.skipUnless(os.name == "nt", "junction test is Windows-specific")
    def test_rejects_internal_junction(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "catalogue projector script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            skill = make_skill(root, "sample-skill")
            external = Path(tmp) / "external"
            external.mkdir()
            (external / "hidden.txt").write_text("outside\n", encoding="utf-8")
            linked = skill / "references" / "linked"
            created = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(linked), str(external)],
                text=True, capture_output=True, check=False,
            )
            if created.returncode != 0:
                self.skipTest(created.stderr or created.stdout)
            with self.assertRaisesRegex(ValueError, "linked|reparse"):
                module.build_catalogue_projection(root)


if __name__ == "__main__":
    unittest.main()
