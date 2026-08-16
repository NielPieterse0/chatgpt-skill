from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "config" / "catalogue-skill-updates" / "kis-mcp.json"
ALLOWED_DISPOSITIONS = {"adopt", "adapt", "defer", "not-applicable", "preserve-local"}


def tree_manifest(path: Path) -> tuple[str, dict[str, str]]:
    entries = []
    for candidate in path.rglob("*"):
        if candidate.is_file():
            relative = candidate.relative_to(path).as_posix()
            entries.append((relative, hashlib.sha256(candidate.read_bytes()).hexdigest()))

    # Canonicalize ordering independently of pathlib's OS-specific path ordering.
    entries.sort(key=lambda item: (item[0].casefold(), item[0]))
    files = dict(entries)

    digest = hashlib.sha256()
    for relative, file_hash in entries:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(file_hash.encode())
        digest.update(b"\n")
    return digest.hexdigest(), files


class KisMcpRefreshRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_record_has_diffable_baselines_and_allowed_decisions(self) -> None:
        self.assertEqual(self.record["schema_version"], 1)
        self.assertEqual(self.record["skill_id"], "kis-mcp")
        self.assertEqual(
            self.record["snapshot_manifest_order"],
            "relative-posix-path-casefold-then-exact",
        )
        self.assertEqual(self.record["authority"]["issue_number"], 57)
        self.assertEqual(self.record["previous_source_baseline"]["status"], "legacy-non-diffable")
        self.assertIsNone(self.record["previous_source_baseline"]["mcp_development_source_hash"])
        self.assertTrue(self.record["decisions"])
        for decision in self.record["decisions"]:
            self.assertIn(decision["disposition"], ALLOWED_DISPOSITIONS)
            self.assertTrue(decision["source"])
            self.assertTrue(decision["topic"])
            self.assertTrue(decision["rationale"])
            self.assertIsInstance(decision["target_files"], list)

    def test_recorded_snapshot_hashes_match_tracked_bytes(self) -> None:
        for key in ("adopted_before", "adopted_after"):
            entry = self.record[key]
            path = ROOT / entry["snapshot_path"]
            tree_hash, files = tree_manifest(path)
            self.assertEqual(entry["tree_sha256"], tree_hash, key)
            self.assertEqual(entry["files"], files, key)
            self.assertEqual(entry["file_count"], len(files), key)

    def test_source_snapshots_match_recorded_hashes(self) -> None:
        source_root = ROOT / self.record["source_baseline"]["snapshot_path"]
        for name, entry in self.record["source_baseline"]["skills"].items():
            tree_hash, files = tree_manifest(source_root / name)
            self.assertEqual(entry["tree_sha256"], tree_hash, name)
            self.assertEqual(entry["files"], files, name)
            self.assertEqual(entry["file_count"], len(files), name)

    def test_refresh_changes_only_declared_kis_mcp_files(self) -> None:
        before = ROOT / self.record["adopted_before"]["snapshot_path"]
        after = ROOT / self.record["adopted_after"]["snapshot_path"]
        _, before_files = tree_manifest(before)
        _, after_files = tree_manifest(after)
        changed = {
            path for path in before_files | after_files
            if before_files.get(path) != after_files.get(path)
        }
        self.assertEqual(
            changed,
            {"SKILL.md", "references/operator-support.md", "references/skills-module.md"},
        )

    def test_next_baseline_points_to_current_source_and_adopted_snapshots(self) -> None:
        next_baseline = self.record["next_baseline"]
        self.assertEqual(next_baseline["source_snapshot_path"], self.record["source_baseline"]["snapshot_path"])
        self.assertEqual(next_baseline["adopted_snapshot_path"], self.record["adopted_after"]["snapshot_path"])
        self.assertGreaterEqual(len(next_baseline["procedure"]), 4)


if __name__ == "__main__":
    unittest.main()
