from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "catalogue_evaluation.py"


class CatalogueEvaluationTests(unittest.TestCase):
    def _skill(self, root: Path, name: str, body: str = "# Skill\n") -> Path:
        target = root / name
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Use when testing {name}.\n---\n{body}",
            encoding="utf-8",
        )
        return target

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_generate_and_validate_current_catalogue_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            self._skill(catalog, "beta")
            definitions = repo / "tests" / "skills" / "alpha"
            definitions.mkdir(parents=True)
            for name in ("trigger-cases.json", "output-evals.json", "abuse-cases.json"):
                (definitions / name).write_text("{}", encoding="utf-8")
            record = repo / "docs" / "testing" / "full-catalogue-skill-evaluation.json"

            generated = self._run(
                "generate",
                "--repo", str(repo),
                "--catalog-root", str(catalog),
                "--output", str(record),
                "--evaluated-at", "2026-08-16",
                "--source-revision", "f" * 40,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            payload = json.loads(record.read_text(encoding="utf-8"))
            self.assertEqual(payload["coverage"]["active_count"], 2)
            self.assertEqual(payload["coverage"]["current_covered_count"], 2)
            self.assertEqual(payload["coverage"]["defer_count"], 2)
            rows = {item["skill_id"]: item for item in payload["skills"]}
            self.assertEqual(rows["alpha"]["tracked_definition_status"], "complete")
            self.assertEqual(rows["beta"]["tracked_definition_status"], "missing")
            self.assertEqual(rows["alpha"]["behavioral_status"], "not_observable")
            self.assertEqual(rows["alpha"]["human_review_status"], "pending")

            validated = self._run(
                "validate",
                "--repo", str(repo),
                "--record", str(record),
                "--catalog-root", str(catalog),
            )
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            result = json.loads(validated.stdout)
            self.assertTrue(result["ok"])
            self.assertEqual(result["current_covered_count"], 2)

    def test_validate_fails_when_live_catalogue_hash_drifts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            skill = self._skill(catalog, "alpha")
            record = repo / "docs" / "testing" / "full-catalogue-skill-evaluation.json"
            generated = self._run(
                "generate",
                "--repo", str(repo),
                "--catalog-root", str(catalog),
                "--output", str(record),
                "--evaluated-at", "2026-08-16",
                "--source-revision", "f" * 40,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            (skill / "SKILL.md").write_text(
                "---\nname: alpha\ndescription: Use when alpha changed.\n---\n# changed\n",
                encoding="utf-8",
            )

            validated = self._run(
                "validate",
                "--repo", str(repo),
                "--record", str(record),
                "--catalog-root", str(catalog),
            )

            self.assertNotEqual(validated.returncode, 0)
            result = json.loads(validated.stdout)
            self.assertFalse(result["ok"])
            self.assertIn("CATALOGUE_DRIFT", {item["code"] for item in result["errors"]})


if __name__ == "__main__":
    unittest.main()
