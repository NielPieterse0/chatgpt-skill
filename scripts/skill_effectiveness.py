#!/usr/bin/env python3
"""Validate skill evaluation evidence and emit a multi-dimensional scorecard."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
SKILL_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
TELEMETRY_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
METRICS = ("duration_ms", "input_tokens", "output_tokens", "tool_calls", "retries")
TELEMETRY_COUNT_FIELDS = (
    "discovered_count", "loaded_count", "resource_read_count", "evaluated_count",
    "mutation_count", "applied_count", "completed_count", "failed_count", "error_count",
    "duration_samples", "token_samples", "tool_call_samples", "retry_samples",
    "verification_samples", "verification_passes",
)
TELEMETRY_SUM_FIELDS = (
    "total_duration_ms", "total_tokens", "total_tool_calls", "total_retries"
)
TELEMETRY_GROUP_KEYS = {
    "skill_id", "content_sha256", "project_id", *TELEMETRY_COUNT_FIELDS, *TELEMETRY_SUM_FIELDS,
}
TOP_LEVEL_KEYS = {
    "schema_version", "skill_id", "adopted_content_sha256", "runtime_content_sha256",
    "adapter", "target_verified_at", "eval_definition_revision", "baseline",
    "isolation_method", "trigger", "output_observability", "output_runs", "verification",
    "abuse_observability", "abuse", "compatibility", "human_review", "rollback",
    "production_regressions",
}


class EvaluationError(ValueError):
    """Raised when evaluation evidence is incomplete or inconsistent."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"invalid JSON at {path}: {exc}") from exc


def _require_exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        unknown = sorted(actual - keys)
        raise EvaluationError(f"{label} keys mismatch; missing={missing}, unknown={unknown}")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvaluationError(f"{label} must be a non-empty string")
    return value.strip()


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise EvaluationError(f"{label} must be boolean")
    return value


def _validate_skill_id(skill_id: Any) -> str:
    if not isinstance(skill_id, str) or SKILL_ID_RE.fullmatch(skill_id) is None or "--" in skill_id:
        raise EvaluationError("skill_id must be a canonical lowercase skill name")
    return skill_id


def _direct_child(root: Path, name: str, label: str) -> Path:
    root = root.resolve()
    candidate = root / name
    try:
        resolved = candidate.resolve()
    except OSError as exc:
        raise EvaluationError(f"cannot resolve {label}: {exc}") from exc
    if resolved.parent != root:
        raise EvaluationError(f"{label} must remain a direct child of {root}")
    return resolved


def _resolve_commit_revision(repo: Path, revision: str) -> str:
    if REVISION_RE.fullmatch(revision) is None:
        raise EvaluationError("eval_definition_revision must be a full immutable Git object ID")
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", f"{revision}^{{commit}}"],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError as exc:
        raise EvaluationError(f"cannot execute git for evaluation provenance: {exc}") from exc
    resolved = result.stdout.strip()
    if result.returncode != 0 or REVISION_RE.fullmatch(resolved) is None:
        detail = result.stderr.strip()
        raise EvaluationError(f"eval_definition_revision is not a resolvable commit: {detail}")
    if resolved != revision:
        raise EvaluationError("eval_definition_revision must use the full canonical commit ID")
    return resolved


def _definition_blob(repo: Path, relative_path: Path, revision: str | None) -> bytes:
    if revision is None:
        try:
            return (repo / relative_path).read_bytes()
        except OSError as exc:
            raise EvaluationError(f"cannot read {relative_path}: {exc}") from exc
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"{revision}:{relative_path.as_posix()}"],
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise EvaluationError(f"cannot execute git for evaluation definitions: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise EvaluationError(
            f"cannot resolve evaluation definition {relative_path} at {revision}: {detail}"
        )
    return result.stdout


def _definition_json(repo: Path, relative_path: Path, revision: str | None) -> tuple[Any, str]:
    raw = _definition_blob(repo, relative_path, revision)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"invalid JSON at {relative_path}: {exc}") from exc
    return value, hashlib.sha256(raw).hexdigest()


def _validate_definition_documents(
    skill_id: str, trigger: Any, output_doc: Any, abuse_doc: Any
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(trigger, list):
        raise EvaluationError("trigger-cases.json must contain a list")
    trigger_ids: set[str] = set()
    categories = defaultdict(int)
    for raw_case in trigger:
        case = _require_exact_keys(
            raw_case, {"id", "query", "expected", "category", "rationale"}, "trigger definition"
        )
        case_id = _require_text(case["id"], "trigger definition.id")
        if case_id in trigger_ids:
            raise EvaluationError(f"duplicate trigger definition id: {case_id}")
        trigger_ids.add(case_id)
        _require_text(case["query"], "trigger definition.query")
        _require_text(case["rationale"], "trigger definition.rationale")
        if case["expected"] not in {"trigger", "do_not_trigger"}:
            raise EvaluationError("trigger definition.expected is invalid")
        if case["category"] not in {"positive", "near_miss", "conflict", "prompt_injection"}:
            raise EvaluationError("trigger definition.category is invalid")
        categories[case["category"]] += 1

    output_value = _require_exact_keys(
        output_doc, {"skill_name", "baseline", "evals"}, "output-evals.json"
    )
    if output_value["skill_name"] != skill_id:
        raise EvaluationError("output-evals.json skill identity mismatch")
    _require_text(output_value["baseline"], "output-evals.json baseline")
    output = output_value["evals"]
    if not isinstance(output, list):
        raise EvaluationError("output-evals.json evals must be a list")
    output_ids: set[str] = set()
    for raw_eval in output:
        eval_case = _require_exact_keys(
            raw_eval,
            {"id", "prompt", "expected_outcome", "assertions", "human_review"},
            "output eval definition",
        )
        eval_id = _require_text(eval_case["id"], "output eval definition.id")
        if eval_id in output_ids:
            raise EvaluationError(f"duplicate output eval definition id: {eval_id}")
        output_ids.add(eval_id)
        _require_text(eval_case["prompt"], "output eval definition.prompt")
        _require_text(eval_case["expected_outcome"], "output eval definition.expected_outcome")
        assertions = eval_case["assertions"]
        if not isinstance(assertions, list) or not assertions:
            raise EvaluationError("output eval assertions must be a non-empty list")
        assertion_ids: set[str] = set()
        for raw_assertion in assertions:
            assertion = _require_exact_keys(
                raw_assertion, {"id", "text", "critical", "method"}, "output assertion definition"
            )
            assertion_id = _require_text(assertion["id"], "output assertion definition.id")
            if assertion_id in assertion_ids:
                raise EvaluationError(f"duplicate output assertion definition id: {eval_id}/{assertion_id}")
            assertion_ids.add(assertion_id)
            _require_text(assertion["text"], "output assertion definition.text")
            _require_bool(assertion["critical"], "output assertion definition.critical")
            _require_text(assertion["method"], "output assertion definition.method")
        human_review = eval_case["human_review"]
        if not isinstance(human_review, list) or not all(
            isinstance(item, str) and item.strip() for item in human_review
        ):
            raise EvaluationError("output eval human_review must be a string list")

    abuse_value = _require_exact_keys(abuse_doc, {"skill_name", "cases"}, "abuse-cases.json")
    if abuse_value["skill_name"] != skill_id:
        raise EvaluationError("abuse-cases.json skill identity mismatch")
    abuse = abuse_value["cases"]
    if not isinstance(abuse, list):
        raise EvaluationError("abuse-cases.json cases must be a list")
    abuse_ids: set[str] = set()
    for raw_case in abuse:
        case = _require_exact_keys(raw_case, {"id", "scenario", "expected"}, "abuse definition")
        case_id = _require_text(case["id"], "abuse definition.id")
        if case_id in abuse_ids:
            raise EvaluationError(f"duplicate abuse definition id: {case_id}")
        abuse_ids.add(case_id)
        _require_text(case["scenario"], "abuse definition.scenario")
        _require_text(case["expected"], "abuse definition.expected")

    minimums = {"positive": 6, "near_miss": 6, "conflict": 2, "prompt_injection": 2}
    for category, minimum in minimums.items():
        if categories[category] < minimum:
            raise EvaluationError(f"trigger definitions require at least {minimum} {category} cases")
    return trigger, output, abuse


def load_definitions(repo: Path, skill_id: str, revision: str | None = None) -> dict[str, Any]:
    skill_id = _validate_skill_id(skill_id)
    if revision is None:
        _direct_child(repo / "tests" / "skills", skill_id, "evaluation definition directory")
    base = Path("tests") / "skills" / skill_id
    trigger_path = base / "trigger-cases.json"
    output_path = base / "output-evals.json"
    abuse_path = base / "abuse-cases.json"
    trigger, trigger_hash = _definition_json(repo, trigger_path, revision)
    output_doc, output_hash = _definition_json(repo, output_path, revision)
    abuse_doc, abuse_hash = _definition_json(repo, abuse_path, revision)
    trigger, output, abuse = _validate_definition_documents(
        skill_id, trigger, output_doc, abuse_doc
    )
    return {
        "trigger": trigger,
        "output": output,
        "abuse": abuse,
        "provenance": {
            "revision": revision,
            "sha256": {
                trigger_path.as_posix(): trigger_hash,
                output_path.as_posix(): output_hash,
                abuse_path.as_posix(): abuse_hash,
            },
        },
    }


def _load_identity(repo: Path, skill_id: str) -> tuple[str, str]:
    skill_id = _validate_skill_id(skill_id)
    skill_dir = _direct_child(repo / "skills", skill_id, "skill directory")
    manifest = _load_json(skill_dir / "adoption-manifest.json")
    try:
        adopted = manifest["source"]["adopted_content_sha256"]
    except (KeyError, TypeError) as exc:
        raise EvaluationError("adoption manifest lacks adopted content hash") from exc
    if not isinstance(adopted, str) or not SHA256_RE.fullmatch(adopted):
        raise EvaluationError("adoption manifest content hash is invalid")
    try:
        runtime = hashlib.sha256((skill_dir / "SKILL.md").read_bytes()).hexdigest()
    except OSError as exc:
        raise EvaluationError(f"cannot read {skill_id}/SKILL.md: {exc}") from exc
    return adopted, runtime


def _validate_identity(repo: Path, skill_id: str, record: dict[str, Any]) -> None:
    if record["schema_version"] != 1:
        raise EvaluationError("evaluation record schema_version must be 1")
    if record["skill_id"] != skill_id:
        raise EvaluationError("evaluation record skill_id mismatch")
    adopted, runtime = _load_identity(repo, skill_id)
    if record["adopted_content_sha256"] != adopted:
        raise EvaluationError("evaluation record adopted content hash mismatch")
    if record["runtime_content_sha256"] != runtime:
        raise EvaluationError("evaluation record runtime content hash mismatch")
    if not REVISION_RE.fullmatch(str(record["eval_definition_revision"])):
        raise EvaluationError("eval_definition_revision must be an immutable hex revision")
    _require_text(record["adapter"], "adapter")
    _require_text(record["target_verified_at"], "target_verified_at")
    _require_text(record["isolation_method"], "isolation_method")

def _validate_baseline(record: dict[str, Any]) -> None:
    baseline = _require_exact_keys(record["baseline"], {"kind", "identity"}, "baseline")
    if baseline["kind"] not in {"no-skill", "previous-version"}:
        raise EvaluationError("baseline.kind must be no-skill or previous-version")
    _require_text(baseline["identity"], "baseline.identity")


def _ids(items: list[dict[str, Any]], label: str) -> set[str]:
    result: set[str] = set()
    for item in items:
        item_id = _require_text(item.get("id"), f"{label}.id")
        if item_id in result:
            raise EvaluationError(f"duplicate {label} id: {item_id}")
        result.add(item_id)
    return result


def _validate_trigger(definitions: list[dict[str, Any]], trigger: Any) -> None:
    value = _require_exact_keys(trigger, {"observability", "reason", "cases"}, "trigger")
    if value["observability"] not in {"observed", "not_observable"}:
        raise EvaluationError("trigger.observability is invalid")
    if not isinstance(value["cases"], list):
        raise EvaluationError("trigger.cases must be a list")
    if value["observability"] == "not_observable":
        _require_text(value["reason"], "trigger.reason")
        if value["cases"]:
            raise EvaluationError("unobservable trigger evidence must not claim case results")
        return
    if value["reason"] is not None:
        raise EvaluationError("observed trigger evidence must use null reason")
    expected_ids = _ids(definitions, "trigger definition")
    actual_ids: set[str] = set()
    for case in value["cases"]:
        item = _require_exact_keys(case, {"id", "triggers", "runs"}, "trigger case result")
        case_id = _require_text(item["id"], "trigger case result.id")
        if case_id in actual_ids:
            raise EvaluationError(f"duplicate trigger result: {case_id}")
        actual_ids.add(case_id)
        for key in ("triggers", "runs"):
            metric = item[key]
            if isinstance(metric, bool) or not isinstance(metric, int) or metric < 0:
                raise EvaluationError(f"trigger {case_id}.{key} must be non-negative integer")
        if item["runs"] != 3 or item["triggers"] > item["runs"]:
            raise EvaluationError(f"trigger {case_id} must contain exactly three bounded runs")
    if actual_ids != expected_ids:
        raise EvaluationError("trigger result IDs do not match tracked definitions")


def _validate_metrics(run: dict[str, Any]) -> None:
    metrics = _require_exact_keys(run["metrics"], set(METRICS), "output run metrics")
    missing = run["not_observable"]
    if not isinstance(missing, dict) or not set(missing) <= set(METRICS):
        raise EvaluationError("output run not_observable keys are invalid")
    for metric, raw in metrics.items():
        if raw is None:
            _require_text(missing.get(metric), f"not_observable.{metric}")
            continue
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
            raise EvaluationError(f"metric {metric} must be non-negative integer or null")
        if metric in missing:
            raise EvaluationError(f"observed metric {metric} must not have not_observable reason")


def _validate_observability(value: Any, label: str) -> dict[str, Any]:
    result = _require_exact_keys(value, {"status", "reason"}, label)
    if result["status"] not in {"observed", "not_observable"}:
        raise EvaluationError(f"{label}.status is invalid")
    if result["status"] == "observed":
        if result["reason"] is not None:
            raise EvaluationError(f"observed {label} must use null reason")
    else:
        _require_text(result["reason"], f"{label}.reason")
    return result


def _validate_output(
    definitions: list[dict[str, Any]], observability: Any, runs: Any
) -> None:
    observed = _validate_observability(observability, "output_observability")
    if not isinstance(runs, list):
        raise EvaluationError("output_runs must be a list")
    if observed["status"] == "not_observable":
        if runs:
            raise EvaluationError("unobservable output evidence must not claim run results")
        return
    if not runs:
        raise EvaluationError("observed output evidence requires candidate and baseline runs")
    definitions_by_id = {item["id"]: item for item in definitions}
    observed_pairs: set[tuple[str, str]] = set()
    seen_runs: set[tuple[str, str, int]] = set()
    run_numbers: dict[tuple[str, str], set[int]] = defaultdict(set)
    for raw in runs:
        run = _require_exact_keys(
            raw,
            {"eval_id", "configuration", "run", "assertions", "metrics", "not_observable"},
            "output run",
        )
        eval_id = _require_text(run["eval_id"], "output run.eval_id")
        if eval_id not in definitions_by_id:
            raise EvaluationError(f"unknown output eval id: {eval_id}")
        config = run["configuration"]
        if config not in {"with_skill", "baseline"}:
            raise EvaluationError("output configuration must be with_skill or baseline")
        run_no = run["run"]
        if isinstance(run_no, bool) or not isinstance(run_no, int) or run_no < 1:
            raise EvaluationError("output run number must be a positive integer")
        run_key = (eval_id, config, run_no)
        if run_key in seen_runs:
            raise EvaluationError(f"duplicate output run: {run_key}")
        seen_runs.add(run_key)
        observed_pairs.add((eval_id, config))
        run_numbers[(eval_id, config)].add(run_no)
        assertions = run["assertions"]
        if not isinstance(assertions, list):
            raise EvaluationError("output assertions must be a list")
        expected_assertions = {item["id"] for item in definitions_by_id[eval_id]["assertions"]}
        actual_assertions: set[str] = set()
        for raw_assertion in assertions:
            assertion = _require_exact_keys(
                raw_assertion, {"id", "passed", "evidence"}, "output assertion result"
            )
            assertion_id = _require_text(assertion["id"], "output assertion result.id")
            if assertion_id in actual_assertions:
                raise EvaluationError(f"duplicate assertion result: {eval_id}/{assertion_id}")
            actual_assertions.add(assertion_id)
            _require_bool(assertion["passed"], "output assertion result.passed")
            _require_text(assertion["evidence"], "output assertion result.evidence")
        if actual_assertions != expected_assertions:
            raise EvaluationError(f"assertion result IDs do not match {eval_id} definition")
        _validate_metrics(run)
    required_pairs = {(item["id"], config) for item in definitions for config in ("with_skill", "baseline")}
    if observed_pairs != required_pairs:
        raise EvaluationError("output results must cover every eval for candidate and baseline")
    for eval_case in definitions:
        eval_id = eval_case["id"]
        candidate_runs = run_numbers[(eval_id, "with_skill")]
        baseline_runs = run_numbers[(eval_id, "baseline")]
        if candidate_runs != baseline_runs:
            raise EvaluationError(
                f"output runs must use identical candidate/baseline run numbers for {eval_id}"
            )


def _validate_checks(record: dict[str, Any], definitions: dict[str, Any]) -> None:
    verification = record["verification"]
    if not isinstance(verification, list) or not verification:
        raise EvaluationError("verification must contain at least one check")
    for check in verification:
        value = _require_exact_keys(check, {"id", "passed", "evidence"}, "verification")
        _require_text(value["id"], "verification.id")
        _require_bool(value["passed"], "verification.passed")
        _require_text(value["evidence"], "verification.evidence")

    abuse_observability = _validate_observability(
        record["abuse_observability"], "abuse_observability"
    )
    abuse = record["abuse"]
    if not isinstance(abuse, list):
        raise EvaluationError("abuse must be a list")
    if abuse_observability["status"] == "not_observable":
        if abuse:
            raise EvaluationError("unobservable abuse evidence must not claim case results")
    else:
        expected_ids = _ids(definitions["abuse"], "abuse definition")
        actual_ids: set[str] = set()
        for case in abuse:
            value = _require_exact_keys(
                case, {"id", "passed", "evidence"}, "abuse result"
            )
            case_id = _require_text(value["id"], "abuse result.id")
            if case_id in actual_ids:
                raise EvaluationError(f"duplicate abuse result: {case_id}")
            actual_ids.add(case_id)
            _require_bool(value["passed"], "abuse result.passed")
            _require_text(value["evidence"], "abuse result.evidence")
        if actual_ids != expected_ids:
            raise EvaluationError("abuse result IDs do not match tracked definitions")

    compatibility = _require_exact_keys(record["compatibility"], {"status", "evidence"}, "compatibility")
    if compatibility["status"] not in {"pass", "fail", "not_observable"}:
        raise EvaluationError("compatibility.status is invalid")
    _require_text(compatibility["evidence"], "compatibility.evidence")
    human = _require_exact_keys(
        record["human_review"], {"status", "reviewer", "date", "feedback"}, "human_review"
    )
    if human["status"] not in {"pass", "fail", "pending"}:
        raise EvaluationError("human_review.status is invalid")
    if human["status"] == "pending":
        if human["reviewer"] is not None or human["date"] is not None:
            raise EvaluationError("pending human review requires null reviewer and date")
    else:
        _require_text(human["reviewer"], "human_review.reviewer")
        _require_text(human["date"], "human_review.date")
    if not isinstance(human["feedback"], list) or not all(
        isinstance(item, str) for item in human["feedback"]
    ):
        raise EvaluationError("human_review.feedback must be a string list")

    rollback = _require_exact_keys(record["rollback"], {"verified", "evidence"}, "rollback")
    _require_bool(rollback["verified"], "rollback.verified")
    _require_text(rollback["evidence"], "rollback.evidence")

    regressions = record["production_regressions"]
    if not isinstance(regressions, list):
        raise EvaluationError("production_regressions must be a list")
    for regression in regressions:
        value = _require_exact_keys(
            regression, {"id", "summary", "fixture_candidate"}, "production regression"
        )
        _require_text(value["id"], "production regression.id")
        _require_text(value["summary"], "production regression.summary")
        _require_text(value["fixture_candidate"], "production regression.fixture_candidate")


def _validate_record(repo: Path, skill_id: str, record: Any, definitions: dict[str, Any]) -> dict[str, Any]:
    value = _require_exact_keys(record, TOP_LEVEL_KEYS, "evaluation record")
    _validate_identity(repo, skill_id, value)
    _validate_baseline(value)
    _validate_trigger(definitions["trigger"], value["trigger"])
    _validate_output(
        definitions["output"], value["output_observability"], value["output_runs"]
    )
    _validate_checks(value, definitions)
    return value


def _trigger_dimension(definitions: list[dict[str, Any]], record: dict[str, Any]) -> dict[str, Any]:
    trigger = record["trigger"]
    if trigger["observability"] == "not_observable":
        return {
            "status": "not_observable",
            "reason": trigger["reason"],
            "passed": None,
            "total": len(definitions),
            "cases": [],
        }
    results = {item["id"]: item for item in trigger["cases"]}
    cases = []
    for definition in definitions:
        result = results[definition["id"]]
        category = definition["category"]
        expected = definition["expected"]
        if category == "positive":
            passed = result["triggers"] >= 2
        elif category == "near_miss":
            passed = result["triggers"] <= 1
        elif expected == "trigger":
            passed = result["triggers"] == result["runs"]
        else:
            passed = result["triggers"] == 0
        cases.append(
            {
                "id": definition["id"],
                "category": category,
                "expected": expected,
                "triggers": result["triggers"],
                "runs": result["runs"],
                "trigger_rate": result["triggers"] / result["runs"],
                "passed": passed,
            }
        )
    passed_count = sum(1 for item in cases if item["passed"])
    return {
        "status": "pass" if passed_count == len(cases) else "fail",
        "passed": passed_count,
        "total": len(cases),
        "cases": cases,
    }


def _assertion_rates(
    definitions: list[dict[str, Any]], runs: list[dict[str, Any]]
) -> dict[tuple[str, str], dict[str, float]]:
    values: dict[tuple[str, str], dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for run in runs:
        key = (run["eval_id"], run["configuration"])
        for assertion in run["assertions"]:
            values[key][assertion["id"]].append(assertion["passed"])
    rates: dict[tuple[str, str], dict[str, float]] = {}
    for key, assertions in values.items():
        rates[key] = {
            assertion_id: sum(1 for passed in outcomes if passed) / len(outcomes)
            for assertion_id, outcomes in assertions.items()
        }
    return rates


def _output_dimension(
    definitions: list[dict[str, Any]], observability: dict[str, Any], runs: list[dict[str, Any]]
) -> dict[str, Any]:
    if observability["status"] == "not_observable":
        return {
            "status": "not_observable",
            "reason": observability["reason"],
            "with_skill_pass_rate": None,
            "baseline_pass_rate": None,
            "critical_failures": [],
            "baseline_critical_regressions": [],
            "material_improvements": [],
            "run_counts": {},
        }
    rates = _assertion_rates(definitions, runs)
    critical_failures = []
    baseline_regressions = []
    improvements = []
    candidate_values: list[float] = []
    baseline_values: list[float] = []
    for eval_case in definitions:
        eval_id = eval_case["id"]
        candidate = rates[(eval_id, "with_skill")]
        baseline = rates[(eval_id, "baseline")]
        for assertion in eval_case["assertions"]:
            assertion_id = assertion["id"]
            candidate_rate = candidate[assertion_id]
            baseline_rate = baseline[assertion_id]
            candidate_values.append(candidate_rate)
            baseline_values.append(baseline_rate)
            if assertion.get("critical") is True and candidate_rate < 1.0:
                critical_failures.append(
                    {"eval_id": eval_id, "assertion_id": assertion_id, "pass_rate": candidate_rate}
                )
            if assertion.get("critical") is True and baseline_rate == 1.0 and candidate_rate < 1.0:
                baseline_regressions.append(
                    {"eval_id": eval_id, "assertion_id": assertion_id,
                     "baseline_pass_rate": baseline_rate, "candidate_pass_rate": candidate_rate}
                )
            if candidate_rate >= (2 / 3) and baseline_rate < (2 / 3):
                improvements.append(
                    {"eval_id": eval_id, "assertion_id": assertion_id,
                     "baseline_pass_rate": baseline_rate, "candidate_pass_rate": candidate_rate}
                )
    status = "pass" if not critical_failures and not baseline_regressions and improvements else "fail"
    run_counts = {
        eval_case["id"]: sum(
            1
            for run in runs
            if run["eval_id"] == eval_case["id"] and run["configuration"] == "with_skill"
        )
        for eval_case in definitions
    }
    return {
        "status": status,
        "with_skill_pass_rate": sum(candidate_values) / len(candidate_values),
        "baseline_pass_rate": sum(baseline_values) / len(baseline_values),
        "critical_failures": critical_failures,
        "baseline_critical_regressions": baseline_regressions,
        "material_improvements": improvements,
        "run_counts": run_counts,
    }


def _stats(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"status": "not_observable", "samples": 0, "mean": None}
    return {"status": "observed", "samples": len(values), "mean": sum(values) / len(values)}


def _efficiency_dimension(runs: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    overall_statuses: set[str] = set()
    for metric in METRICS:
        by_config: dict[str, Any] = {}
        for config in ("with_skill", "baseline"):
            relevant = [run for run in runs if run["configuration"] == config]
            observed = [run["metrics"][metric] for run in relevant if run["metrics"][metric] is not None]
            result = _stats(observed)
            missing = len(relevant) - len(observed)
            if observed and missing:
                result["status"] = "partial"
                result["not_observable_samples"] = missing
            elif not observed:
                reasons = sorted(
                    {run["not_observable"].get(metric) for run in relevant if run["metrics"][metric] is None}
                    - {None}
                )
                result["reasons"] = reasons
            by_config[config] = result
            overall_statuses.add(result["status"])
        candidate_mean = by_config["with_skill"]["mean"]
        baseline_mean = by_config["baseline"]["mean"]
        delta = None if candidate_mean is None or baseline_mean is None else candidate_mean - baseline_mean
        metrics[metric] = {**by_config, "delta": delta}
    if overall_statuses == {"observed"}:
        status = "observed"
    elif overall_statuses == {"not_observable"}:
        status = "not_observable"
    else:
        status = "partial"
    return {"status": status, "metrics": metrics}

def _boolean_gate(items: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [item["id"] for item in items if not item["passed"]]
    return {
        "status": "pass" if not failed else "fail",
        "passed": len(items) - len(failed),
        "total": len(items),
        "failed_ids": failed,
    }


def _nonnegative_int(value: Any, label: str, *, optional: bool = False) -> int | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        suffix = " or null" if optional else ""
        raise EvaluationError(f"{label} must be a non-negative integer{suffix}")
    return value


def _normalize_telemetry_group(group: Any) -> dict[str, Any]:
    value = _require_exact_keys(group, TELEMETRY_GROUP_KEYS, "telemetry group")
    skill_id = value["skill_id"]
    project_id = value["project_id"]
    if skill_id is not None and (
        not isinstance(skill_id, str) or TELEMETRY_ID_RE.fullmatch(skill_id) is None
    ):
        raise EvaluationError("telemetry group.skill_id is invalid")
    if project_id is not None and (
        not isinstance(project_id, str) or TELEMETRY_ID_RE.fullmatch(project_id) is None
    ):
        raise EvaluationError("telemetry group.project_id is invalid")
    content_sha256 = value["content_sha256"]
    if content_sha256 is not None and (
        not isinstance(content_sha256, str) or SHA256_RE.fullmatch(content_sha256) is None
    ):
        raise EvaluationError("telemetry group.content_sha256 is invalid")
    normalized = {
        "skill_id": skill_id,
        "content_sha256": content_sha256,
        "project_id": project_id,
    }
    for field in TELEMETRY_COUNT_FIELDS:
        normalized[field] = _nonnegative_int(
            value[field], f"telemetry group.{field}", optional=field == "verification_passes"
        )
    for field in TELEMETRY_SUM_FIELDS:
        normalized[field] = _nonnegative_int(
            value[field], f"telemetry group.{field}", optional=True
        )
    return normalized


def _operational_telemetry(record: dict[str, Any], telemetry: Any | None) -> dict[str, Any]:
    if telemetry is None:
        return {
            "status": "not_provided",
            "behavioral_effectiveness_evidence": False,
            "totals": {},
            "groups": [],
        }
    report = _require_exact_keys(
        telemetry, {"schema_version", "groups", "event_count", "truncated"}, "telemetry report"
    )
    if report["schema_version"] != 1:
        raise EvaluationError("telemetry report schema_version must be 1")
    event_count = _nonnegative_int(report["event_count"], "telemetry report.event_count")
    _require_bool(report["truncated"], "telemetry report.truncated")
    if not isinstance(report["groups"], list):
        raise EvaluationError("telemetry groups must be a list")
    normalized_groups = [_normalize_telemetry_group(group) for group in report["groups"]]
    matching = [
        group for group in normalized_groups
        if group["skill_id"] == record["skill_id"]
        and group["content_sha256"] == record["runtime_content_sha256"]
    ]
    optional_fields = ("verification_passes", *TELEMETRY_SUM_FIELDS)
    mandatory_count_fields = tuple(
        field for field in TELEMETRY_COUNT_FIELDS if field != "verification_passes"
    )
    totals: dict[str, int | None] = {field: 0 for field in mandatory_count_fields}
    totals.update({field: None for field in optional_fields})
    observations = {
        field: {"observed_groups": 0, "not_observable_groups": 0}
        for field in optional_fields
    }
    for group in matching:
        for field in mandatory_count_fields:
            totals[field] = int(totals[field] or 0) + int(group[field])
        for field in optional_fields:
            raw = group[field]
            if raw is None:
                observations[field]["not_observable_groups"] += 1
                continue
            observations[field]["observed_groups"] += 1
            totals[field] = int(totals[field] or 0) + raw
    field_observability = {}
    for field, counts in observations.items():
        if counts["observed_groups"] == 0:
            status = "not_observable"
        elif counts["not_observable_groups"]:
            status = "partial"
        else:
            status = "observed"
        field_observability[field] = {"status": status, **counts}
    return {
        "status": "truncated" if report["truncated"] else "observed",
        "behavioral_effectiveness_evidence": False,
        "event_count": event_count,
        "matching_group_count": len(matching),
        "totals": totals,
        "field_observability": field_observability,
        "groups": matching,
        "interpretation": "Operational usage context only; it does not change behavioral gates.",
    }

def evaluate_record(
    repo: Path,
    skill_id: str,
    record: Any,
    *,
    telemetry: Any | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    skill_id = _validate_skill_id(skill_id)
    preliminary = _require_exact_keys(record, TOP_LEVEL_KEYS, "evaluation record")
    revision = _resolve_commit_revision(repo, str(preliminary["eval_definition_revision"]))
    definitions = load_definitions(repo, skill_id, revision=revision)
    value = _validate_record(repo, skill_id, preliminary, definitions)

    trigger = _trigger_dimension(definitions["trigger"], value)
    output = _output_dimension(
        definitions["output"], value["output_observability"], value["output_runs"]
    )
    efficiency = _efficiency_dimension(value["output_runs"])
    verification = _boolean_gate(value["verification"])
    if value["abuse_observability"]["status"] == "not_observable":
        abuse = {
            "status": "not_observable",
            "reason": value["abuse_observability"]["reason"],
            "passed": None,
            "total": len(definitions["abuse"]),
            "failed_ids": [],
        }
    else:
        abuse = _boolean_gate(value["abuse"])
    compatibility = dict(value["compatibility"])
    human = dict(value["human_review"])
    rollback = {
        "status": "pass" if value["rollback"]["verified"] else "fail",
        **value["rollback"],
    }
    operational = _operational_telemetry(value, telemetry)

    hard_failures: list[str] = []
    deferred: list[str] = []
    if trigger["status"] == "fail":
        hard_failures.append("trigger:boundary_failure")
    elif trigger["status"] == "not_observable":
        deferred.append("trigger:not_observable")
    if output["status"] == "not_observable":
        deferred.append("output:not_observable")
    else:
        if output["critical_failures"]:
            hard_failures.append("output:critical_failure")
        if output["baseline_critical_regressions"]:
            hard_failures.append("output:baseline_critical_regression")
        if not output["material_improvements"]:
            hard_failures.append("output:no_material_improvement")
    if verification["status"] == "fail":
        hard_failures.append("verification:failed")
    if abuse["status"] == "fail":
        hard_failures.append("abuse:failed")
    elif abuse["status"] == "not_observable":
        deferred.append("abuse:not_observable")
    if compatibility["status"] == "fail":
        hard_failures.append("compatibility:failed")
    elif compatibility["status"] == "not_observable":
        deferred.append("compatibility:not_observable")
    if human["status"] == "fail":
        hard_failures.append("human_review:failed")
    elif human["status"] == "pending":
        deferred.append("human_review:pending")
    if rollback["status"] == "fail":
        hard_failures.append("rollback:failed")

    blockers = hard_failures + deferred
    disposition = "revise" if hard_failures else "defer" if deferred else "admit"
    return {
        "schema_version": 1,
        "skill_id": skill_id,
        "adopted_content_sha256": value["adopted_content_sha256"],
        "runtime_content_sha256": value["runtime_content_sha256"],
        "evaluation": {
            "adapter": value["adapter"],
            "target_verified_at": value["target_verified_at"],
            "eval_definition_revision": value["eval_definition_revision"],
            "definition_provenance": definitions["provenance"],
            "baseline": value["baseline"],
            "isolation_method": value["isolation_method"],
        },
        "dimensions": {
            "trigger": trigger,
            "output_quality": output,
            "efficiency": efficiency,
            "verification": verification,
            "abuse": abuse,
            "compatibility": compatibility,
            "human_review": human,
            "rollback": rollback,
            "operational_telemetry": operational,
        },
        "fixture_candidates": value["production_regressions"],
        "recommended_disposition": disposition,
        "blocking_reasons": blockers,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate generated skill-evaluation evidence and emit a scorecard."
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--skill", required=True)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--telemetry", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        record = _load_json(args.record)
        telemetry = _load_json(args.telemetry) if args.telemetry else None
        scorecard = evaluate_record(args.repo, args.skill, record, telemetry=telemetry)
    except EvaluationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(scorecard, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
