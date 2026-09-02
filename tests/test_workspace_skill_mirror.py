from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "workspace_skill_mirror.py"
spec = importlib.util.spec_from_file_location("workspace_skill_mirror", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class WorkspaceSkillMirrorTests(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        skill = repo / "skills" / "demo" / "references"
        skill.mkdir(parents=True)
        (skill.parent / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
        (skill.parent / "adoption-manifest.json").write_text("{}\n", encoding="utf-8")
        (skill / "guide.md").write_text("depth\n", encoding="utf-8")
        return repo

    def test_refresh_projects_runtime_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            changed = module.refresh(repo)
            self.assertEqual(changed, ["demo"])
            mirror = repo / "workspace-skills" / "demo"
            self.assertTrue((mirror / "SKILL.md").is_file())
            self.assertTrue((mirror / "references" / "guide.md").is_file())
            self.assertFalse((mirror / "adoption-manifest.json").exists())

    def test_verify_detects_repo_owned_mirror_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            module.refresh(repo)
            (repo / "workspace-skills" / "demo" / "SKILL.md").write_text("drift\n", encoding="utf-8")
            self.assertEqual(module.verify_repo_mirror(repo), ["repo-owned mirror mismatch: demo"])


if __name__ == "__main__":
    unittest.main()
