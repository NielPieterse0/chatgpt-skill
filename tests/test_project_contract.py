from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
