import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "plugin_portfolio.py"
SCHEMA = REPO_ROOT / "schemas" / "plugin-portfolio-record.schema.json"


def valid_record() -> dict:
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


def write_record(root: Path, record: dict) -> Path:
    record_path = (
        root
        / "portfolio"
        / "plugins"
        / record["plugin_id"]
        / "plugin-record.json"
    )
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record_path


def run_validator(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "validate", "--repo", str(root), *extra],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class PluginPortfolioValidationTests(unittest.TestCase):
    def test_valid_record_and_schema_are_accepted(self) -> None:
        self.assertTrue(SCHEMA.is_file(), "plugin portfolio schema is missing")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_record(root, valid_record())
            result = run_validator(root, "--json")
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(1, payload["record_count"])
        self.assertEqual([], payload["errors"])


if __name__ == "__main__":
    unittest.main()
