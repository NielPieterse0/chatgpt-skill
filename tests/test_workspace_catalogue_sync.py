from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.sync_workspace_catalogue import SyncError, sync_catalogue


class WorkspaceCatalogueSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.catalogue = self.root / "catalogue"
        self.repo.mkdir()
        self.catalogue.mkdir()
        self._git("init", "-b", "main")
        self._git("config", "user.email", "tests@example.invalid")
        self._git("config", "user.name", "Test User")
        self._git("remote", "add", "origin", "https://github.com/example/chatgpt-skill.git")
        (self.repo / "skills").mkdir()
        (self.repo / "README.md").write_text("test\n", encoding="utf-8")
        self._commit("initial")
        self._accept_main()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def _commit(self, message: str) -> str:
        self._git("add", "-A")
        self._git("commit", "-m", message)
        return self._git("rev-parse", "HEAD")

    def _accept_main(self) -> str:
        commit = self._git("rev-parse", "HEAD")
        self._git("update-ref", "refs/remotes/origin/main", commit)
        return commit

    def _write_skill(self, name: str, marker: str) -> None:
        skill = self.repo / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill.\n---\n\n# {name}\n\n{marker}\n",
            encoding="utf-8",
        )
        (skill / "adoption-manifest.json").write_text(
            json.dumps({"skill": name, "marker": marker}, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_new_skill_is_created_from_accepted_main(self) -> None:
        self._write_skill("new-skill", "v1")
        accepted = self._commit("add skill")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue)

        self.assertTrue(result["ok"])
        self.assertEqual(accepted, result["source_commit"])
        self.assertEqual("create", result["skills"][0]["action"])
        self.assertIn("v1", (self.catalogue / "new-skill" / "SKILL.md").read_text(encoding="utf-8"))

    def test_second_run_is_idempotent(self) -> None:
        self._write_skill("stable-skill", "v1")
        self._commit("add skill")
        self._accept_main()
        sync_catalogue(self.repo, self.catalogue)

        result = sync_catalogue(self.repo, self.catalogue, skills=["stable-skill"])

        self.assertTrue(result["ok"])
        self.assertEqual("unchanged", result["skills"][0]["action"])

    def test_safe_update_requires_catalogue_to_match_previous_main(self) -> None:
        self._write_skill("updated-skill", "v1")
        self._commit("add skill")
        self._accept_main()
        sync_catalogue(self.repo, self.catalogue)
        self._write_skill("updated-skill", "v2")
        self._commit("update skill")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue)

        self.assertTrue(result["ok"])
        self.assertEqual("update", result["skills"][0]["action"])
        self.assertIn("v2", (self.catalogue / "updated-skill" / "SKILL.md").read_text(encoding="utf-8"))

    def test_diverged_catalogue_blocks_update_without_overwrite(self) -> None:
        self._write_skill("conflict-skill", "v1")
        self._commit("add skill")
        self._accept_main()
        sync_catalogue(self.repo, self.catalogue)
        skill_file = self.catalogue / "conflict-skill" / "SKILL.md"
        skill_file.write_text(skill_file.read_text(encoding="utf-8") + "local drift\n", encoding="utf-8")
        self._write_skill("conflict-skill", "v2")
        self._commit("update skill")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue)

        self.assertFalse(result["ok"])
        self.assertEqual("blocked", result["skills"][0]["action"])
        self.assertIn("local drift", skill_file.read_text(encoding="utf-8"))
        self.assertNotIn("v2", skill_file.read_text(encoding="utf-8"))

    def test_repository_deletion_never_deletes_catalogue_automatically(self) -> None:
        self._write_skill("retired-skill", "v1")
        self._commit("add skill")
        self._accept_main()
        sync_catalogue(self.repo, self.catalogue)
        for child in (self.repo / "skills" / "retired-skill").iterdir():
            child.unlink()
        (self.repo / "skills" / "retired-skill").rmdir()
        self._commit("remove skill")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue)

        self.assertFalse(result["ok"])
        self.assertEqual("blocked", result["skills"][0]["action"])
        self.assertTrue((self.catalogue / "retired-skill" / "SKILL.md").is_file())

    def test_non_accepted_branch_state_is_rejected(self) -> None:
        self._write_skill("branch-only", "v1")
        self._commit("branch-only skill")

        with self.assertRaises(SyncError):
            sync_catalogue(self.repo, self.catalogue, source_ref="HEAD", skills=["branch-only"])

    def test_dry_run_does_not_write(self) -> None:
        self._write_skill("dry-run-skill", "v1")
        self._commit("add skill")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue, dry_run=True)

        self.assertTrue(result["ok"])
        self.assertTrue(result["dry_run"])
        self.assertFalse((self.catalogue / "dry-run-skill").exists())

    def test_multi_skill_preflight_blocks_all_writes_on_one_conflict(self) -> None:
        self._write_skill("first-skill", "v1")
        self._write_skill("second-skill", "v1")
        self._commit("add skills")
        self._accept_main()
        sync_catalogue(self.repo, self.catalogue)
        drifted = self.catalogue / "second-skill" / "SKILL.md"
        drifted.write_text(drifted.read_text(encoding="utf-8") + "catalogue drift\n", encoding="utf-8")
        self._write_skill("first-skill", "v2")
        self._write_skill("second-skill", "v2")
        self._commit("update skills")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue)

        self.assertFalse(result["ok"])
        self.assertIn("v1", (self.catalogue / "first-skill" / "SKILL.md").read_text(encoding="utf-8"))
        self.assertNotIn("v2", (self.catalogue / "first-skill" / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("catalogue drift", drifted.read_text(encoding="utf-8"))

    def test_runtime_catalogue_excludes_repository_only_manifest(self) -> None:
        self._write_skill("runtime-only-skill", "v1")
        refs = self.repo / "skills" / "runtime-only-skill" / "references"
        refs.mkdir()
        (refs / "guide.md").write_text("runtime guide\n", encoding="utf-8")
        self._commit("add runtime-only skill")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue)

        self.assertTrue(result["ok"])
        published = self.catalogue / "runtime-only-skill"
        self.assertTrue((published / "SKILL.md").is_file())
        self.assertTrue((published / "references" / "guide.md").is_file())
        self.assertFalse((published / "adoption-manifest.json").exists())

    def test_update_accepts_previous_runtime_projection_without_manifest(self) -> None:
        self._write_skill("projected-skill", "v1")
        first = self._commit("add projected skill")
        self._accept_main()
        skill_root = self.repo / "skills" / "projected-skill"
        catalogue_root = self.catalogue / "projected-skill"
        catalogue_root.mkdir()
        (catalogue_root / "SKILL.md").write_bytes(
            subprocess.run(
                ["git", "-C", str(self.repo), "show", f"{first}:skills/projected-skill/SKILL.md"],
                check=True,
                capture_output=True,
            ).stdout
        )
        self._write_skill("projected-skill", "v2")
        self._commit("update projected skill")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue)

        self.assertTrue(result["ok"])
        self.assertEqual("update", result["skills"][0]["action"])
        self.assertIn("v2", (catalogue_root / "SKILL.md").read_text(encoding="utf-8"))
        self.assertFalse((catalogue_root / "adoption-manifest.json").exists())

    def test_delayed_retry_uses_last_accepted_skill_version_as_baseline(self) -> None:
        self._write_skill("delayed-skill", "v1")
        self._commit("add delayed skill")
        self._accept_main()
        sync_catalogue(self.repo, self.catalogue)

        self._write_skill("delayed-skill", "v2")
        self._commit("update delayed skill")
        self._accept_main()
        (self.repo / "README.md").write_text("unrelated accepted change\n", encoding="utf-8")
        self._commit("unrelated change")
        self._accept_main()

        result = sync_catalogue(self.repo, self.catalogue, skills=["delayed-skill"])

        self.assertTrue(result["ok"])
        self.assertEqual("update", result["skills"][0]["action"])
        self.assertIn("v2", (self.catalogue / "delayed-skill" / "SKILL.md").read_text(encoding="utf-8"))

    def test_post_merge_hook_surfaces_publication_failure(self) -> None:
        scripts = self.repo / "scripts"
        scripts.mkdir()
        (scripts / "workspace_skill_mirror.py").write_text(
            "import sys\nprint('simulated sync failure')\nraise SystemExit(7)\n",
            encoding="utf-8",
        )
        hook = Path(__file__).resolve().parents[1] / ".githooks" / "post-merge"
        hooks = self.repo / ".githooks"
        hooks.mkdir()
        test_hook = hooks / "post-merge"
        test_hook.write_bytes(hook.read_bytes())
        test_hook.chmod(0o755)
        self._git("config", "core.hooksPath", ".githooks")

        command = (
            ["git", "-C", str(self.repo), "hook", "run", "post-merge"]
            if sys.platform == "win32"
            else [sys.executable, str(test_hook)]
        )
        completed = subprocess.run(
            command,
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(7, completed.returncode)
        self.assertIn("workspace skill synchronization failed", completed.stderr)


if __name__ == "__main__":
    unittest.main()
