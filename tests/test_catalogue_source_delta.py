from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "catalogue_source_delta.py"


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def commit_all(repo: Path, message: str) -> str:
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", message)
    return run_git(repo, "rev-parse", "HEAD")


def make_source_repo(root: Path, url: str) -> tuple[Path, str]:
    repo = root / "source"
    repo.mkdir()
    run_git(repo, "init")
    run_git(repo, "config", "user.email", "tests@example.com")
    run_git(repo, "config", "user.name", "Tests")
    run_git(repo, "remote", "add", "origin", url)
    skill = repo / ".agents" / "skills" / "sample-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: source\n---\n\n# Sample\n",
        encoding="utf-8",
    )
    baseline = commit_all(repo, "baseline")
    return repo, baseline


def tree_hash(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        (p for p in skill_dir.rglob("*") if p.is_file()),
        key=lambda p: (p.relative_to(skill_dir).as_posix().casefold(), p.as_posix()),
    ):
        relative = path.relative_to(skill_dir).as_posix()
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode())
        digest.update(b"\n")
    return digest.hexdigest()


def adopted_hash(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    files = [p for p in skill_dir.rglob("*") if p.is_file() and p.name != "adoption-manifest.json"]
    for path in sorted(files, key=lambda p: p.relative_to(skill_dir).as_posix()):
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8")
        content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def make_adopted_repo(root: Path, source_url: str, revision: str) -> Path:
    repo = root / "adopted"
    skill = repo / "skills" / "sample-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: adopted\n---\n\n# Adopted\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": 2,
        "skill": "sample-skill",
        "source": {
            "repository": source_url,
            "revision": revision,
            "imported_at": "2026-08-16",
            "provenance_type": "trusted-local",
            "handoff": None,
            "adopted_content_sha256": adopted_hash(skill),
        },
    }
    (skill / "adoption-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return repo


def load_module():
    if not SCRIPT.is_file():
        return None
    spec = importlib.util.spec_from_file_location("catalogue_source_delta", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatalogueSourceDeltaTests(unittest.TestCase):
    def test_modified_source_package_is_due_with_exact_delta(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            source_skill = source / ".agents" / "skills" / "sample-skill"
            (source_skill / "references").mkdir()
            (source_skill / "references" / "guide.md").write_text("changed\n", encoding="utf-8")
            current = commit_all(source, "change skill")
            report = module.build_report(adopted, {url: source})
        item = report["skills"][0]
        self.assertEqual(item["status"], "source_changed")
        self.assertEqual(item["reviewed_revision"], baseline)
        self.assertEqual(item["current_revision"], current)
        self.assertEqual(item["changed_paths"], [".agents/skills/sample-skill/references/guide.md"])
        self.assertTrue(item["disposition_required"])
        self.assertIn("security", item["required_rechecks"])

    def test_unrelated_repository_advance_is_not_material_skill_delta(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            (source / "README.md").write_text("unrelated\n", encoding="utf-8")
            current = commit_all(source, "unrelated change")
            report = module.build_report(adopted, {url: source})
        item = report["skills"][0]
        self.assertEqual(item["status"], "source_unchanged")
        self.assertEqual(item["current_revision"], current)
        self.assertEqual(item["changed_paths"], [])
        self.assertFalse(item["disposition_required"])

    def test_removed_source_package_requires_review_not_deletion(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            run_git(source, "rm", "-r", ".agents/skills/sample-skill")
            commit_all(source, "remove source skill")
            report = module.build_report(adopted, {url: source})
        item = report["skills"][0]
        self.assertEqual(item["status"], "source_removed")
        self.assertTrue(item["disposition_required"])
        self.assertEqual(item["recommended_dispositions"], ["defer", "not-applicable", "preserve-local"])
        self.assertFalse(report["checks"]["automatic_sync_applied"])

    def test_missing_source_mapping_is_not_observable(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            _, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            report = module.build_report(adopted, {})
        item = report["skills"][0]
        self.assertEqual(item["status"], "not_observable")
        self.assertIsNone(item["current_revision"])
        self.assertTrue(item["disposition_required"])

    def test_adopted_hash_drift_fails_closed(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            (adopted / "skills" / "sample-skill" / "SKILL.md").write_text("drift\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "adopted content hash"):
                module.build_report(adopted, {url: source})

    def test_workspace_divergence_is_explicit_review_evidence(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            workspace = root / "workspace"
            workspace_skill = workspace / "sample-skill"
            workspace_skill.mkdir(parents=True)
            (workspace_skill / "SKILL.md").write_text("different\n", encoding="utf-8")
            report = module.build_report(adopted, {url: source}, catalog_root=workspace)
        item = report["skills"][0]
        self.assertEqual(item["source_status"], "source_unchanged")
        self.assertEqual(item["workspace_status"], "diverged_from_adoption_record")
        self.assertIn("workspace-diverged", item["review_reasons"])
        self.assertTrue(item["disposition_required"])

    def test_snapshot_refresh_record_is_tracked_and_detects_source_skill_change(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            workspace = root / "workspace"
            source_skill = workspace / "source-helper"
            source_skill.mkdir(parents=True)
            (source_skill / "SKILL.md").write_text(
                "---\nname: source-helper\ndescription: helper\n---\n",
                encoding="utf-8",
            )
            update_dir = adopted / "config" / "catalogue-skill-updates"
            update_dir.mkdir(parents=True)
            update = {
                "schema_version": 1,
                "skill_id": "target-skill",
                "source_baseline": {
                    "skills": {
                        "source-helper": {
                            "tree_sha256": tree_hash(source_skill),
                            "files": {"SKILL.md": hashlib.sha256((source_skill / "SKILL.md").read_bytes()).hexdigest()},
                            "file_count": 1,
                        }
                    }
                },
                "next_baseline": {"procedure": ["snapshot again"]},
            }
            (update_dir / "target-skill.json").write_text(json.dumps(update), encoding="utf-8")
            before = module.build_report(adopted, {url: source}, catalog_root=workspace)
            (source_skill / "SKILL.md").write_text("changed\n", encoding="utf-8")
            after = module.build_report(adopted, {url: source}, catalog_root=workspace)
        self.assertEqual(before["summary"]["tracked_refresh_count"], 1)
        self.assertEqual(before["refresh_records"][0]["status"], "source_snapshot_unchanged")
        self.assertFalse(before["refresh_records"][0]["disposition_required"])
        self.assertEqual(after["refresh_records"][0]["status"], "source_snapshot_changed")
        self.assertEqual(after["refresh_records"][0]["changed_source_skills"], ["source-helper"])
        self.assertTrue(after["refresh_records"][0]["disposition_required"])

    def test_reviewed_maintenance_baseline_suppresses_already_classified_delta(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, url)
            adopted = make_adopted_repo(root, url, baseline)
            workspace = root / "workspace"
            workspace_skill = workspace / "sample-skill"
            workspace_skill.mkdir(parents=True)
            (workspace_skill / "SKILL.md").write_text("accepted successor\n", encoding="utf-8")
            run_git(source, "rm", "-r", ".agents/skills/sample-skill")
            current = commit_all(source, "remove source skill")
            maintenance_dir = adopted / "config" / "catalogue-source-maintenance"
            maintenance_dir.mkdir(parents=True)
            maintenance = {
                "schema_version": 1,
                "skill_baselines": {
                    "sample-skill": {
                        "reviewed_source_revision": current,
                        "workspace_content_sha256": module.compute_skill_hash(workspace_skill),
                    }
                },
                "refresh_baselines": {},
            }
            (maintenance_dir / "2026-08-16.json").write_text(json.dumps(maintenance), encoding="utf-8")
            report = module.build_report(adopted, {url: source}, catalog_root=workspace)
        item = report["skills"][0]
        self.assertEqual(item["origin_reviewed_revision"], baseline)
        self.assertEqual(item["reviewed_revision"], current)
        self.assertEqual(item["source_status"], "source_unchanged")
        self.assertEqual(item["workspace_status"], "matches_reviewed_workspace_baseline")
        self.assertFalse(item["disposition_required"])

    def test_snapshot_hash_rejects_linked_or_reparse_package_path(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "sample-skill"
            linked = skill / "references" / "linked"
            linked.mkdir(parents=True)
            (linked / "guide.md").write_text("outside-like\n", encoding="utf-8")
            original = module._is_link_like

            def fake_link_like(path: Path) -> bool:
                return path == linked or original(path)

            with mock.patch.object(module, "_is_link_like", side_effect=fake_link_like):
                with self.assertRaisesRegex(ValueError, "linked or reparse"):
                    module._snapshot_tree_hash(skill)

    def test_repository_maintenance_baseline_is_machine_readable(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        skill_baselines, refresh_baselines = module._load_maintenance_baselines(ROOT)
        self.assertIn("develop-code", skill_baselines)
        self.assertIn("develop-docs", skill_baselines)
        self.assertIn("kis-mcp", refresh_baselines)
        self.assertEqual(len(refresh_baselines["kis-mcp"]), 4)

    def test_source_repository_identity_must_match_mapping(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "source delta script is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://github.com/example/source.git"
            source, baseline = make_source_repo(root, "https://github.com/example/other.git")
            adopted = make_adopted_repo(root, url, baseline)
            with self.assertRaisesRegex(ValueError, "origin.*does not match"):
                module.build_report(adopted, {url: source})


if __name__ == "__main__":
    unittest.main()
