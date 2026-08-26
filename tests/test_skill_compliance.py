from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_compliance.py"
MATRIX = ROOT / "docs" / "audits" / "agent-skills-compliance-matrix.json"


class SkillComplianceTests(unittest.TestCase):
    def run_validator(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "validate", "--repo", str(ROOT), *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_repository_compliance_matrix_validates(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["audit_id"], "agent-skills-compliance")
        self.assertGreater(payload["summary"]["normative"]["compliant"], 0)
        self.assertIn("recommended", payload["summary"])

    def test_source_identity_substitution_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
            matrix["sources"]["AS-01"]["path"] = "package.json"
            matrix["sources"]["AS-01"]["sha256"] = hashlib.sha256(
                (ROOT / "package.json").read_bytes()
            ).hexdigest()
            candidate = Path(temp) / "matrix.json"
            candidate.write_text(json.dumps(matrix), encoding="utf-8")
            result = self.run_validator("--matrix", str(candidate))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any(item["code"] == "SOURCE_IDENTITY_MISMATCH" for item in payload["errors"]))

    def test_source_fingerprint_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
            source_id = sorted(matrix["sources"])[0]
            matrix["sources"][source_id]["sha256"] = "0" * 64
            candidate = Path(temp) / "matrix.json"
            candidate.write_text(json.dumps(matrix), encoding="utf-8")
            result = self.run_validator("--matrix", str(candidate))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any(item["code"] == "SOURCE_HASH_MISMATCH" for item in payload["errors"]))

    def test_compliant_requirement_requires_resolvable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
            requirement = next(
                item for item in matrix["requirements"] if item["status"] == "compliant"
            )
            requirement["evidence"] = ["missing/evidence.txt"]
            candidate = Path(temp) / "matrix.json"
            candidate.write_text(json.dumps(matrix), encoding="utf-8")
            result = self.run_validator("--matrix", str(candidate))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any(item["code"] == "EVIDENCE_MISSING" for item in payload["errors"]))

    def test_normative_gap_fails_compliance_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
            requirement = next(
                item for item in matrix["requirements"] if item["classification"] == "normative"
            )
            requirement["status"] = "non_compliant"
            candidate = Path(temp) / "matrix.json"
            candidate.write_text(json.dumps(matrix), encoding="utf-8")
            result = self.run_validator("--matrix", str(candidate))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any(item["code"] == "NORMATIVE_GAP" for item in payload["errors"]))

    def test_expired_audit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
            matrix["audited_at"] = "2000-01-01"
            candidate = Path(temp) / "matrix.json"
            candidate.write_text(json.dumps(matrix), encoding="utf-8")
            result = self.run_validator("--matrix", str(candidate))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any(item["code"] == "AUDIT_STALE" for item in payload["errors"]))

    def test_reaudit_policy_must_be_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
            matrix["reaudit"] = {"max_age_days": 0, "triggers": []}
            candidate = Path(temp) / "matrix.json"
            candidate.write_text(json.dumps(matrix), encoding="utf-8")
            result = self.run_validator("--matrix", str(candidate))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any(item["code"] == "REAUDIT_INVALID" for item in payload["errors"]))

    def test_current_adopted_skill_references_resolve(self) -> None:
        result = self.run_validator()
        payload = json.loads(result.stdout)
        package_checks = payload["package_checks"]
        self.assertEqual(package_checks["invalid_reference_count"], 0)
        self.assertEqual(package_checks["over_500_line_count"], 0)
        expected_skill_count = sum(1 for _ in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(package_checks["skill_count"], expected_skill_count)


if __name__ == "__main__":
    unittest.main()
