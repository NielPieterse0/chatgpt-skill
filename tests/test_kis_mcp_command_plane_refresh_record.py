from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "config" / "catalogue-skill-updates" / "kis-mcp-command-plane-2026-08-16.json"


def tree_manifest(path: Path) -> tuple[str, dict[str, str]]:
    entries: list[tuple[str, str]] = []
    for candidate in path.rglob("*"):
        if candidate.is_file():
            relative = candidate.relative_to(path).as_posix()
            entries.append((relative, hashlib.sha256(candidate.read_bytes()).hexdigest()))
    entries.sort(key=lambda item: (item[0].casefold(), item[0]))
    files = dict(entries)
    digest = hashlib.sha256()
    for relative, file_hash in entries:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(file_hash.encode())
        digest.update(b"\n")
    return digest.hexdigest(), files


class KisMcpCommandPlaneRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_record_binds_issue_source_and_previous_baseline(self) -> None:
        record = self.record
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["skill_id"], "kis-mcp")
        self.assertEqual(record["authority"]["issue_number"], 80)
        self.assertEqual(record["source_evidence"]["repository"], "NielPieterse0/kis-mcp")
        self.assertEqual(len(record["source_evidence"]["repository_revision"]), 40)
        self.assertEqual(
            record["adopted_before"]["snapshot_path"],
            "references/catalogue-update-baselines/kis-mcp/2026-08-16/adopted-after",
        )

    def test_after_snapshot_hashes_match_tracked_bytes(self) -> None:
        entry = self.record["adopted_after"]
        tree_hash, files = tree_manifest(ROOT / entry["snapshot_path"])
        self.assertEqual(entry["tree_sha256"], tree_hash)
        self.assertEqual(entry["files"], files)
        self.assertEqual(entry["file_count"], len(files))

    def test_delta_is_bounded_to_command_plane_guidance(self) -> None:
        before = ROOT / self.record["adopted_before"]["snapshot_path"]
        after = ROOT / self.record["adopted_after"]["snapshot_path"]
        _, before_files = tree_manifest(before)
        _, after_files = tree_manifest(after)
        changed = {
            item for item in before_files | after_files
            if before_files.get(item) != after_files.get(item)
        }
        self.assertEqual(changed, {"SKILL.md", "references/work-management.md"})

    def test_command_plane_concepts_are_present(self) -> None:
        after = ROOT / self.record["adopted_after"]["snapshot_path"]
        text = (after / "SKILL.md").read_text(encoding="utf-8") + "\n" + (
            after / "references" / "work-management.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "take-next-project-work",
            "manage-project-work-state",
            "work_management_then_repository_change",
            "project_management_sync_change_classification",
            "complete-work-managed-pull-request",
        ):
            self.assertIn(expected, text)
        self.assertNotIn(
            "The repository-owned source issue/PR must carry the canonical work metadata",
            text,
        )


if __name__ == "__main__":
    unittest.main()
