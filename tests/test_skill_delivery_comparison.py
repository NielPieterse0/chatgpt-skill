from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_delivery_comparison.py"
spec = importlib.util.spec_from_file_location("skill_delivery_comparison", SCRIPT)
assert spec and spec.loader
skill_delivery_comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_delivery_comparison)


class SkillDeliveryComparisonTests(unittest.TestCase):
    digest = "a" * 64
    other_digest = "b" * 64

    def _group(
        self,
        *,
        skill: str = "alpha",
        digest: str | None = None,
        project: str | None = "chatgpt-skill",
        path: str = "kis_native",
        loaded: int = 1,
    ) -> dict[str, object]:
        resource_reads = 2 if path == "mcp_resource" else 1
        return {
            "skill_id": skill,
            "content_sha256": digest or self.digest,
            "project_id": project,
            "delivery_path": path,
            "loaded_count": loaded,
            "resource_read_count": resource_reads,
            "applied_count": 0,
            "completed_count": 0,
            "failed_count": 0,
            "error_count": 0,
            "digest_verified_count": loaded + resource_reads if path == "mcp_resource" else 0,
            "digest_failed_count": 0,
        }

    def _comparison(
        self,
        *,
        skill: str = "alpha",
        digest: str | None = None,
        project: str | None = "chatgpt-skill",
        comparable: bool = True,
        reason: str = "matched_content_sha256",
    ) -> dict[str, object]:
        return {
            "skill_id": skill,
            "content_sha256": digest or self.digest,
            "project_id": project,
            "comparable": comparable,
            "reason": reason,
        }

    def _report(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "groups": [
                self._group(),
                self._group(path="mcp_resource", loaded=2),
                self._group(skill="beta", digest=self.other_digest, loaded=3),
            ],
            "comparisons": [
                self._comparison(),
                self._comparison(
                    skill="beta",
                    digest=self.other_digest,
                    comparable=False,
                    reason="missing_mcp_resource",
                ),
            ],
            "event_count": 11,
            "catalogue_exposure_count": 7,
            "truncated": False,
        }

    def test_valid_report_projects_same_hash_delivery_comparison(self) -> None:
        projection = skill_delivery_comparison.project_report(self._report())

        self.assertFalse(projection["behavioral_effectiveness_evidence"])
        self.assertEqual(projection["summary"]["identity_count"], 2)
        self.assertEqual(projection["summary"]["comparable_identity_count"], 1)
        self.assertEqual(projection["summary"]["path_group_counts"]["kis_native"], 2)
        self.assertEqual(projection["summary"]["path_group_counts"]["mcp_resource"], 1)
        self.assertEqual(
            projection["summary"]["path_totals"]["mcp_resource"]["loaded_count"], 2
        )
        self.assertEqual(projection["source_catalogue_exposure_count"], 7)
        self.assertFalse(projection["source_truncated"])
        self.assertTrue(projection["summary"]["metric_comparison_eligible"])
        self.assertEqual(projection["summary"]["metric_comparison_status"], "complete")

    def test_truncated_report_blocks_metric_comparison_but_preserves_identity_pairing(self) -> None:
        report = self._report()
        report["truncated"] = True

        projection = skill_delivery_comparison.project_report(report)

        self.assertEqual(projection["summary"]["comparable_identity_count"], 1)
        self.assertFalse(projection["summary"]["metric_comparison_eligible"])
        self.assertEqual(projection["summary"]["metric_comparison_status"], "truncated")
        self.assertTrue(projection["source_truncated"])

    def test_filters_preserve_identity_and_source_metadata(self) -> None:
        projection = skill_delivery_comparison.project_report(
            self._report(),
            skill_id="alpha",
            project_id="chatgpt-skill",
            content_sha256=self.digest,
        )

        self.assertEqual(projection["summary"]["identity_count"], 1)
        self.assertEqual(projection["summary"]["comparable_identity_count"], 1)
        self.assertEqual(len(projection["groups"]), 2)
        self.assertEqual(projection["source_event_count"], 11)
        self.assertEqual(
            projection["filters"],
            {
                "skill_id": "alpha",
                "project": {"mode": "exact", "value": "chatgpt-skill"},
                "content_sha256": self.digest,
            },
        )

    def test_null_project_filter_is_distinct_from_all_projects(self) -> None:
        report = self._report()
        report["groups"] = [
            self._group(project=None),
            self._group(project=None, path="mcp_resource"),
            self._group(project="chatgpt-skill"),
            self._group(project="chatgpt-skill", path="mcp_resource"),
        ]
        report["comparisons"] = [
            self._comparison(project=None),
            self._comparison(project="chatgpt-skill"),
        ]

        all_projects = skill_delivery_comparison.project_report(report, skill_id="alpha")
        null_project = skill_delivery_comparison.project_report(
            report, skill_id="alpha", project_id=None
        )

        self.assertEqual(all_projects["summary"]["identity_count"], 2)
        self.assertEqual(null_project["summary"]["identity_count"], 1)
        self.assertTrue(all(item["project_id"] is None for item in null_project["groups"]))
        self.assertEqual(
            null_project["filters"]["project"], {"mode": "exact", "value": None}
        )

    def test_different_hashes_never_form_transport_pair(self) -> None:
        report = self._report()
        report["groups"] = [
            self._group(digest=self.digest),
            self._group(digest=self.other_digest),
            self._group(digest=self.other_digest, path="mcp_resource"),
        ]
        report["comparisons"] = [
            self._comparison(
                digest=self.digest,
                comparable=False,
                reason="missing_mcp_resource",
            ),
            self._comparison(digest=self.other_digest),
        ]

        projection = skill_delivery_comparison.project_report(report)

        comparisons = {
            item["content_sha256"]: item for item in projection["comparisons"]
        }
        self.assertFalse(comparisons[self.digest]["comparable"])
        self.assertTrue(comparisons[self.other_digest]["comparable"])

    def test_claimed_comparison_without_both_paths_is_rejected(self) -> None:
        report = self._report()
        report["groups"] = [self._group()]
        report["comparisons"] = [self._comparison()]

        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

    def test_comparable_mcp_group_requires_clean_digest_verification(self) -> None:
        report = self._report()
        mcp = next(
            item for item in report["groups"] if item["delivery_path"] == "mcp_resource"
        )
        self.assertEqual(mcp["loaded_count"], 2)
        self.assertEqual(mcp["resource_read_count"], 2)
        self.assertEqual(mcp["digest_verified_count"], 4)
        skill_delivery_comparison.validate_report(report)

        for verified, failed in ((0, 0), (3, 0), (5, 0), (3, 1)):
            with self.subTest(verified=verified, failed=failed):
                report = self._report()
                mcp = next(
                    item for item in report["groups"]
                    if item["delivery_path"] == "mcp_resource"
                )
                mcp["digest_verified_count"] = verified
                mcp["digest_failed_count"] = failed
                with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
                    skill_delivery_comparison.validate_report(report)

        report = self._report()
        mcp = next(
            item for item in report["groups"] if item["delivery_path"] == "mcp_resource"
        )
        mcp["loaded_count"] = 0
        mcp["resource_read_count"] = 0
        mcp["digest_verified_count"] = 0
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

    def test_live_contract_load_only_mcp_digest_coverage_is_valid(self) -> None:
        report = self._report()
        mcp = next(
            item for item in report["groups"] if item["delivery_path"] == "mcp_resource"
        )
        mcp["loaded_count"] = 2
        mcp["resource_read_count"] = 0
        mcp["digest_verified_count"] = 2
        mcp["digest_failed_count"] = 0

        normalized = skill_delivery_comparison.validate_report(report)

        self.assertEqual(normalized["groups"][1]["digest_verified_count"], 2)

    def test_duplicate_delivery_path_group_is_rejected(self) -> None:
        report = self._report()
        report["groups"].append(copy.deepcopy(report["groups"][0]))
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

    def test_missing_or_unknown_comparison_identity_is_rejected(self) -> None:
        report = self._report()
        report["comparisons"] = report["comparisons"][:-1]
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

        report = self._report()
        report["comparisons"].append(
            self._comparison(skill="gamma", digest="c" * 64, comparable=False,
                             reason="missing_mcp_resource")
        )
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

    def test_unknown_fields_and_invalid_scalars_fail_closed(self) -> None:
        mutations = (
            lambda report: report.__setitem__("unexpected", True),
            lambda report: report.__setitem__("schema_version", 2),
            lambda report: report.__setitem__("event_count", True),
            lambda report: report.__setitem__("catalogue_exposure_count", -1),
            lambda report: report.__setitem__("truncated", "yes"),
            lambda report: report["groups"][0].__setitem__("delivery_path", "other"),
            lambda report: report["groups"][0].__setitem__("loaded_count", -1),
            lambda report: report["groups"][0].__setitem__("content_sha256", "bad"),
            lambda report: report["groups"][0].__setitem__("project_id", "bad id"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                report = self._report()
                mutate(report)
                with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
                    skill_delivery_comparison.validate_report(report)

    def test_group_and_comparison_unknown_fields_fail_closed(self) -> None:
        report = self._report()
        report["groups"][0]["resource_uri"] = "skill://alpha/SKILL.md"
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

        report = self._report()
        report["comparisons"][0]["extra"] = True
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

    def test_inconsistent_reason_and_mcp_only_identity_are_rejected(self) -> None:
        report = self._report()
        report["comparisons"][0]["reason"] = "missing_mcp_resource"
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

        report = self._report()
        report["groups"] = [self._group(path="mcp_resource")]
        report["comparisons"] = [
            self._comparison(comparable=False, reason="missing_kis_native")
        ]
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.validate_report(report)

    def test_catalogue_exposure_is_not_added_to_meaningful_usage(self) -> None:
        report = self._report()
        report["catalogue_exposure_count"] = 1000
        projection = skill_delivery_comparison.project_report(report)

        self.assertEqual(projection["source_catalogue_exposure_count"], 1000)
        native = projection["summary"]["path_totals"]["kis_native"]
        self.assertEqual(native["loaded_count"], 4)

    def test_invalid_filter_is_rejected(self) -> None:
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.project_report(self._report(), skill_id="bad id")
        with self.assertRaises(skill_delivery_comparison.DeliveryTelemetryError):
            skill_delivery_comparison.project_report(
                self._report(), content_sha256="not-a-hash"
            )

    def test_cli_null_project_filter_is_unambiguous(self) -> None:
        report = self._report()
        report["groups"] = [
            self._group(project=None),
            self._group(project=None, path="mcp_resource"),
            self._group(project="chatgpt-skill"),
            self._group(project="chatgpt-skill", path="mcp_resource"),
        ]
        report["comparisons"] = [
            self._comparison(project=None),
            self._comparison(project="chatgpt-skill"),
        ]
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "report.json"
            source.write_text(json.dumps(report), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = skill_delivery_comparison.main(
                    ["--input", str(source), "--skill", "alpha", "--null-project"]
                )
        self.assertEqual(exit_code, 0)
        projection = json.loads(stdout.getvalue())
        self.assertEqual(projection["summary"]["identity_count"], 1)
        self.assertEqual(projection["filters"]["project"], {"mode": "exact", "value": None})

    def test_cli_rejects_same_input_and_output_without_deleting_input(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "report.json"
            source.write_text(json.dumps(self._report()), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_delivery_comparison.main(
                    ["--input", str(source), "--output", str(source)]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("input and output paths must differ", stderr.getvalue())
            self.assertTrue(source.exists())

    def test_cli_rejects_hard_link_alias_to_input(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "report.json"
            alias = root / "alias.json"
            source.write_text(json.dumps(self._report()), encoding="utf-8")
            try:
                os.link(source, alias)
            except OSError as exc:
                self.skipTest(f"hard link unavailable: {exc}")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_delivery_comparison.main(
                    ["--input", str(source), "--output", str(alias)]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("input and output paths must differ", stderr.getvalue())
            self.assertTrue(source.exists())
            self.assertTrue(alias.exists())

    def test_cli_parser_failure_clears_stale_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "report.json"
            output = root / "projection.json"
            source.write_text(json.dumps(self._report()), encoding="utf-8")
            output.write_text("stale", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_delivery_comparison.main(
                    [
                        "--input", str(source), "--output", str(output),
                        "--project", "chatgpt-skill", "--null-project",
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("not allowed with argument", stderr.getvalue())
            self.assertFalse(output.exists())

    def test_end_of_options_marker_prevents_output_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "report.json"
            victim = root / "victim.json"
            source.write_text(json.dumps(self._report()), encoding="utf-8")
            victim.write_text("keep", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_delivery_comparison.main(
                    ["--input", str(source), "--", "--output", str(victim)]
                )
            self.assertEqual(exit_code, 2)
            self.assertTrue(victim.exists())

    def test_later_empty_output_does_not_delete_superseded_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "report.json"
            victim = root / "victim.json"
            source.write_text(json.dumps(self._report()), encoding="utf-8")
            victim.write_text("keep", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_delivery_comparison.main(
                    [
                        "--input", str(source), "--output", str(victim), "--output="
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertTrue(victim.exists())

    def test_preliminary_parser_failure_still_clears_recoverable_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "projection.json"
            output.write_text("stale", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_delivery_comparison.main(
                    ["--input", "--output", str(output)]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("expected one argument", stderr.getvalue())
            self.assertFalse(output.exists())

    def test_cli_writes_projection_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "report.json"
            output = root / "projection.json"
            source.write_text(json.dumps(self._report()), encoding="utf-8")

            exit_code = skill_delivery_comparison.main(
                ["--input", str(source), "--output", str(output), "--skill", "alpha"]
            )
            self.assertEqual(exit_code, 0)
            projection = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(projection["summary"]["identity_count"], 1)

            invalid = self._report()
            invalid["groups"][0]["loaded_count"] = -1
            source.write_text(json.dumps(invalid), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = skill_delivery_comparison.main(
                    ["--input", str(source), "--output", str(output)]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("ERROR:", stderr.getvalue())
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
