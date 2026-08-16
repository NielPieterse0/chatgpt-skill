import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "plugin_portfolio.py"


def base_record() -> dict:
    return {
        "schema_version": 1,
        "plugin_id": "example-plugin",
        "display_name": "Example Plugin",
        "plugin_kind": "codex-plugin",
        "portfolio_status": "candidate",
        "source_status": "verified",
        "source": {
            "provenance_type": "trusted-local",
            "owner": "example-org",
            "canonical_uri": "https://example.test/example-plugin",
            "version": "1.2.3",
            "immutable_revision": "a" * 40,
            "retrieved_at": "2026-08-16",
            "artifact_sha256": "b" * 64,
            "license_or_terms": "MIT",
            "handoff": None,
        },
        "contents": {
            "skills": ["evaluate-skill"],
            "apps": [],
            "app_templates": [],
            "mcp_or_tooling": ["plugin-eval-cli"],
            "resources": ["README.md"],
        },
        "capabilities": {
            "filesystem_read": ["fixtures/"],
            "filesystem_write": [],
            "process_execution": False,
            "network": False,
            "credentials": False,
            "external_mutation": False,
        },
        "dependencies": [],
        "targets": [],
        "evaluation": {
            "status": "not_started",
            "evidence": [],
            "baseline": None,
            "reviewer": None,
            "reviewed_at": None,
        },
        "update": {
            "last_accepted_revision": None,
            "last_checked_at": None,
            "delta_evidence": None,
        },
        "rollback": {
            "disable_method": None,
            "uninstall_method": None,
            "retained_evidence": [],
        },
    }


def accepted_record() -> dict:
    record = base_record()
    record["portfolio_status"] = "accepted"
    record["evaluation"] = {
        "status": "passed",
        "evidence": ["evidence/plugin-eval.json"],
        "baseline": "without-plugin",
        "reviewer": "reviewer",
        "reviewed_at": "2026-08-16",
    }
    record["update"] = {
        "last_accepted_revision": record["source"]["immutable_revision"],
        "last_checked_at": "2026-08-16",
        "delta_evidence": "evidence/source-delta.json",
    }
    record["rollback"] = {
        "disable_method": "Disable the target plugin integration.",
        "uninstall_method": None,
        "retained_evidence": ["evidence/plugin-eval.json"],
    }
    return record


def validate(record: dict, *, materialize_evidence: bool = False) -> tuple[subprocess.CompletedProcess[str], set[str]]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        record_path = root / "portfolio" / "plugins" / record["plugin_id"] / "plugin-record.json"
        record_path.parent.mkdir(parents=True)
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if materialize_evidence:
            evidence_paths = list(record.get("evaluation", {}).get("evidence", []))
            evidence_paths += list(record.get("rollback", {}).get("retained_evidence", []))
            delta_evidence = record.get("update", {}).get("delta_evidence")
            if isinstance(delta_evidence, str):
                evidence_paths.append(delta_evidence)
            for relative in set(evidence_paths):
                evidence_path = root.joinpath(*Path(relative).parts)
                evidence_path.parent.mkdir(parents=True, exist_ok=True)
                evidence_path.write_text("{}\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "validate", "--repo", str(root), "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    payload = json.loads(result.stdout)
    return result, {item["code"] for item in payload["errors"]}


class PluginPortfolioGateTests(unittest.TestCase):
    def test_import_isolate_requires_finalized_matching_handoff(self) -> None:
        record = base_record()
        record["source"]["provenance_type"] = "import-isolate"
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("HANDOFF_REQUIRED", codes)

    def test_trusted_local_rejects_import_isolate_handoff(self) -> None:
        record = base_record()
        record["source"]["handoff"] = {
            "case_id": "case-1",
            "artifact": "plugin.zip",
            "artifact_sha256": record["source"]["artifact_sha256"],
        }
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("HANDOFF_UNEXPECTED", codes)

    def test_verified_source_requires_complete_immutable_identity(self) -> None:
        record = base_record()
        record["source"]["immutable_revision"] = None
        record["source"]["artifact_sha256"] = None
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("VERIFIED_SOURCE_INCOMPLETE", codes)

    def test_accepted_requires_passed_reviewed_evaluation(self) -> None:
        record = base_record()
        record["portfolio_status"] = "accepted"
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("ACCEPTED_EVALUATION_REQUIRED", codes)
        self.assertIn("ACCEPTED_REVIEW_REQUIRED", codes)
        self.assertIn("ACCEPTED_UPDATE_BASELINE_REQUIRED", codes)
        self.assertIn("ACCEPTED_ROLLBACK_REQUIRED", codes)

    def test_complete_accepted_record_is_valid(self) -> None:
        result, codes = validate(accepted_record(), materialize_evidence=True)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)
        self.assertEqual(set(), codes)

    def test_accepted_record_rejects_missing_repository_evidence(self) -> None:
        result, codes = validate(accepted_record())
        self.assertNotEqual(0, result.returncode)
        self.assertIn("EVIDENCE_MISSING", codes)
    def test_accepted_record_rejects_directory_as_evidence(self) -> None:
        record = accepted_record()
        record["evaluation"]["evidence"] = ["."]
        record["rollback"]["retained_evidence"] = ["."]
        record["update"]["delta_evidence"] = "."
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("EVIDENCE_NOT_FILE", codes)

    def test_accepted_record_rejects_self_reference_as_evidence(self) -> None:
        record = accepted_record()
        self_reference = "portfolio/plugins/example-plugin/plugin-record.json"
        record["evaluation"]["evidence"] = [self_reference]
        record["rollback"]["retained_evidence"] = [self_reference]
        record["update"]["delta_evidence"] = self_reference
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("EVIDENCE_SELF_REFERENCE", codes)
    def test_active_target_requires_installed_state(self) -> None:
        record = base_record()
        record["targets"] = [
            {
                "target_id": "chatgpt",
                "installation_status": "not_installed",
                "activation_status": "active",
                "app_access": [],
            }
        ]
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("TARGET_ACTIVE_NOT_INSTALLED", codes)

    def test_unknown_fields_fail_closed(self) -> None:
        record = copy.deepcopy(base_record())
        record["unexpected"] = True
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("RECORD_UNKNOWN", codes)


    def test_handoff_pending_can_be_recorded_without_finalized_handoff(self) -> None:
        record = base_record()
        record["source"]["provenance_type"] = "import-isolate"
        record["source_status"] = "handoff_pending"
        record["source"]["handoff"] = None
        result, codes = validate(record)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)
        self.assertEqual(set(), codes)

    def test_import_isolate_handoff_digest_must_match_bundle_digest(self) -> None:
        record = base_record()
        record["source"]["provenance_type"] = "import-isolate"
        record["source"]["handoff"] = {
            "case_id": "case-1",
            "artifact": "plugin.zip",
            "artifact_sha256": "c" * 64,
        }
        result, codes = validate(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("HANDOFF_DIGEST_MISMATCH", codes)

if __name__ == "__main__":
    unittest.main()
