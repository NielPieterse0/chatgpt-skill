from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.project_contract import validate_project_contract

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "settings" / "projects" / "chatgpt-skill.json"


class ProjectContractTests(unittest.TestCase):
    def test_work_management_contract_is_complete(self) -> None:
        self.assertTrue(CONFIG.is_file(), "project Work Management registration is required")
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual("chatgpt-skill", data["project_id"])
        self.assertEqual("NielPieterse0/chatgpt-skill", data["repository"]["full_name"])
        work = data["work_management"]
        self.assertEqual("commissioned_kis_work_management", work["authority"])
        self.assertEqual("capability_driven", work["discovery"])
        self.assertNotIn("authority_root", work)
        self.assertNotIn("schema_source", work)
        self.assertEqual({"owner": "NielPieterse0", "owner_type": "user", "number": 1}, work["github_project"])
        self.assertTrue(work["source_scope"]["exact_match_required"])
        self.assertEqual("NielPieterse0/chatgpt-skill", work["source_scope"]["repository"])
        self.assertTrue(work["identity"]["preserve_issue_backed_identity"])
        self.assertEqual("github_project", work["identity"]["projection"])
        self.assertEqual(
            {"work_item_semantics", "work_lifecycle_operations", "work_selection"},
            set(work["contract_fingerprints"]),
        )
        self.assertTrue(
            all(
                isinstance(value, str)
                and len(value) == 64
                and all(char in "0123456789abcdef" for char in value)
                for value in work["contract_fingerprints"].values()
            )
        )
        self.assertEqual(
            {
                "all_open_source_issues_projected": True,
                "closed_source_issues_retained_for_history": True,
                "require_current_kis_metadata_contract": True,
                "reconcile_before_claim": True,
                "reconcile_before_closeout": True,
                "fail_closed_on_projection_drift": True,
            },
            work["projection_invariants"],
        )
        self.assertTrue({"project_management.read", "project_management.write", "work.reconcile"}.issubset(set(work["required_capability_families"])))
        self.assertTrue({"runtime.project_management_inventory", "runtime.project_management_reconcile", "runtime.project_management_schema_status", "runtime.project_management_verify_traceability"}.issubset(set(work["required_operations"])))

    def test_project_contract_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/project_contract.py", "validate", "--repo", "."],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_project_contract_rejects_missing_projection_gate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            config = repo / "settings" / "projects" / "chatgpt-skill.json"
            config.parent.mkdir(parents=True)
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
            data["work_management"]["projection_invariants"]["reconcile_before_closeout"] = False
            config.write_text(json.dumps(data), encoding="utf-8")

            issues = validate_project_contract(repo)

            self.assertIn("PROJECTION_INVARIANTS_INVALID", {issue.code for issue in issues})

    def test_project_contract_rejects_invalid_work_contract_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            config = repo / "settings" / "projects" / "chatgpt-skill.json"
            config.parent.mkdir(parents=True)
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
            data["work_management"]["contract_fingerprints"]["work_selection"] = "stale"
            config.write_text(json.dumps(data), encoding="utf-8")

            issues = validate_project_contract(repo)

            self.assertIn("WORK_CONTRACT_FINGERPRINTS_INVALID", {issue.code for issue in issues})

    def test_project_contract_rejects_boolean_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            config = repo / "settings" / "projects" / "chatgpt-skill.json"
            config.parent.mkdir(parents=True)
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
            data["schema_version"] = True
            config.write_text(json.dumps(data), encoding="utf-8")

            issues = validate_project_contract(repo)

            self.assertIn("PROJECT_SCHEMA_VERSION_INVALID", {issue.code for issue in issues})


if __name__ == "__main__":
    unittest.main()
