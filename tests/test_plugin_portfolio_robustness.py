import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from tests.test_plugin_portfolio_gates import accepted_record, base_record


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from scripts import plugin_portfolio
VALIDATOR = REPO_ROOT / "scripts" / "plugin_portfolio.py"


def run_root(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "validate", "--repo", str(root), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_record(record: dict) -> tuple[subprocess.CompletedProcess[str], set[str]]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        record_path = root / "portfolio" / "plugins" / record["plugin_id"] / "plugin-record.json"
        record_path.parent.mkdir(parents=True)
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        result = run_root(root)
    payload = json.loads(result.stdout)
    return result, {item["code"] for item in payload["errors"]}


class PluginPortfolioRobustnessTests(unittest.TestCase):
    def test_compact_date_is_rejected(self) -> None:
        record = base_record()
        record["source"]["retrieved_at"] = "20260816"
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SOURCE_DATE_INVALID", codes)

    def test_schema_length_limits_are_enforced(self) -> None:
        record = base_record()
        record["display_name"] = "x" * 201
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("DISPLAY_NAME_INVALID", codes)

    def test_malformed_enum_returns_structured_error(self) -> None:
        record = base_record()
        record["plugin_kind"] = []
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PLUGIN_KIND_INVALID", codes)

    def test_malformed_uri_returns_structured_error(self) -> None:
        record = base_record()
        record["source"]["canonical_uri"] = "http://[broken"
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SOURCE_URI_INVALID", codes)

    def test_missing_portfolio_root_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = run_root(Path(temp))
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PORTFOLIO_ROOT_MISSING", {item["code"] for item in payload["errors"]})

    def test_plugin_directory_requires_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "portfolio" / "plugins" / "example-plugin").mkdir(parents=True)
            result = run_root(root)
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PLUGIN_RECORD_MISSING", {item["code"] for item in payload["errors"]})

    def test_nested_record_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nested = root / "portfolio" / "plugins" / "example-plugin" / "nested" / "plugin-record.json"
            nested.parent.mkdir(parents=True)
            nested.write_text("{}\n", encoding="utf-8")
            result = run_root(root)
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PLUGIN_RECORD_MISPLACED", {item["code"] for item in payload["errors"]})

    def test_empty_portfolio_root_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "portfolio" / "plugins").mkdir(parents=True)
            result = run_root(root)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)


    def test_repository_path_length_limit_is_enforced(self) -> None:
        record = base_record()
        record["update"]["delta_evidence"] = "x" * 501
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("UPDATE_DELTA_PATH_INVALID", codes)

    def test_boolean_schema_version_is_rejected(self) -> None:
        record = base_record()
        record["schema_version"] = True
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SCHEMA_VERSION_INVALID", codes)

    def test_symlinked_plugin_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            portfolio = root / "portfolio" / "plugins"
            portfolio.mkdir(parents=True)
            external = root / "external-plugin"
            external.mkdir()
            (external / "plugin-record.json").write_text(
                json.dumps(base_record(), indent=2) + "\n", encoding="utf-8"
            )
            linked = portfolio / "example-plugin"
            try:
                os.symlink(external, linked, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"directory symlink unavailable: {exc}")
            result = run_root(root)
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PLUGIN_DIRECTORY_LINKED", {item["code"] for item in payload["errors"]})

    def test_whitespace_repository_path_is_rejected(self) -> None:
        record = base_record()
        record["update"]["delta_evidence"] = "   "
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("UPDATE_DELTA_PATH_INVALID", codes)

    def test_canonical_uri_with_whitespace_is_rejected(self) -> None:
        record = base_record()
        record["source"]["canonical_uri"] = "https://example.test/a b"
        result, codes = run_record(record)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SOURCE_URI_INVALID", codes)

    def test_nested_link_or_junction_is_rejected_before_descent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plugin_dir = root / "portfolio" / "plugins" / "example-plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "plugin-record.json").write_text(
                json.dumps(base_record(), indent=2) + "\n", encoding="utf-8"
            )
            external = root / "external"
            external.mkdir()
            (external / "plugin-record.json").write_text("{}\n", encoding="utf-8")
            linked = plugin_dir / "linked"
            if os.name == "nt":
                creation = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(linked), str(external)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if creation.returncode != 0:
                    self.skipTest(f"junction unavailable: {creation.stderr or creation.stdout}")
            else:
                try:
                    os.symlink(external, linked, target_is_directory=True)
                except (OSError, NotImplementedError) as exc:
                    self.skipTest(f"directory symlink unavailable: {exc}")
            result = run_root(root)
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PLUGIN_PATH_LINKED", {item["code"] for item in payload["errors"]})

    def test_linked_portfolio_parent_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            external = root / "external-portfolio"
            (external / "plugins").mkdir(parents=True)
            linked_parent = root / "portfolio"
            if os.name == "nt":
                creation = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(linked_parent), str(external)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if creation.returncode != 0:
                    self.skipTest(f"junction unavailable: {creation.stderr or creation.stdout}")
            else:
                try:
                    os.symlink(external, linked_parent, target_is_directory=True)
                except (OSError, NotImplementedError) as exc:
                    self.skipTest(f"directory symlink unavailable: {exc}")
            result = run_root(root)
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PORTFOLIO_PATH_LINKED", {item["code"] for item in payload["errors"]})

    def test_root_level_plugin_record_is_rejected_as_misplaced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            portfolio = root / "portfolio" / "plugins"
            portfolio.mkdir(parents=True)
            (portfolio / "plugin-record.json").write_text("{}\n", encoding="utf-8")
            result = run_root(root)
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PLUGIN_RECORD_MISPLACED", {item["code"] for item in payload["errors"]})

    def test_unreadable_portfolio_root_returns_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            portfolio = root / "portfolio" / "plugins"
            portfolio.mkdir(parents=True)
            original_iterdir = Path.iterdir

            def guarded_iterdir(path: Path):
                if path == portfolio:
                    raise OSError("simulated enumeration failure")
                return original_iterdir(path)

            with mock.patch.object(Path, "iterdir", guarded_iterdir):
                report = plugin_portfolio.validate_repository(root)
        self.assertFalse(report.ok)
        self.assertIn("PORTFOLIO_ROOT_UNREADABLE", {item.code for item in report.errors})

    def test_all_closed_enum_fields_reject_unknown_values(self) -> None:
        cases = []

        record = base_record()
        record["plugin_kind"] = "unknown"
        cases.append(("plugin_kind", record, "PLUGIN_KIND_INVALID"))

        record = base_record()
        record["portfolio_status"] = "unknown"
        cases.append(("portfolio_status", record, "PORTFOLIO_STATUS_INVALID"))

        record = base_record()
        record["source_status"] = "unknown"
        cases.append(("source_status", record, "SOURCE_STATUS_INVALID"))

        record = base_record()
        record["source"]["provenance_type"] = "unknown"
        cases.append(("provenance_type", record, "PROVENANCE_TYPE_INVALID"))

        record = base_record()
        record["evaluation"]["status"] = "unknown"
        cases.append(("evaluation_status", record, "EVALUATION_STATUS_INVALID"))

        record = base_record()
        record["dependencies"] = [{"id": "dep", "kind": "unknown", "version": None, "required": True}]
        cases.append(("dependency_kind", record, "DEPENDENCY_KIND_INVALID"))

        record = base_record()
        record["targets"] = [{"target_id": "chatgpt", "installation_status": "unknown", "activation_status": "inactive", "app_access": []}]
        cases.append(("installation_status", record, "INSTALLATION_STATUS_INVALID"))

        record = base_record()
        record["targets"] = [{"target_id": "chatgpt", "installation_status": "installed", "activation_status": "unknown", "app_access": []}]
        cases.append(("activation_status", record, "ACTIVATION_STATUS_INVALID"))

        record = base_record()
        record["targets"] = [{"target_id": "chatgpt", "installation_status": "installed", "activation_status": "inactive", "app_access": [{"app_id": "github", "access_status": "unknown"}]}]
        cases.append(("app_access_status", record, "APP_ACCESS_STATUS_INVALID"))

        for name, candidate, expected_code in cases:
            with self.subTest(name=name):
                result, codes = run_record(candidate)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected_code, codes)

    def test_valid_nested_dependency_target_and_app_access_are_accepted(self) -> None:
        record = base_record()
        record["dependencies"] = [{"id": "helper", "kind": "executable", "version": "1.0", "required": True}]
        record["targets"] = [{"target_id": "chatgpt", "installation_status": "installed", "activation_status": "inactive", "app_access": [{"app_id": "github", "access_status": "connected"}]}]
        result, codes = run_record(record)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)
        self.assertEqual(set(), codes)

    def test_evidence_path_through_link_or_junction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plugin_dir = root / "portfolio" / "plugins" / "example-plugin"
            plugin_dir.mkdir(parents=True)
            record = accepted_record()
            record["evaluation"]["evidence"] = ["evidence/plugin-eval.json"]
            record["rollback"]["retained_evidence"] = ["evidence/plugin-eval.json"]
            record["update"]["delta_evidence"] = "evidence/plugin-eval.json"
            (plugin_dir / "plugin-record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            external = root / "external-evidence"
            external.mkdir()
            (external / "plugin-eval.json").write_text("{}\n", encoding="utf-8")
            linked = root / "evidence"
            if os.name == "nt":
                creation = subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(external)], text=True, capture_output=True, check=False)
                if creation.returncode != 0:
                    self.skipTest(f"junction unavailable: {creation.stderr or creation.stdout}")
            else:
                try:
                    os.symlink(external, linked, target_is_directory=True)
                except (OSError, NotImplementedError) as exc:
                    self.skipTest(f"directory symlink unavailable: {exc}")
            result = run_root(root)
        payload = json.loads(result.stdout)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("EVIDENCE_LINKED", {item["code"] for item in payload["errors"]})

if __name__ == "__main__":
    unittest.main()
