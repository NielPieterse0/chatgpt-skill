from __future__ import annotations

import hashlib
import http.client
import json
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skill_catalog_dashboard.catalog import discover_catalog
from skill_catalog_dashboard.repo import _candidate_order_key, collect_repository_evidence
from skill_catalog_dashboard.report import build_report, report_to_dict, report_to_json
from skill_catalog_dashboard.telemetry import load_telemetry_json, load_telemetry_sqlite
from skill_catalog_dashboard.web import make_server, render_html
from skill_catalog_dashboard.work import load_work_management_json


class SkillCatalogDashboardTests(unittest.TestCase):
    def _skill(
        self,
        root: Path,
        name: str,
        *,
        description: str = "Use this skill for dashboard tests.",
        status: str | None = None,
        folded: bool = False,
    ) -> Path:
        skill = root / name
        skill.mkdir(parents=True)
        if folded:
            description_lines = "\n".join(
                f"  {line}" for line in description.split("\n")
            )
            description_field = f"description: >\n{description_lines}"
        else:
            description_field = f"description: {description}"
        status_field = "" if status is None else f"\nstatus: {status}"
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\n{description_field}{status_field}\n---\n# {name}\n",
            encoding="utf-8",
        )
        return skill

    def _scorecard(
        self,
        skill_id: str,
        runtime_hash: str,
        *,
        disposition: str = "admit",
        verified_at: str = "2026-08-15",
    ) -> dict[str, object]:
        metric = {
            "with_skill": {"status": "observed", "samples": 1, "mean": 1.0},
            "baseline": {"status": "observed", "samples": 1, "mean": 1.0},
            "delta": 0.0,
        }
        return {
            "schema_version": 1,
            "skill_id": skill_id,
            "adopted_content_sha256": "a" * 64,
            "runtime_content_sha256": runtime_hash,
            "evaluation": {
                "adapter": "test-adapter",
                "target_verified_at": verified_at,
                "eval_definition_revision": "b" * 40,
                "definition_provenance": {
                    "revision": "b" * 40,
                    "sha256": {
                        "trigger-cases.json": "c" * 64,
                        "output-cases.json": "d" * 64,
                        "abuse-cases.json": "e" * 64,
                    },
                },
                "baseline": {"kind": "no-skill", "identity": "baseline"},
                "isolation_method": "fresh-process",
            },
            "dimensions": {
                "trigger": {"status": "pass", "passed": 0, "total": 0, "cases": []},
                "output_quality": {
                    "status": "pass",
                    "with_skill_pass_rate": 1.0,
                    "baseline_pass_rate": 0.0,
                    "critical_failures": [],
                    "baseline_critical_regressions": [],
                    "material_improvements": [{"evidence": "test"}],
                    "run_counts": {},
                },
                "efficiency": {
                    "status": "observed",
                    "metrics": {
                        key: dict(metric)
                        for key in ("duration_ms", "input_tokens", "output_tokens", "tool_calls", "retries")
                    },
                },
                "verification": {"status": "pass", "passed": 1, "total": 1, "failed_ids": []},
                "abuse": {"status": "pass", "passed": 1, "total": 1, "failed_ids": []},
                "compatibility": {"status": "pass", "evidence": "compatible"},
                "human_review": {
                    "status": "pass",
                    "reviewer": "test-reviewer",
                    "date": verified_at,
                    "feedback": [],
                },
                "rollback": {"status": "pass", "verified": True, "evidence": "rollback verified"},
                "operational_telemetry": {
                    "status": "not_provided",
                    "behavioral_effectiveness_evidence": False,
                    "totals": {},
                    "groups": [],
                },
            },
            "fixture_candidates": [],
            "recommended_disposition": disposition,
            "blocking_reasons": [] if disposition == "admit" else ["test:blocker"],
        }

    def _programme_summary(
        self,
        entries: tuple[object, ...],
        *,
        evaluated_at: str = "2026-08-16",
        overrides: dict[str, dict[str, object]] | None = None,
    ) -> dict[str, object]:
        overrides = overrides or {}
        rows: list[dict[str, object]] = []
        snapshot_lines: list[str] = []
        for entry in entries:
            name = entry.name
            digest = entry.content_sha256 or ""
            override = overrides.get(name, {})
            recorded_digest = str(override.get("content_sha256", digest))
            snapshot_lines.append(f"{name}:{recorded_digest}\n")
            row: dict[str, object] = {
                "skill_id": name,
                "content_sha256": recorded_digest,
                "catalogue_status": "active",
                "structural_status": "pass",
                "structural_evidence": {
                    "file_count": 1,
                    "total_bytes": 1,
                    "skill_md_lines": 5,
                    "symlink_count": 0,
                },
                "repo_adoption_status": "not_recorded",
                "tracked_definition_status": "missing",
                "behavioral_status": "not_observable",
                "compatibility_status": "partial",
                "human_review_status": "pending",
                "recommendation": "defer",
                "blocking_reasons": ["isolated_behavioral_runner_unavailable"],
                "prior_issue_54_status": "not_in_cohort",
            }
            row.update(override)
            rows.append(row)
        covered = len(rows)
        return {
            "schema_version": 1,
            "issue": 55,
            "evaluated_at": evaluated_at,
            "source_revision": "f" * 40,
            "catalogue_root": "test-catalogue",
            "catalogue_snapshot_sha256": hashlib.sha256(
                "".join(sorted(snapshot_lines)).encode("utf-8")
            ).hexdigest(),
            "owner": "chatgpt-skill evaluation programme",
            "evaluation_standard": "docs/testing/skill-evaluation-standard.md",
            "global_limitations": ["isolated_behavioral_runner_unavailable"],
            "coverage": {
                "total_catalogue_count": covered,
                "active_count": covered,
                "current_covered_count": covered,
                "current_coverage": 1.0 if covered else 0.0,
                "defer_count": sum(row["recommendation"] == "defer" for row in rows),
                "suspend_count": sum(row["recommendation"] == "suspend" for row in rows),
            },
            "skills": rows,
            "re_evaluation": {
                "owner": "chatgpt-skill evaluation programme",
                "max_age_days": 90,
                "triggers": ["canonical skill content hash changes"],
            },
        }

    def _write_programme_summary(self, repo: Path, payload: dict[str, object]) -> Path:
        target = repo / "docs" / "testing" / "full-catalogue-skill-evaluation.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload), encoding="utf-8")
        return target

    def _write_project_binding(self, repo: Path) -> None:
        source = ROOT / "settings" / "projects" / "chatgpt-skill.json"
        target = repo / "settings" / "projects" / "chatgpt-skill.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    def _source_issue_export(self, path: Path, open_numbers: list[int]) -> Path:
        issues = [
            {
                "number": number,
                "state": "open",
                "url": f"https://github.com/NielPieterse0/chatgpt-skill/issues/{number}",
            }
            for number in open_numbers
        ]
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "scope": "open_issues",
                    "repository": "NielPieterse0/chatgpt-skill",
                    "complete": True,
                    "truncated": False,
                    "issues": issues,
                }
            ),
            encoding="utf-8",
        )
        return path

    def _schema_status_export(
        self,
        path: Path,
        *,
        fields_ready: bool = True,
        missing_fields: list[str] | None = None,
        type_mismatches: list[str] | None = None,
        missing_options: list[str] | None = None,
    ) -> Path:
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_id": "chatgpt-skill",
                    "ready": False,
                    "fields_ready": fields_ready,
                    "views_ready": False,
                    "missing_fields": missing_fields or [],
                    "type_mismatches": type_mismatches or [],
                    "missing_options": missing_options or [],
                }
            ),
            encoding="utf-8",
        )
        return path

    def _work_contract_export(self, path: Path) -> Path:
        config = json.loads(
            (ROOT / "settings" / "projects" / "chatgpt-skill.json").read_text(encoding="utf-8")
        )
        fingerprints = config["work_management"]["contract_fingerprints"]
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "canonical_contracts": {"fingerprints": fingerprints},
                }
            ),
            encoding="utf-8",
        )
        return path

    def _telemetry_db(self, path: Path) -> None:
        connection = sqlite3.connect(path)
        try:
            connection.execute(
                """
                CREATE TABLE skill_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    skill_id TEXT,
                    snapshot_id TEXT,
                    content_sha256 TEXT,
                    project_id TEXT,
                    activation_id TEXT,
                    request_id TEXT,
                    outcome TEXT NOT NULL,
                    duration_ms INTEGER,
                    error_class TEXT,
                    total_tokens INTEGER,
                    tool_calls INTEGER,
                    retries INTEGER,
                    verification_passed INTEGER
                )
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _event(
        self,
        path: Path,
        *,
        name: str,
        digest: str,
        event: str,
        occurred_at: str,
        project: str | None = "chatgpt-skill",
        outcome: str = "success",
    ) -> None:
        connection = sqlite3.connect(path)
        try:
            connection.execute(
                """
                INSERT INTO skill_events (
                    occurred_at, event_name, source, skill_id, content_sha256,
                    project_id, outcome
                ) VALUES (?, ?, 'observed', ?, ?, ?, ?)
                """,
                (occurred_at, event, name, digest, project, outcome),
            )
            connection.commit()
        finally:
            connection.close()

    def test_discovers_scalar_and_folded_frontmatter_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "catalogue root"
            root.mkdir()
            self._skill(root, "zeta")
            self._skill(
                root,
                "alpha",
                description="Use when a task needs\nmultiple folded lines.",
                folded=True,
            )

            inventory = discover_catalog([root])

            self.assertEqual([entry.name for entry in inventory.entries], ["alpha", "zeta"])
            alpha = inventory.entries[0]
            self.assertEqual(alpha.description, "Use when a task needs multiple folded lines.")
            self.assertEqual(alpha.status, "active")
            self.assertEqual(alpha.parse_status, "valid")
            self.assertEqual(len(alpha.content_sha256 or ""), 64)
            self.assertTrue(Path(alpha.source_path).is_absolute())
            self.assertEqual(inventory.warnings, ())

    def test_explicit_status_and_category_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = self._skill(root, "disabled-skill", status="disabled")
            content = (skill / "SKILL.md").read_text(encoding="utf-8")
            content = content.replace("status: disabled", "status: disabled\ncategory: testing")
            (skill / "SKILL.md").write_text(content, encoding="utf-8")

            entry = discover_catalog([root]).entries[0]

            self.assertEqual(entry.status, "disabled")
            self.assertEqual(entry.category, "testing")

    def test_valid_nested_optional_frontmatter_is_ignored_for_inventory_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = self._skill(root, "metadata-skill")
            content = (skill / "SKILL.md").read_text(encoding="utf-8")
            content = content.replace(
                "name: metadata-skill\n",
                'name: metadata-skill\nmetadata:\n  author: example-org\n  version: "1.0"\n',
            )
            (skill / "SKILL.md").write_text(content, encoding="utf-8")

            entry = discover_catalog([root]).entries[0]

            self.assertEqual(entry.parse_status, "valid")
            self.assertEqual(entry.name, "metadata-skill")
            self.assertEqual(entry.description, "Use this skill for dashboard tests.")

    def test_missing_and_malformed_skill_files_are_nonfatal_and_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "missing-entrypoint").mkdir()
            broken = root / "broken"
            broken.mkdir()
            (broken / "SKILL.md").write_text("name: broken\n", encoding="utf-8")
            self._skill(root, "good")

            inventory = discover_catalog([root])

            self.assertEqual([entry.name for entry in inventory.entries], ["broken", "good"])
            bad = inventory.entries[0]
            self.assertEqual(bad.parse_status, "invalid")
            self.assertEqual(bad.status, "invalid")
            self.assertTrue(any("frontmatter" in warning for warning in bad.warnings))
            self.assertTrue(any("missing SKILL.md" in warning for warning in inventory.warnings))

    def test_multiple_roots_use_first_root_precedence_and_warn_on_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            first = base / "first"
            second = base / "second"
            first.mkdir()
            second.mkdir()
            self._skill(first, "shared", description="first description")
            self._skill(second, "shared", description="second description")
            self._skill(second, "second-only")

            inventory = discover_catalog([first, second])

            self.assertEqual([entry.name for entry in inventory.entries], ["second-only", "shared"])
            shared = next(entry for entry in inventory.entries if entry.name == "shared")
            self.assertEqual(shared.description, "first description")
            self.assertTrue(any("duplicate" in warning for warning in shared.warnings))

    def test_missing_root_is_nonfatal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            missing = Path(raw) / "does-not-exist"

            inventory = discover_catalog([missing])

            self.assertEqual(inventory.entries, ())
            self.assertEqual(inventory.root_statuses, ((str(missing.resolve()), "not_available"),))
            self.assertTrue(any("catalogue root unavailable" in item for item in inventory.warnings))

    def test_symlinked_catalogue_child_is_rejected_without_disclosure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = self._skill(root, "linked-skill")
            original_is_symlink = Path.is_symlink

            def marked_symlink(path: Path) -> bool:
                if path == skill:
                    return True
                return original_is_symlink(path)

            with patch.object(Path, "is_symlink", marked_symlink):
                inventory = discover_catalog([root])

            self.assertEqual(inventory.entries, ())
            self.assertTrue(any("linked catalogue entry rejected" in item for item in inventory.warnings))

    def test_catalogue_file_identity_change_before_open_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = self._skill(root, "raced-skill")
            entrypoint = skill / "SKILL.md"
            original_open = Path.open
            swapped = False

            def swapping_open(path: Path, *args: object, **kwargs: object):
                nonlocal swapped
                if path == entrypoint and not swapped and "b" in str(kwargs.get("mode", args[0] if args else "r")):
                    swapped = True
                    entrypoint.unlink()
                    with original_open(entrypoint, "w", encoding="utf-8") as handle:
                        handle.write("---\nname: raced-skill\ndescription: replacement\n---\n")
                return original_open(path, *args, **kwargs)

            with patch.object(Path, "open", swapping_open):
                inventory = discover_catalog([root])

            self.assertEqual(inventory.entries, ())
            self.assertTrue(any("changed during validation" in item for item in inventory.warnings))

    def test_catalogue_opened_handle_must_remain_in_validated_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = base / "catalog"
            root.mkdir()
            self._skill(root, "alpha")
            escaped = base / "outside" / "SKILL.md"

            with patch("skill_catalog_dashboard.catalog.opened_path", return_value=escaped):
                inventory = discover_catalog([root])

            self.assertEqual(inventory.entries, ())
            self.assertTrue(any("escaped validated catalogue directory" in item for item in inventory.warnings))

    def test_repository_adoption_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            manifest_dir = repo / "skills" / "alpha"
            manifest_dir.mkdir(parents=True)
            manifest = manifest_dir / "adoption-manifest.json"
            manifest.write_text(
                json.dumps({"skill": "alpha", "approval": {"status": "approved"}}),
                encoding="utf-8",
            )
            original_is_symlink = Path.is_symlink

            def marked_symlink(path: Path) -> bool:
                if path == manifest:
                    return True
                return original_is_symlink(path)

            with patch.object(Path, "is_symlink", marked_symlink):
                evidence = collect_repository_evidence(repo, [entry])["alpha"]

            self.assertEqual(evidence.adoption_status, "invalid")
            self.assertTrue(any("linked" in item for item in evidence.warnings))

    def test_repository_opened_handle_must_remain_in_repo_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            manifest_dir = repo / "skills" / "alpha"
            manifest_dir.mkdir(parents=True)
            manifest = manifest_dir / "adoption-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "skill": "alpha",
                        "source": {"adopted_content_sha256": "a" * 64},
                        "approval": {"status": "approved"},
                    }
                ),
                encoding="utf-8",
            )
            escaped = base / "outside" / "adoption-manifest.json"

            with patch("skill_catalog_dashboard.repo.opened_path", return_value=escaped):
                evidence = collect_repository_evidence(repo, [entry])["alpha"]

            self.assertEqual(evidence.adoption_status, "invalid")
            self.assertTrue(any("escaped repository boundary" in item for item in evidence.warnings))

    def test_repository_adoption_contract_rejects_bad_status_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            manifest_dir = repo / "skills" / "alpha"
            manifest_dir.mkdir(parents=True)
            manifest = manifest_dir / "adoption-manifest.json"

            for status, digest in (("pending", "a" * 64), ("approved", "not-a-sha256")):
                with self.subTest(status=status, digest=digest):
                    manifest.write_text(
                        json.dumps(
                            {
                                "schema_version": 2,
                                "skill": "alpha",
                                "source": {"adopted_content_sha256": digest},
                                "approval": {"status": status},
                            }
                        ),
                        encoding="utf-8",
                    )
                    evidence = collect_repository_evidence(repo, [entry])["alpha"]
                    self.assertEqual(evidence.adoption_status, "invalid")
                    self.assertIsNone(evidence.adopted_content_sha256)
                    self.assertTrue(evidence.warnings)

    def test_repository_adoption_identity_change_before_open_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            manifest_dir = repo / "skills" / "alpha"
            manifest_dir.mkdir(parents=True)
            manifest = manifest_dir / "adoption-manifest.json"
            manifest.write_text(
                json.dumps({"skill": "alpha", "approval": {"status": "approved"}}),
                encoding="utf-8",
            )
            original_open = Path.open
            swapped = False

            def swapping_open(path: Path, *args: object, **kwargs: object):
                nonlocal swapped
                if path == manifest and not swapped:
                    swapped = True
                    manifest.unlink()
                    with original_open(manifest, "w", encoding="utf-8") as handle:
                        handle.write(json.dumps({"skill": "alpha", "approval": {"status": "replaced"}}))
                return original_open(path, *args, **kwargs)

            with patch.object(Path, "open", swapping_open):
                evidence = collect_repository_evidence(repo, [entry])["alpha"]

            self.assertEqual(evidence.adoption_status, "invalid")
            self.assertTrue(any("changed during validation" in item for item in evidence.warnings))

    def test_repository_evidence_selects_latest_iteration_and_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog_root = base / "catalog"
            repo_root = base / "repo"
            catalog_root.mkdir()
            repo_root.mkdir()
            self._skill(catalog_root, "alpha")
            entry = discover_catalog([catalog_root]).entries[0]
            manifest_dir = repo_root / "skills" / "alpha"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "adoption-manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "skill": "alpha",
                        "source": {"adopted_content_sha256": "a" * 64},
                        "approval": {"status": "approved"},
                    }
                ),
                encoding="utf-8",
            )
            for iteration, disposition in ((1, "admit"), (2, "revise")):
                target = repo_root / ".work" / "evals" / "alpha" / f"iteration-{iteration}"
                target.mkdir(parents=True)
                (target / "scorecard.json").write_text(
                    json.dumps(
                        self._scorecard(
                            "alpha",
                            entry.content_sha256 or "",
                            disposition=disposition,
                            verified_at=f"2026-08-{10 + iteration:02d}",
                        )
                    ),
                    encoding="utf-8",
                )

            evidence = collect_repository_evidence(repo_root, [entry])["alpha"]

            self.assertEqual(evidence.adoption_status, "approved")
            self.assertEqual(evidence.adopted_content_sha256, "a" * 64)
            self.assertEqual(evidence.evaluation_status, "revise")
            self.assertEqual(evidence.evaluation_disposition, "revise")
            self.assertEqual(evidence.last_evaluated_at, "2026-08-12")
            self.assertTrue(evidence.evaluation_path.endswith("iteration-2\\scorecard.json") or evidence.evaluation_path.endswith("iteration-2/scorecard.json"))

    def test_tracked_programme_defers_provide_current_hash_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            self._skill(catalog, "beta")
            entries = discover_catalog([catalog]).entries
            programme = self._programme_summary(entries)
            self._write_programme_summary(repo, programme)

            payload = report_to_dict(
                build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )

            self.assertEqual(payload["summary"]["repo_evaluated_count"], 2)
            self.assertEqual(payload["summary"]["evaluation_coverage"], 1.0)
            self.assertEqual(payload["summary"]["defer_count"], 2)
            rows = {item["name"]: item for item in payload["skills"]}
            self.assertEqual(rows["alpha"]["evaluation_status"], "defer")
            self.assertTrue(rows["alpha"]["evaluation_path"].endswith("full-catalogue-skill-evaluation.json"))

    def test_tracked_programme_hash_drift_is_stale_and_excluded_from_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            self._skill(catalog, "beta")
            entries = discover_catalog([catalog]).entries
            programme = self._programme_summary(
                entries, overrides={"alpha": {"content_sha256": "0" * 64}}
            )
            self._write_programme_summary(repo, programme)

            payload = report_to_dict(
                build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )

            self.assertEqual(payload["summary"]["repo_evaluated_count"], 1)
            self.assertEqual(payload["summary"]["evaluation_coverage"], 0.5)
            self.assertEqual(payload["summary"]["stale_evaluation_count"], 1)
            rows = {item["name"]: item for item in payload["skills"]}
            self.assertEqual(rows["alpha"]["evaluation_status"], "stale")
            self.assertTrue(any("programme" in item and "hash" in item for item in rows["alpha"]["warnings"]))

    def test_expired_tracked_programme_summary_is_stale_and_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entries = discover_catalog([catalog]).entries
            programme = self._programme_summary(entries, evaluated_at="2000-01-01")
            self._write_programme_summary(repo, programme)

            payload = report_to_dict(
                build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )

            self.assertEqual(payload["summary"]["repo_evaluated_count"], 0)
            self.assertEqual(payload["summary"]["stale_evaluation_count"], 1)
            self.assertEqual(payload["summary"]["evaluation_coverage"], 0.0)
            self.assertTrue(any("evidence age" in item for item in payload["skills"][0]["warnings"]))

    def test_malformed_tracked_programme_summary_cannot_inflate_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entries = discover_catalog([catalog]).entries
            programme = self._programme_summary(entries)
            programme["coverage"]["current_covered_count"] = 99
            self._write_programme_summary(repo, programme)

            payload = report_to_dict(
                build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )

            self.assertEqual(payload["summary"]["repo_evaluated_count"], 0)
            self.assertEqual(payload["summary"]["evaluation_coverage"], 0.0)
            self.assertTrue(any("programme evaluation summary invalid" in item for item in payload["skills"][0]["warnings"]))

    def test_current_generated_scorecard_overrides_tracked_programme_defer(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            self._write_programme_summary(repo, self._programme_summary((entry,)))
            target = repo / ".work" / "evals" / "alpha" / "iteration-1"
            target.mkdir(parents=True)
            (target / "scorecard.json").write_text(
                json.dumps(self._scorecard("alpha", entry.content_sha256 or "", disposition="admit")),
                encoding="utf-8",
            )

            evidence = collect_repository_evidence(repo, [entry])["alpha"]

            self.assertEqual(evidence.evaluation_status, "admit")
            self.assertEqual(evidence.evaluation_disposition, "admit")
            self.assertTrue(evidence.evaluation_path.endswith("scorecard.json"))

    def test_stale_generated_scorecard_is_excluded_from_current_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            target = repo / ".work" / "evals" / "alpha" / "iteration-1"
            target.mkdir(parents=True)
            (target / "scorecard.json").write_text(
                json.dumps(self._scorecard("alpha", "0" * 64, disposition="defer")),
                encoding="utf-8",
            )

            payload = report_to_dict(
                build_report([catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )

            self.assertEqual(payload["summary"]["stale_evaluation_count"], 1)
            self.assertEqual(payload["summary"]["repo_evaluated_count"], 0)
            self.assertEqual(payload["summary"]["evaluation_coverage"], 0.0)

    def test_incomplete_evaluation_json_cannot_inflate_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            target = repo / ".work" / "evals" / "alpha" / "iteration-1"
            target.mkdir(parents=True)
            (target / "unrelated.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "skill_id": "alpha",
                        "runtime_content_sha256": entry.content_sha256,
                        "recommended_disposition": "admit",
                        "blocking_reasons": [],
                        "evaluation": {"target_verified_at": "2026-08-15"},
                    }
                ),
                encoding="utf-8",
            )

            evidence = collect_repository_evidence(repo, [entry])["alpha"]

            self.assertEqual(evidence.evaluation_status, "not_recorded")
            self.assertIsNone(evidence.evaluation_disposition)

    def test_incomplete_nested_scorecard_objects_cannot_inflate_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            target = repo / ".work" / "evals" / "alpha" / "iteration-2"
            target.mkdir(parents=True)

            cases = []
            empty_dimension = self._scorecard("alpha", entry.content_sha256 or "")
            empty_dimension["dimensions"]["output_quality"] = {}
            cases.append(empty_dimension)
            empty_provenance = self._scorecard("alpha", entry.content_sha256 or "")
            empty_provenance["evaluation"]["definition_provenance"] = {}
            cases.append(empty_provenance)

            for index, scorecard in enumerate(cases):
                with self.subTest(index=index):
                    path = target / f"scorecard-{index}.json"
                    path.write_text(json.dumps(scorecard), encoding="utf-8")
                    evidence = collect_repository_evidence(repo, [entry])["alpha"]
                    self.assertEqual(evidence.evaluation_status, "not_recorded")
                    path.unlink()

    def test_repository_evidence_marks_hash_mismatch_stale_and_missing_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog_root = base / "catalog"
            repo_root = base / "repo"
            catalog_root.mkdir()
            repo_root.mkdir()
            self._skill(catalog_root, "alpha")
            self._skill(catalog_root, "beta")
            entries = discover_catalog([catalog_root]).entries
            target = repo_root / ".work" / "evals" / "alpha" / "iteration-3"
            target.mkdir(parents=True)
            (target / "result.json").write_text(
                json.dumps(
                    self._scorecard(
                        "alpha",
                        "f" * 64,
                        disposition="defer",
                        verified_at="2026-08-13",
                    )
                ),
                encoding="utf-8",
            )

            evidence = collect_repository_evidence(repo_root, entries)

            self.assertEqual(evidence["alpha"].evaluation_status, "stale")
            self.assertEqual(evidence["alpha"].evaluation_disposition, "defer")
            self.assertTrue(any("hash" in item for item in evidence["alpha"].warnings))
            self.assertEqual(evidence["beta"].adoption_status, "not_recorded")
            self.assertEqual(evidence["beta"].evaluation_status, "not_recorded")

    def test_repository_evidence_degrades_unreadable_eval_directory_to_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            entry = discover_catalog([catalog]).entries[0]
            eval_root = repo / ".work" / "evals" / "alpha"
            eval_root.mkdir(parents=True)

            original_iterdir = Path.iterdir

            def guarded_iterdir(path: Path):
                if path == eval_root:
                    raise OSError("permission denied")
                return original_iterdir(path)

            with patch.object(Path, "iterdir", guarded_iterdir):
                evidence = collect_repository_evidence(repo, [entry])["alpha"]

            self.assertEqual(evidence.evaluation_status, "invalid")
            self.assertTrue(any("unreadable" in item for item in evidence.warnings))

    def test_evaluation_candidate_order_is_total_for_case_colliding_paths(self) -> None:
        upper = _candidate_order_key(2, 2, Path("A/scorecard.json"))
        lower = _candidate_order_key(2, 2, Path("a/scorecard.json"))

        self.assertNotEqual(upper, lower)
        self.assertEqual(sorted([lower, upper]), sorted([upper, lower]))

    def test_sqlite_telemetry_aggregates_current_version_and_last_used(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            db = Path(raw) / "skills.sqlite3"
            self._telemetry_db(db)
            digest = "b" * 64
            self._event(db, name="alpha", digest=digest, event="skill_discovered", occurred_at="2026-08-15T10:00:00+00:00")
            self._event(db, name="alpha", digest=digest, event="skill_loaded", occurred_at="2026-08-15T11:00:00+00:00")
            self._event(db, name="alpha", digest=digest, event="skill_resource_read", occurred_at="2026-08-15T11:02:00+00:00")
            self._event(db, name="alpha", digest=digest, event="skill_applied", occurred_at="2026-08-15T11:03:00+00:00")
            self._event(db, name="alpha", digest=digest, event="skill_completed", occurred_at="2026-08-15T11:04:00+00:00")
            self._event(db, name="alpha", digest=digest, event="skill_failed", occurred_at="2026-08-15T11:05:00+00:00", outcome="failed")

            snapshot = load_telemetry_sqlite(db)
            group = snapshot.by_identity[("alpha", digest)]

            self.assertEqual(snapshot.status, "observed")
            self.assertEqual(group.discovered_count, 1)
            self.assertEqual(group.loaded_count, 1)
            self.assertEqual(group.resource_read_count, 1)
            self.assertEqual(group.applied_count, 1)
            self.assertEqual(group.completed_count, 1)
            self.assertEqual(group.failed_count, 1)
            self.assertEqual(group.error_count, 1)
            self.assertEqual(group.last_used_at, "2026-08-15T11:05:00+00:00")
            self.assertEqual(group.last_used_status, "observed")
            self.assertEqual(group.projects, ("chatgpt-skill",))

    def test_sqlite_last_used_compares_timestamp_instants_not_text_offsets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            db = Path(raw) / "skills.sqlite3"
            self._telemetry_db(db)
            digest = "e" * 64
            self._event(
                db,
                name="alpha",
                digest=digest,
                event="skill_loaded",
                occurred_at="2026-08-15T13:30:00+02:00",
            )
            self._event(
                db,
                name="alpha",
                digest=digest,
                event="skill_loaded",
                occurred_at="2026-08-15T12:00:00+00:00",
            )

            group = load_telemetry_sqlite(db).by_identity[("alpha", digest)]

            self.assertEqual(group.last_used_at, "2026-08-15T12:00:00+00:00")

    def test_sqlite_retention_bound_is_reported_as_truncated(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            db = Path(raw) / "skills.sqlite3"
            self._telemetry_db(db)
            connection = sqlite3.connect(db)
            try:
                connection.executemany(
                    """
                    INSERT INTO skill_events (
                        occurred_at, event_name, source, skill_id, content_sha256,
                        project_id, outcome
                    ) VALUES ('2026-08-15T10:00:00+00:00', 'skill_discovered', 'observed', ?, ?, 'chatgpt-skill', 'success')
                    """,
                    (("alpha", "f" * 64) for _ in range(20_000)),
                )
                connection.commit()
            finally:
                connection.close()

            snapshot = load_telemetry_sqlite(db)

            self.assertEqual(snapshot.status, "truncated")
            self.assertEqual(snapshot.event_count, 20_000)
            self.assertTrue(any("retention bound" in item for item in snapshot.warnings))

    def test_telemetry_json_preserves_truncation_and_last_used_unobservability(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "telemetry.json"
            digest = "c" * 64
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "event_count": 9,
                        "truncated": True,
                        "groups": [
                            {
                                "skill_id": "alpha",
                                "content_sha256": digest,
                                "project_id": "one",
                                "discovered_count": 2,
                                "loaded_count": 3,
                                "resource_read_count": 1,
                                "evaluated_count": 0,
                                "mutation_count": 0,
                                "applied_count": 1,
                                "completed_count": 1,
                                "failed_count": 0,
                                "error_count": 0,
                                "duration_samples": 0,
                                "total_duration_ms": None,
                                "token_samples": 0,
                                "total_tokens": None,
                                "tool_call_samples": 0,
                                "total_tool_calls": None,
                                "retry_samples": 0,
                                "total_retries": None,
                                "verification_samples": 0,
                                "verification_passes": None,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            snapshot = load_telemetry_json(path)
            group = snapshot.by_identity[("alpha", digest)]

            self.assertEqual(snapshot.status, "truncated")
            self.assertTrue(any("truncated" in item for item in snapshot.warnings))
            self.assertEqual(group.loaded_count, 3)
            self.assertEqual(group.last_used_status, "not_observable")
            self.assertIsNone(group.last_used_at)

    def test_truncated_telemetry_rows_preserve_incomplete_status(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            path = base / "telemetry.json"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            self._skill(catalog, "beta")
            entries = discover_catalog([catalog]).entries
            alpha = next(item for item in entries if item.name == "alpha")
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "event_count": 3,
                        "truncated": True,
                        "groups": [
                            {
                                "skill_id": "alpha",
                                "content_sha256": alpha.content_sha256,
                                "project_id": "chatgpt-skill",
                                "discovered_count": 1,
                                "loaded_count": 2,
                                "resource_read_count": 0,
                                "evaluated_count": 0,
                                "mutation_count": 0,
                                "applied_count": 0,
                                "completed_count": 0,
                                "failed_count": 0,
                                "error_count": 0,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = report_to_dict(
                build_report([catalog], repo_root=repo, telemetry_json=path)
            )
            rows = {item["name"]: item for item in payload["skills"]}

            self.assertEqual(rows["alpha"]["telemetry"]["status"], "observed_incomplete")
            self.assertEqual(rows["alpha"]["telemetry"]["loaded_count"], 2)
            self.assertEqual(
                rows["beta"]["telemetry"]["status"],
                "not_observable_due_to_truncation",
            )
            self.assertEqual(rows["beta"]["telemetry"]["last_used_status"], "not_observable")
            self.assertNotIn("loaded_count", rows["beta"]["telemetry"])

    def test_telemetry_json_rejects_unsupported_schema_and_malformed_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "telemetry.json"
            cases = (
                {
                    "schema_version": 2,
                    "event_count": 0,
                    "truncated": False,
                    "groups": [],
                },
                {
                    "schema_version": 1,
                    "event_count": 1,
                    "truncated": False,
                    "groups": [
                        {
                            "skill_id": None,
                            "content_sha256": "a" * 64,
                            **{field: 0 for field in (
                                "discovered_count", "loaded_count", "resource_read_count",
                                "evaluated_count", "mutation_count", "applied_count",
                                "completed_count", "failed_count", "error_count"
                            )},
                        }
                    ],
                },
            )
            for payload in cases:
                with self.subTest(payload=payload):
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    snapshot = load_telemetry_json(path)
                    self.assertEqual(snapshot.status, "invalid")
                    self.assertTrue(snapshot.warnings)

    def test_missing_or_invalid_telemetry_is_nonfatal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            missing = load_telemetry_sqlite(base / "missing.sqlite3")
            self.assertEqual(missing.status, "not_available")
            invalid = base / "invalid.sqlite3"
            sqlite3.connect(invalid).close()
            malformed = load_telemetry_sqlite(invalid)
            self.assertEqual(malformed.status, "invalid")
            self.assertTrue(malformed.warnings)


    def test_work_management_snapshot_projects_issue_backed_lifecycle_work(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "work.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "result": {
                            "schema_version": 1,
                            "project_id": "chatgpt-skill",
                            "repository": "nielpieterse0/chatgpt-skill",
                            "complete": True,
                            "truncated": False,
                            "include_history": True,
                            "next_eligible_item_id": "item-79",
                            "cards": [
                                {
                                    "item_id": "item-85",
                                    "repository": "NielPieterse0/chatgpt-skill",
                                    "number": 85,
                                    "title": "Evaluation runner",
                                    "source_state": "open",
                                    "work_state": "ready",
                                    "execution_owner": None,
                                    "priority": "high",
                                    "effort": "large",
                                    "blocked_by": None,
                                    "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/85",
                                },
                                {
                                    "item_id": "item-79",
                                    "repository": "NielPieterse0/chatgpt-skill",
                                    "number": 79,
                                    "title": "Lifecycle queue",
                                    "source_state": "open",
                                    "work_state": "ready",
                                    "execution_owner": None,
                                    "priority": "high",
                                    "effort": "medium",
                                    "blocked_by": None,
                                    "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/79",
                                },
                                {
                                    "item_id": "item-93",
                                    "repository": "NielPieterse0/chatgpt-skill",
                                    "number": 93,
                                    "title": "External experiment",
                                    "source_state": "open",
                                    "work_state": "blocked",
                                    "execution_owner": None,
                                    "priority": "high",
                                    "effort": "small",
                                    "blocked_by": "external capability",
                                    "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/93",
                                },
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )

            source = self._source_issue_export(Path(raw) / "issues.json", [79, 85, 93])
            schema = self._schema_status_export(Path(raw) / "schema-status.json")
            contract = self._work_contract_export(Path(raw) / "work-contract.json")
            snapshot = load_work_management_json(
                path,
                source_issues_json=source,
                schema_status_json=schema,
                contract_json=contract,
            )

            self.assertEqual(snapshot.status, "observed")
            self.assertEqual([item.number for item in snapshot.items], [79, 85, 93])
            self.assertEqual(snapshot.items[2].source_state, "open")
            self.assertEqual(snapshot.items[2].work_state, "blocked")
            self.assertEqual(snapshot.items[2].priority, "high")

    def test_work_management_snapshot_rejects_non_v1_outer_envelopes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "work.json"
            result = {
                "schema_version": 1,
                "project_id": "chatgpt-skill",
                "repository": "NielPieterse0/chatgpt-skill",
                "complete": True,
                "truncated": False,
                "include_history": True,
                "cards": [],
            }
            envelopes = ({}, {"schema_version": True}, {"schema_version": "1"}, {"schema_version": 2})
            for envelope in envelopes:
                with self.subTest(envelope=envelope):
                    path.write_text(json.dumps({**envelope, "result": result}), encoding="utf-8")
                    snapshot = load_work_management_json(path)
                    self.assertEqual(snapshot.status, "invalid")
                    self.assertEqual(snapshot.items, ())
                    self.assertTrue(any("envelope schema_version" in item for item in snapshot.warnings))

    def test_work_management_snapshot_rejects_non_v1_supporting_evidence(self) -> None:
        invalid_versions = (
            ("missing", None),
            ("boolean-true", True),
            ("boolean-false", False),
            ("string", "1"),
            ("zero", 0),
            ("version-two", 2),
        )
        for target in ("work", "source", "schema", "contract"):
            for label, version in invalid_versions:
                with self.subTest(target=target, version=label), tempfile.TemporaryDirectory() as raw:
                    base = Path(raw)
                    work = base / "work.json"
                    work.write_text(json.dumps({
                        "schema_version": 1,
                        "project_id": "chatgpt-skill",
                        "repository": "NielPieterse0/chatgpt-skill",
                        "complete": True,
                        "truncated": False,
                        "include_history": True,
                        "cards": [],
                    }), encoding="utf-8")
                    source = self._source_issue_export(base / "issues.json", [])
                    schema = self._schema_status_export(base / "schema.json")
                    contract = self._work_contract_export(base / "contract.json")
                    selected = {"work": work, "source": source, "schema": schema, "contract": contract}[target]
                    payload = json.loads(selected.read_text(encoding="utf-8"))
                    if label == "missing":
                        payload.pop("schema_version")
                    else:
                        payload["schema_version"] = version
                    selected.write_text(json.dumps(payload), encoding="utf-8")

                    snapshot = load_work_management_json(
                        work,
                        source_issues_json=source,
                        schema_status_json=schema,
                        contract_json=contract,
                    )

                    self.assertEqual(snapshot.status, "invalid")
                    self.assertEqual(snapshot.items, ())
                    self.assertTrue(any("schema_version" in item for item in snapshot.warnings))

    def test_work_management_snapshot_rejects_foreign_scope_and_preserves_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "work.json"
            base = {
                "schema_version": 1,
                "project_id": "chatgpt-skill",
                "repository": "nielpieterse0/chatgpt-skill",
                "complete": False,
                "truncated": True,
                "next_eligible_item_id": "partial-ready",
                "cards": [
                    {
                        "item_id": "partial-ready",
                        "repository": "NielPieterse0/chatgpt-skill",
                        "number": 85,
                        "title": "Partial ready work",
                        "source_state": "open",
                        "work_state": "ready",
                        "priority": "high",
                        "effort": "large",
                        "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/85",
                    }
                ],
            }
            path.write_text(json.dumps(base), encoding="utf-8")
            incomplete = load_work_management_json(path)
            self.assertEqual(incomplete.status, "incomplete")
            self.assertEqual(incomplete.items, ())
            self.assertTrue(incomplete.warnings)

            base["complete"] = True
            base["truncated"] = False
            base["next_eligible_item_id"] = None
            base["cards"] = [
                {
                    "item_id": "foreign",
                    "repository": "NielPieterse0/kis-mcp",
                    "number": 1,
                    "title": "wrong repository",
                    "source_state": "open",
                    "work_state": "ready",
                    "url": "https://github.com/NielPieterse0/kis-mcp/issues/1",
                }
            ]
            path.write_text(json.dumps(base), encoding="utf-8")
            invalid = load_work_management_json(path)
            self.assertEqual(invalid.status, "invalid")
            self.assertEqual(invalid.items, ())

    def test_work_management_snapshot_requires_explicit_boolean_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "work.json"
            base = {
                "schema_version": 1,
                "project_id": "chatgpt-skill",
                "repository": "nielpieterse0/chatgpt-skill",
                "complete": True,
                "next_eligible_item_id": None,
                "cards": [],
            }
            for value in (None, "false", 0):
                with self.subTest(truncated=value):
                    payload = dict(base)
                    payload["truncated"] = value
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    snapshot = load_work_management_json(path)
                    self.assertEqual(snapshot.status, "invalid")
                    self.assertEqual(snapshot.items, ())
            path.write_text(json.dumps(base), encoding="utf-8")
            missing = load_work_management_json(path)
            self.assertEqual(missing.status, "invalid")
            self.assertEqual(missing.items, ())

    def test_work_management_snapshot_preserves_kis_owned_lifecycle_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "work.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "chatgpt-skill",
                        "repository": "nielpieterse0/chatgpt-skill",
                        "complete": True,
                        "truncated": False,
                        "include_history": True,
                        "next_eligible_item_id": "kis-next",
                        "cards": [
                            {
                                "item_id": "kis-next",
                                "repository": "NielPieterse0/chatgpt-skill",
                                "number": 87,
                                "title": "KIS-owned lifecycle values",
                                "source_state": "open",
                                "work_state": "future-kis-state",
                                "priority": "future-priority",
                                "effort": "future-effort",
                                "execution_owner": "kis-owner",
                                "blocked_by": "KIS dependency expression",
                                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/87",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            snapshot = load_work_management_json(path)

            self.assertEqual(snapshot.status, "unverified")
            self.assertEqual(len(snapshot.items), 1)
            self.assertTrue(snapshot.warnings)
            item = snapshot.items[0]
            self.assertEqual(item.work_state, "future-kis-state")
            self.assertEqual(item.priority, "future-priority")
            self.assertEqual(item.effort, "future-effort")
            self.assertEqual(item.execution_owner, "kis-owner")
            self.assertEqual(item.blocked_by, "KIS dependency expression")

    def test_work_management_snapshot_validates_identity_not_kis_policy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "work.json"
            card = {
                "item_id": "item-85",
                "repository": "NielPieterse0/chatgpt-skill",
                "number": 85,
                "title": "Work item",
                "source_state": "open",
                "work_state": "future-state",
                "priority": "future-priority",
                "effort": "future-effort",
                "blocked_by": "future-dependency",
                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/85",
            }
            base = {
                "schema_version": 1,
                "project_id": "chatgpt-skill",
                "repository": "nielpieterse0/chatgpt-skill",
                "complete": True,
                "truncated": False,
                "include_history": True,
                "next_eligible_item_id": "item-85",
            }
            path.write_text(json.dumps({**base, "cards": [card]}), encoding="utf-8")
            observed = load_work_management_json(path)
            self.assertEqual(observed.status, "unverified")
            self.assertEqual(observed.items[0].work_state, "future-state")
            self.assertEqual(observed.items[0].priority, "future-priority")
            self.assertEqual(observed.items[0].effort, "future-effort")

            duplicate_item = {
                **card,
                "number": 86,
                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/86",
            }
            path.write_text(json.dumps({**base, "cards": [card, duplicate_item]}), encoding="utf-8")
            self.assertEqual(load_work_management_json(path).status, "invalid")

            duplicate_issue = {**card, "item_id": "item-other"}
            path.write_text(json.dumps({**base, "cards": [card, duplicate_issue]}), encoding="utf-8")
            self.assertEqual(load_work_management_json(path).status, "invalid")

            stale_next = {**base, "next_eligible_item_id": "missing", "cards": [card]}
            path.write_text(json.dumps(stale_next), encoding="utf-8")
            stale_next_snapshot = load_work_management_json(path)
            self.assertEqual(stale_next_snapshot.status, "unverified")
            self.assertEqual([item.number for item in stale_next_snapshot.items], [85])

            closed = {
                **card,
                "item_id": "closed-109",
                "number": 109,
                "source_state": "closed",
                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/109",
            }
            closed_payload = {**base, "cards": [card, closed]}
            path.write_text(json.dumps(closed_payload), encoding="utf-8")
            closed_snapshot = load_work_management_json(path)
            self.assertEqual(closed_snapshot.status, "unverified")
            self.assertEqual([item.number for item in closed_snapshot.items], [85])

            path.write_text(
                json.dumps({**base, "cards": [card, {**closed, "url": "https://example.invalid/109"}]}),
                encoding="utf-8",
            )
            self.assertEqual(load_work_management_json(path).status, "invalid")

    def test_work_management_source_coverage_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "work.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "chatgpt-skill",
                        "repository": "NielPieterse0/chatgpt-skill",
                        "complete": True,
                        "truncated": False,
                        "include_history": True,
                        "next_eligible_item_id": "item-87",
                        "cards": [
                            {
                                "item_id": "item-87",
                                "repository": "NielPieterse0/chatgpt-skill",
                                "number": 87,
                                "title": "Projected work",
                                "source_state": "open",
                                "work_state": "ready",
                                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/87",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            source = self._source_issue_export(Path(raw) / "issues.json", [87, 88])

            snapshot = load_work_management_json(path, source_issues_json=source)

            self.assertEqual(snapshot.status, "invalid")
            self.assertEqual(snapshot.items, ())
            self.assertTrue(any("missing=[88]" in warning for warning in snapshot.warnings))

            projected = json.loads(path.read_text(encoding="utf-8"))
            projected["cards"].append({
                "item_id": "item-88",
                "repository": "NielPieterse0/chatgpt-skill",
                "number": 88,
                "title": "Extra projected work",
                "source_state": "open",
                "work_state": "ready",
                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/88",
            })
            path.write_text(json.dumps(projected), encoding="utf-8")
            source = self._source_issue_export(Path(raw) / "issues.json", [87])

            extra = load_work_management_json(path, source_issues_json=source)

            self.assertEqual(extra.status, "invalid")
            self.assertEqual(extra.items, ())
            self.assertTrue(any("extra=[88]" in warning for warning in extra.warnings))

    def test_work_management_requires_history_scope_and_kis_field_schema(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            work = base / "work.json"
            payload = {
                "schema_version": 1,
                "project_id": "chatgpt-skill",
                "repository": "NielPieterse0/chatgpt-skill",
                "complete": True,
                "truncated": False,
                "include_history": False,
                "next_eligible_item_id": "item-87",
                "cards": [
                    {
                        "item_id": "item-87",
                        "repository": "NielPieterse0/chatgpt-skill",
                        "number": 87,
                        "title": "Open work",
                        "source_state": "open",
                        "work_state": "ready",
                        "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/87",
                    },
                    {
                        "item_id": "item-109",
                        "repository": "NielPieterse0/chatgpt-skill",
                        "number": 109,
                        "title": "Historical work",
                        "source_state": "closed",
                        "work_state": "done",
                        "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/109",
                    },
                ],
            }
            work.write_text(json.dumps(payload), encoding="utf-8")
            source = self._source_issue_export(base / "issues.json", [87])
            schema = self._schema_status_export(base / "schema-status.json")
            contract = self._work_contract_export(base / "work-contract.json")

            unverified_history = load_work_management_json(
                work,
                source_issues_json=source,
                schema_status_json=schema,
                contract_json=contract,
            )
            self.assertEqual(unverified_history.status, "invalid")
            self.assertEqual(unverified_history.items, ())
            self.assertTrue(any("include_history=true" in warning for warning in unverified_history.warnings))

            payload["include_history"] = True
            work.write_text(json.dumps(payload), encoding="utf-8")
            drifted_schema = self._schema_status_export(
                base / "schema-drift.json",
                fields_ready=False,
                missing_fields=["Priority"],
            )
            schema_drift = load_work_management_json(
                work,
                source_issues_json=source,
                schema_status_json=drifted_schema,
                contract_json=contract,
            )
            self.assertEqual(schema_drift.status, "invalid")
            self.assertTrue(any("missing_fields" in warning for warning in schema_drift.warnings))

            observed = load_work_management_json(
                work,
                source_issues_json=source,
                schema_status_json=schema,
                contract_json=contract,
            )
            self.assertEqual(observed.status, "observed")
            self.assertEqual([item.number for item in observed.items], [87])

            stale_contract = json.loads(contract.read_text(encoding="utf-8"))
            stale_contract["canonical_contracts"]["fingerprints"]["work_selection"] = "0" * 64
            contract.write_text(json.dumps(stale_contract), encoding="utf-8")
            stale = load_work_management_json(
                work,
                source_issues_json=source,
                schema_status_json=schema,
                contract_json=contract,
            )
            self.assertEqual(stale.status, "invalid")
            self.assertTrue(any("fingerprints" in warning for warning in stale.warnings))

            contract = self._work_contract_export(base / "work-contract-extra.json")
            extra_contract = json.loads(contract.read_text(encoding="utf-8"))
            extra_contract["canonical_contracts"]["fingerprints"]["future_contract"] = "d" * 64
            contract.write_text(json.dumps(extra_contract), encoding="utf-8")
            extra = load_work_management_json(
                work,
                source_issues_json=source,
                schema_status_json=schema,
                contract_json=contract,
            )
            self.assertEqual(extra.status, "invalid")
            self.assertTrue(any("repository binding" in warning for warning in extra.warnings))

    def test_work_management_uses_repository_owned_binding(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            repo = base / "repo"
            binding = repo / "settings" / "projects" / "chatgpt-skill.json"
            binding.parent.mkdir(parents=True)
            fingerprints = {
                "work_item_semantics": "a" * 64,
                "work_lifecycle_operations": "b" * 64,
                "work_selection": "c" * 64,
            }
            binding.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "custom-project",
                        "repository": {"full_name": "ExampleOrg/example"},
                        "work_management": {
                            "contract_fingerprints": fingerprints,
                            "source_scope": {
                                "repository": "ExampleOrg/example",
                                "exact_match_required": True,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            work = base / "work.json"
            work.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "custom-project",
                        "repository": "ExampleOrg/example",
                        "complete": True,
                        "truncated": False,
                        "include_history": True,
                        "next_eligible_item_id": "item-4",
                        "cards": [
                            {
                                "item_id": "item-4",
                                "repository": "ExampleOrg/example",
                                "number": 4,
                                "title": "Bound work",
                                "source_state": "open",
                                "work_state": "custom-state",
                                "url": "https://github.com/ExampleOrg/example/issues/4",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            source = base / "issues.json"
            source.write_text(json.dumps({
                "schema_version": 1,
                "scope": "open_issues",
                "repository": "ExampleOrg/example",
                "complete": True,
                "truncated": False,
                "issues": [{
                    "number": 4,
                    "state": "open",
                    "url": "https://github.com/ExampleOrg/example/issues/4",
                }],
            }), encoding="utf-8")
            schema = base / "schema.json"
            schema.write_text(json.dumps({
                "schema_version": 1,
                "project_id": "custom-project",
                "fields_ready": True,
                "missing_fields": [],
                "type_mismatches": [],
                "missing_options": [],
            }), encoding="utf-8")
            contract = base / "contract.json"
            contract.write_text(json.dumps({
                "schema_version": 1,
                "canonical_contracts": {"fingerprints": dict(fingerprints)},
            }), encoding="utf-8")

            snapshot = load_work_management_json(
                work,
                repo_root=repo,
                source_issues_json=source,
                schema_status_json=schema,
                contract_json=contract,
            )

            self.assertEqual(snapshot.status, "observed")
            self.assertEqual(snapshot.items[0].repository, "ExampleOrg/example")
            self.assertEqual(snapshot.items[0].work_state, "custom-state")

    def test_report_projects_work_queue_without_changing_skill_totals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._write_project_binding(repo)
            self._skill(catalog, "alpha")
            work = base / "work.json"
            work.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "chatgpt-skill",
                        "repository": "nielpieterse0/chatgpt-skill",
                        "complete": True,
                        "truncated": False,
                        "include_history": True,
                        "next_eligible_item_id": "plugin",
                        "cards": [
                            {
                                "item_id": "plugin",
                                "repository": "NielPieterse0/chatgpt-skill",
                                "number": 87,
                                "title": "Plugin pilot wiring",
                                "source_state": "open",
                                "work_state": "ready",
                                "priority": "high",
                                "effort": "medium",
                                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/87",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            source = self._source_issue_export(base / "issues.json", [87])
            schema = self._schema_status_export(base / "schema-status.json")
            contract = self._work_contract_export(base / "work-contract.json")

            report = build_report(
                [catalog],
                repo_root=repo,
                telemetry_db=base / "missing.sqlite3",
                work_management_json=work,
                source_issues_json=source,
                work_schema_status_json=schema,
                work_contract_json=contract,
            )
            payload = report_to_dict(report)

            self.assertEqual(payload["schema_version"], 2)
            self.assertEqual(payload["summary"]["total_catalogue_count"], 1)
            self.assertEqual(payload["summary"]["work_item_count"], 1)
            self.assertEqual(payload["summary"]["work_state_counts"], {"ready": 1})
            self.assertEqual(payload["work"][0]["source_issue"]["number"], 87)
            self.assertEqual(payload["work"][0]["source_state"], "open")
            self.assertNotIn("is_next", payload["work"][0])
            html = render_html(report)
            self.assertIn("Lifecycle work queue", html)
            self.assertIn("State: ready", html)
            self.assertIn("Plugin pilot wiring", html)
            self.assertNotIn("Next eligible", html)

    def test_report_keeps_work_counts_null_when_source_coverage_is_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._write_project_binding(repo)
            self._skill(catalog, "alpha")
            work = base / "work.json"
            work.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "chatgpt-skill",
                        "repository": "NielPieterse0/chatgpt-skill",
                        "complete": True,
                        "truncated": False,
                        "include_history": True,
                        "next_eligible_item_id": "item-87",
                        "cards": [
                            {
                                "item_id": "item-87",
                                "repository": "NielPieterse0/chatgpt-skill",
                                "number": 87,
                                "title": "Visible but unverified work",
                                "source_state": "open",
                                "work_state": "ready",
                                "url": "https://github.com/NielPieterse0/chatgpt-skill/issues/87",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = report_to_dict(
                build_report(
                    [catalog],
                    repo_root=repo,
                    telemetry_db=base / "missing.sqlite3",
                    work_management_json=work,
                )
            )

            self.assertEqual(payload["sources"]["work_management"]["status"], "unverified")
            self.assertEqual(len(payload["work"]), 1)
            self.assertNotIn("is_next", payload["work"][0])
            self.assertIsNone(payload["summary"]["work_item_count"])
            self.assertIsNone(payload["summary"]["work_state_counts"])
            html = render_html(
                build_report(
                    [catalog],
                    repo_root=repo,
                    telemetry_db=base / "missing.sqlite3",
                    work_management_json=work,
                )
            )
            self.assertIn("Work projection status: <strong>unverified</strong>", html)
            self.assertIn("Unverified state: ready", html)

    def test_report_aggregates_counts_and_exact_hash_usage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            self._skill(catalog, "beta", status="disabled")
            entries = discover_catalog([catalog]).entries
            alpha = next(item for item in entries if item.name == "alpha")
            beta = next(item for item in entries if item.name == "beta")
            eval_dir = repo / ".work" / "evals" / "alpha" / "iteration-1"
            eval_dir.mkdir(parents=True)
            (eval_dir / "scorecard.json").write_text(
                json.dumps(
                    self._scorecard(
                        "alpha",
                        alpha.content_sha256 or "",
                        disposition="admit",
                        verified_at="2026-08-15",
                    )
                ),
                encoding="utf-8",
            )
            db = base / "skills.sqlite3"
            self._telemetry_db(db)
            self._event(
                db,
                name="alpha",
                digest=alpha.content_sha256 or "",
                event="skill_loaded",
                occurred_at="2026-08-15T12:00:00+00:00",
            )
            self._event(
                db,
                name="beta",
                digest="d" * 64,
                event="skill_loaded",
                occurred_at="2026-08-15T12:01:00+00:00",
            )

            report = build_report([catalog], repo_root=repo, telemetry_db=db)
            payload = report_to_dict(report)

            self.assertEqual(payload["summary"]["total_catalogue_count"], 2)
            self.assertEqual(payload["summary"]["active_count"], 1)
            self.assertEqual(payload["summary"]["repo_evaluated_count"], 1)
            self.assertEqual(payload["summary"]["unevaluated_count"], 1)
            self.assertEqual(payload["summary"]["evaluation_coverage"], 0.5)
            rows = {item["name"]: item for item in payload["skills"]}
            self.assertEqual(rows["alpha"]["telemetry"]["status"], "observed")
            self.assertEqual(rows["alpha"]["telemetry"]["loaded_count"], 1)
            self.assertEqual(rows["beta"]["telemetry"]["status"], "hash_version_not_observed")
            self.assertNotIn("loaded_count", rows["beta"]["telemetry"])
            self.assertTrue(any("other content hash" in item for item in rows["beta"]["warnings"]))

    def test_report_json_is_deterministic_and_missing_repo_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            catalog.mkdir()
            self._skill(catalog, "zeta")
            self._skill(catalog, "alpha")
            missing_repo = base / "missing-repo"
            missing_db = base / "missing.sqlite3"

            report = build_report([catalog], repo_root=missing_repo, telemetry_db=missing_db)

            first = report_to_json(report)
            second = report_to_json(report)
            self.assertEqual(first, second)
            payload = json.loads(first)
            self.assertEqual([item["name"] for item in payload["skills"]], ["alpha", "zeta"])
            self.assertTrue(any("repository evidence unavailable" in item for item in payload["warnings"]))
            self.assertEqual(payload["sources"]["telemetry"]["status"], "not_available")
            self.assertEqual(payload["skills"][0]["telemetry"]["status"], "not_available")
            self.assertNotIn("loaded_count", payload["skills"][0]["telemetry"])

    def test_report_distinguishes_unavailable_catalogue_from_empty_catalogue(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            repo = base / "repo"
            empty_catalog = base / "empty-catalog"
            missing_catalog = base / "missing-catalog"
            repo.mkdir()
            empty_catalog.mkdir()

            empty_payload = report_to_dict(
                build_report([empty_catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )
            missing_payload = report_to_dict(
                build_report([missing_catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3")
            )
            mixed_payload = report_to_dict(
                build_report(
                    [empty_catalog, missing_catalog],
                    repo_root=repo,
                    telemetry_db=base / "missing.sqlite3",
                )
            )

            self.assertEqual(empty_payload["sources"]["catalogue"]["status"], "empty")
            self.assertEqual(missing_payload["sources"]["catalogue"]["status"], "not_available")
            self.assertEqual(mixed_payload["sources"]["catalogue"]["status"], "partial")

    def test_cli_smoke_uses_literal_repo_level_module_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._write_project_binding(repo)
            self._skill(catalog, "alpha")
            work = base / "work.json"
            work.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "chatgpt-skill",
                        "repository": "nielpieterse0/chatgpt-skill",
                        "complete": True,
                        "truncated": False,
                        "include_history": True,
                        "next_eligible_item_id": None,
                        "cards": [],
                    }
                ),
                encoding="utf-8",
            )
            source = self._source_issue_export(base / "issues.json", [])
            schema = self._schema_status_export(base / "schema-status.json")
            contract = self._work_contract_export(base / "work-contract.json")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skill_catalog_dashboard",
                    "--catalog-root",
                    str(catalog),
                    "--repo-root",
                    str(repo),
                    "--telemetry-db",
                    str(base / "missing.sqlite3"),
                    "--work-management-json",
                    str(work),
                    "--source-issues-json",
                    str(source),
                    "--work-schema-status-json",
                    str(schema),
                    "--work-contract-json",
                    str(contract),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["total_catalogue_count"], 1)
            self.assertEqual(payload["skills"][0]["name"], "alpha")
            self.assertEqual(payload["sources"]["work_management"]["status"], "observed")

    def test_web_server_requires_literal_ipv4_loopback_binding(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            report = build_report(
                [catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3"
            )
            for host in ("0.0.0.0", "localhost"):
                with self.subTest(host=host):
                    with patch("skill_catalog_dashboard.web.ThreadingHTTPServer") as server_class:
                        with self.assertRaises(ValueError):
                            make_server(report, host=host, port=0)
                        server_class.assert_not_called()

    def test_web_server_exposes_only_read_only_report_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            repo = base / "repo"
            catalog.mkdir()
            repo.mkdir()
            self._skill(catalog, "alpha")
            report = build_report(
                [catalog], repo_root=repo, telemetry_db=base / "missing.sqlite3"
            )
            self.assertIn("alpha", render_html(report))
            server = make_server(report, host="127.0.0.1", port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base_url = f"http://127.0.0.1:{server.server_address[1]}"
                rebound = urllib.request.Request(base_url + "/api/report")
                rebound.add_unredirected_header("Host", "attacker.example")
                with self.assertRaises(urllib.error.HTTPError) as raised_host:
                    urllib.request.urlopen(rebound, timeout=5)
                self.assertEqual(raised_host.exception.code, 403)
                self.assertNotIn(b"alpha", raised_host.exception.read())
                with urllib.request.urlopen(base_url + "/api/report", timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertEqual(payload["summary"]["total_catalogue_count"], 1)
                with urllib.request.urlopen(base_url + "/", timeout=5) as response:
                    html = response.read().decode("utf-8")
                self.assertIn("Workspace Skill Catalogue", html)
                for method in ("POST", "PUT", "PATCH", "DELETE"):
                    with self.subTest(method=method):
                        connection = http.client.HTTPConnection(
                            "127.0.0.1", server.server_address[1], timeout=5
                        )
                        try:
                            connection.request(method, "/api/report", body=b"{}")
                            rejected = connection.getresponse()
                            self.assertEqual(rejected.status, 405)
                            self.assertEqual(rejected.read(), b"method not allowed\n")
                        finally:
                            connection.close()
                        with urllib.request.urlopen(base_url + "/api/report", timeout=5) as response:
                            after_rejection = json.loads(response.read().decode("utf-8"))
                        self.assertEqual(after_rejection, payload)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_dashboard_marks_expired_compliance_audit_stale(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            audit_dir = repo / "docs" / "audits"
            audit_dir.mkdir(parents=True)
            source = repo / "source.md"
            source.write_text("baseline\n", encoding="utf-8")
            matrix = {
                "schema_version": 1,
                "audited_at": "2000-01-01",
                "sources": {"S": {"path": "source.md", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}},
                "requirements": [{"status": "compliant"}],
                "reaudit": {"max_age_days": 90, "triggers": ["source change"]},
            }
            (audit_dir / "agent-skills-compliance-matrix.json").write_text(
                json.dumps(matrix), encoding="utf-8"
            )
            from skill_catalog_dashboard.compliance import load_compliance_summary

            compliance = load_compliance_summary(repo)
        self.assertEqual(compliance["status"], "stale_audit")
        self.assertGreater(compliance["audit_age_days"], 90)

    def test_report_surfaces_repository_compliance_summary(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            catalog = base / "catalog"
            catalog.mkdir()
            self._skill(catalog, "alpha")
            payload = report_to_dict(
                build_report(
                    [catalog],
                    repo_root=ROOT,
                    telemetry_db=base / "missing.sqlite3",
                )
            )
        compliance = payload["summary"]["compliance"]
        self.assertEqual(compliance["status"], "observed")
        self.assertGreater(compliance["counts"]["compliant"], 0)
        self.assertGreaterEqual(compliance["audit_age_days"], 0)
        self.assertEqual(compliance["source_drift_count"], 0)
        html = render_html(
            build_report(
                [catalog],
                repo_root=ROOT,
                telemetry_db=base / "missing.sqlite3",
            )
        )
        self.assertIn("Compliance", html)
        self.assertIn("Audit age", html)


if __name__ == "__main__":
    unittest.main()
