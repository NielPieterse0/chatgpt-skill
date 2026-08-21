#!/usr/bin/env python3
"""Validate description-optimization evidence against fixed trigger splits."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import skill_effectiveness

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class OptimizationError(ValueError):
    """Raised when description-optimization evidence is incomplete or leaks cohorts."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OptimizationError(f"invalid JSON at {path}: {exc}") from exc


def _exact(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OptimizationError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        raise OptimizationError(
            f"{label} keys mismatch; missing={sorted(keys-actual)}, unknown={sorted(actual-keys)}"
        )
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OptimizationError(f"{label} must be a non-empty string")
    return value.strip()


def _validate_result_rows(rows: Any, expected_ids: set[str], label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise OptimizationError(f"{label} must be a list")
    observed: dict[str, dict[str, Any]] = {}
    for raw in rows:
        row = _exact(raw, {"id", "triggers", "runs"}, f"{label} result")
        case_id = _text(row["id"], f"{label}.id")
        if case_id in observed:
            raise OptimizationError(f"duplicate {label} result: {case_id}")
        for key in ("triggers", "runs"):
            value = row[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise OptimizationError(f"{label}.{case_id}.{key} must be a non-negative integer")
        if row["runs"] != 3 or row["triggers"] > row["runs"]:
            raise OptimizationError(f"{label}.{case_id} must contain exactly three bounded runs")
        observed[case_id] = row
    if set(observed) != expected_ids:
        raise OptimizationError(f"{label} result IDs do not match the required cohort")
    return observed


def _passed(definition: dict[str, Any], result: dict[str, Any]) -> bool:
    category = definition["category"]
    expected = definition["expected"]
    triggers = result["triggers"]
    runs = result["runs"]
    if category == "positive":
        return triggers >= 2
    if category == "near_miss":
        return triggers <= 1
    if expected == "trigger":
        return triggers == runs
    return triggers == 0


def _cohort_summary(definitions: list[dict[str, Any]], results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for definition in definitions:
        result = results[definition["id"]]
        rows.append(
            {
                "id": definition["id"],
                "passed": _passed(definition, result),
                "trigger_rate": result["triggers"] / result["runs"],
            }
        )
    passed = sum(1 for row in rows if row["passed"])
    return {"passed": passed, "total": len(rows), "pass_rate": passed / len(rows), "cases": rows}


def validate_record(repo: Path, skill_id: str, record: Any) -> dict[str, Any]:
    value = _exact(
        record,
        {
            "schema_version", "skill_id", "definition_revision", "selected_iteration_id",
            "iterations", "validation", "fresh_sanity",
        },
        "optimization record",
    )
    if value["schema_version"] != 1:
        raise OptimizationError("optimization record schema_version must be 1")
    if value["skill_id"] != skill_id:
        raise OptimizationError("optimization record skill_id mismatch")
    revision = _text(value["definition_revision"], "definition_revision")
    try:
        resolved = skill_effectiveness._resolve_commit_revision(repo.resolve(), revision)
        definitions = skill_effectiveness.load_definitions(repo.resolve(), skill_id, revision=resolved)["trigger"]
    except skill_effectiveness.EvaluationError as exc:
        raise OptimizationError(str(exc)) from exc

    train_defs = [item for item in definitions if item["split"] == "train"]
    validation_defs = [item for item in definitions if item["split"] == "validation"]
    train_ids = {item["id"] for item in train_defs}
    validation_ids = {item["id"] for item in validation_defs}

    iterations = value["iterations"]
    if not isinstance(iterations, list) or not iterations:
        raise OptimizationError("iterations must be a non-empty list")
    iteration_results: dict[str, dict[str, Any]] = {}
    iteration_descriptions: dict[str, str] = {}
    iteration_hashes: dict[str, str] = {}
    seen_description_hashes: set[str] = set()
    for raw in iterations:
        iteration = _exact(
            raw,
            {"id", "description", "description_sha256", "train_results"},
            "iteration",
        )
        iteration_id = _text(iteration["id"], "iteration.id")
        if iteration_id in iteration_results:
            raise OptimizationError(f"duplicate iteration id: {iteration_id}")
        raw_description = iteration["description"]
        description = _text(raw_description, "iteration.description")
        if raw_description != description:
            raise OptimizationError("iteration.description must not have leading or trailing whitespace")
        if len(description) > 1024:
            raise OptimizationError("iteration.description must not exceed 1024 characters")
        description_hash = iteration["description_sha256"]
        if not isinstance(description_hash, str) or SHA256_RE.fullmatch(description_hash) is None:
            raise OptimizationError("iteration.description_sha256 must be a lowercase SHA-256")
        actual_hash = hashlib.sha256(description.encode("utf-8")).hexdigest()
        if description_hash != actual_hash:
            raise OptimizationError("iteration.description_sha256 does not match description bytes")
        if description_hash in seen_description_hashes:
            raise OptimizationError("iteration descriptions must be distinct")
        seen_description_hashes.add(description_hash)
        iteration_results[iteration_id] = _validate_result_rows(
            iteration["train_results"], train_ids, f"iteration {iteration_id} train_results"
        )
        iteration_descriptions[iteration_id] = description
        iteration_hashes[iteration_id] = description_hash

    selected = _text(value["selected_iteration_id"], "selected_iteration_id")
    if selected not in iteration_results:
        raise OptimizationError("selected_iteration_id must reference a recorded iteration")

    validation = value["validation"]
    if not isinstance(validation, list):
        raise OptimizationError("validation must be a list")
    validation_results_by_iteration: dict[str, dict[str, dict[str, Any]]] = {}
    for raw in validation:
        item = _exact(raw, {"iteration_id", "results"}, "validation item")
        iteration_id = _text(item["iteration_id"], "validation.iteration_id")
        if iteration_id not in iteration_results:
            raise OptimizationError("validation iteration_id must reference a recorded iteration")
        if iteration_id in validation_results_by_iteration:
            raise OptimizationError(f"duplicate validation results for iteration: {iteration_id}")
        validation_results_by_iteration[iteration_id] = _validate_result_rows(
            item["results"], validation_ids, f"validation {iteration_id}.results"
        )
    if set(validation_results_by_iteration) != set(iteration_results):
        raise OptimizationError("validation must cover every recorded iteration exactly once")

    validation_summaries = {
        iteration_id: _cohort_summary(validation_defs, results)
        for iteration_id, results in validation_results_by_iteration.items()
    }
    best_passed = max(summary["passed"] for summary in validation_summaries.values())
    if validation_summaries[selected]["passed"] != best_passed:
        raise OptimizationError("selected iteration must have the best validation pass rate")

    fresh = value["fresh_sanity"]
    if not isinstance(fresh, list) or len(fresh) < 4:
        raise OptimizationError("fresh_sanity must contain at least four unseen cases")
    tracked_queries = {item["query"].strip().casefold() for item in definitions}
    fresh_ids: set[str] = set()
    fresh_queries: set[str] = set()
    expected_counts = {"trigger": 0, "do_not_trigger": 0}
    fresh_defs: list[dict[str, Any]] = []
    fresh_results: dict[str, dict[str, Any]] = {}
    for raw in fresh:
        case = _exact(raw, {"id", "query", "expected", "rationale", "triggers", "runs"}, "fresh_sanity case")
        case_id = _text(case["id"], "fresh_sanity.id")
        query = _text(case["query"], "fresh_sanity.query")
        _text(case["rationale"], "fresh_sanity.rationale")
        if case_id in fresh_ids:
            raise OptimizationError(f"duplicate fresh_sanity id: {case_id}")
        normalized_query = query.casefold()
        if normalized_query in tracked_queries or normalized_query in fresh_queries:
            raise OptimizationError("fresh_sanity queries must be unseen and unique")
        if case["expected"] not in expected_counts:
            raise OptimizationError("fresh_sanity.expected is invalid")
        if isinstance(case["runs"], bool) or not isinstance(case["runs"], int) or case["runs"] != 3:
            raise OptimizationError("fresh_sanity runs must equal 3")
        if isinstance(case["triggers"], bool) or not isinstance(case["triggers"], int) or not 0 <= case["triggers"] <= 3:
            raise OptimizationError("fresh_sanity triggers must be an integer from 0 to 3")
        fresh_ids.add(case_id)
        fresh_queries.add(normalized_query)
        expected_counts[case["expected"]] += 1
        category = "positive" if case["expected"] == "trigger" else "near_miss"
        fresh_defs.append({"id": case_id, "category": category, "expected": case["expected"]})
        fresh_results[case_id] = {"id": case_id, "triggers": case["triggers"], "runs": case["runs"]}
    if min(expected_counts.values()) < 2:
        raise OptimizationError("fresh_sanity must include at least two trigger and two do-not-trigger cases")

    return {
        "schema_version": 1,
        "skill_id": skill_id,
        "definition_revision": resolved,
        "selected_iteration_id": selected,
        "selected_description": iteration_descriptions[selected],
        "selected_description_sha256": iteration_hashes[selected],
        "train": _cohort_summary(train_defs, iteration_results[selected]),
        "validation": validation_summaries[selected],
        "validation_iterations": [
            {"iteration_id": iteration_id, **validation_summaries[iteration_id]}
            for iteration_id in iteration_results
        ],
        "fresh_sanity": _cohort_summary(fresh_defs, fresh_results),
        "iteration_count": len(iteration_results),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate trigger description-optimization evidence.")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--skill", required=True)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = validate_record(args.repo, args.skill, _load_json(args.record))
    except OptimizationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
