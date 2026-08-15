from __future__ import annotations

import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from .fs import opened_path
from .models import CatalogSkill, RepoEvidence

_ITERATION = re.compile(r"^iteration-(\d+)$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVISION = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_DISPOSITIONS = {"admit", "revise", "defer"}
_SCORECARD_KEYS = {
    "schema_version",
    "skill_id",
    "adopted_content_sha256",
    "runtime_content_sha256",
    "evaluation",
    "dimensions",
    "fixture_candidates",
    "recommended_disposition",
    "blocking_reasons",
}
_EVALUATION_KEYS = {
    "adapter",
    "target_verified_at",
    "eval_definition_revision",
    "definition_provenance",
    "baseline",
    "isolation_method",
}
_DIMENSION_KEYS = {
    "trigger",
    "output_quality",
    "efficiency",
    "verification",
    "abuse",
    "compatibility",
    "human_review",
    "rollback",
    "operational_telemetry",
}
_EFFICIENCY_METRICS = {"duration_ms", "input_tokens", "output_tokens", "tool_calls", "retries"}


def _candidate_order_key(iteration: int, rank: int, path: Path) -> tuple[int, int, str, str]:
    rendered = str(path)
    return iteration, rank, rendered.casefold(), rendered


def _directory_identity(stat_result: os.stat_result) -> tuple[int, int]:
    return stat_result.st_dev, stat_result.st_ino


def _file_identity(stat_result: os.stat_result) -> tuple[int, int, int, int]:
    return (
        stat_result.st_dev,
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
    )


def _load_object(
    path: Path, *, boundary: Path
) -> tuple[dict[str, object] | None, str | None]:
    try:
        relative = path.relative_to(boundary)
    except ValueError:
        return None, "evidence path is outside repository boundary"
    directory_snapshots: list[tuple[Path, tuple[int, int]]] = []
    current = boundary
    try:
        for part in relative.parts[:-1]:
            current = current / part
            if current.is_symlink():
                return None, f"linked evidence directory rejected: {current}"
            directory_snapshots.append(
                (current, _directory_identity(current.stat(follow_symlinks=False)))
            )
        if path.is_symlink():
            return None, f"linked evidence file rejected: {path}"
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(boundary):
            return None, "resolved evidence path is outside repository boundary"
        expected_file_identity = _file_identity(path.stat(follow_symlinks=False))
        with path.open("rb") as handle:
            try:
                actual_path = opened_path(handle)
            except OSError as exc:
                return None, f"cannot verify opened evidence path: {exc}"
            if not actual_path.is_relative_to(boundary):
                return None, f"opened evidence path escaped repository boundary: {actual_path}"
            opened_stat = os.fstat(handle.fileno())
            if _file_identity(opened_stat) != expected_file_identity:
                return None, "evidence file changed during validation"
            for directory, expected_identity in directory_snapshots:
                if _directory_identity(
                    directory.stat(follow_symlinks=False)
                ) != expected_identity:
                    return None, f"evidence directory changed during validation: {directory}"
            raw = handle.read()
            if _file_identity(os.fstat(handle.fileno())) != expected_file_identity:
                return None, "evidence file changed while being read"
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(value, dict):
        return None, "JSON root is not an object"
    return value, None


def _adoption(repo_root: Path, entry: CatalogSkill) -> tuple[str, str | None, str | None, list[str]]:
    path = repo_root / "skills" / entry.name / "adoption-manifest.json"
    if not path.is_file():
        return "not_recorded", None, None, []
    value, error = _load_object(path, boundary=repo_root)
    if value is None:
        return "invalid", None, str(path), [f"adoption manifest invalid: {error}"]
    if value.get("schema_version") != 2:
        return "invalid", None, str(path), ["adoption manifest schema_version must be 2"]
    if value.get("skill") != entry.name:
        return "invalid", None, str(path), ["adoption manifest skill identity mismatch"]
    approval = value.get("approval")
    source = value.get("source")
    status = approval.get("status") if isinstance(approval, dict) else None
    digest = source.get("adopted_content_sha256") if isinstance(source, dict) else None
    if status != "approved":
        return "invalid", None, str(path), ["adoption manifest approval status must be approved"]
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        return "invalid", None, str(path), ["adoption manifest adopted content hash must be lowercase SHA-256 hex"]
    return "approved", digest, str(path), []


def _valid_verified_at(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    text = value.strip()
    try:
        if len(text) == 10:
            date.fromisoformat(text)
            return True
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_gate(value: object, *, allow_not_observable: bool = False) -> bool:
    if not isinstance(value, dict):
        return False
    required = {"status", "passed", "total", "failed_ids"}
    optional = {"reason"} if allow_not_observable else set()
    allowed_keysets = [required, required | optional]
    if set(value) not in allowed_keysets:
        return False
    statuses = {"pass", "fail"} | ({"not_observable"} if allow_not_observable else set())
    if value.get("status") not in statuses:
        return False
    if not _nonnegative_int(value.get("total")) or not isinstance(value.get("failed_ids"), list):
        return False
    if value.get("status") == "not_observable":
        return value.get("passed") is None and _text(value.get("reason"))
    return _nonnegative_int(value.get("passed")) and value.get("reason") is None


def _valid_scorecard_dimensions(dimensions: object) -> bool:
    if not isinstance(dimensions, dict) or set(dimensions) != _DIMENSION_KEYS:
        return False
    trigger = dimensions.get("trigger")
    if not isinstance(trigger, dict) or trigger.get("status") not in {"pass", "fail", "not_observable"}:
        return False
    if not _nonnegative_int(trigger.get("total")) or not isinstance(trigger.get("cases"), list):
        return False
    if trigger.get("status") == "not_observable":
        if trigger.get("passed") is not None or not _text(trigger.get("reason")):
            return False
    elif not _nonnegative_int(trigger.get("passed")):
        return False

    output = dimensions.get("output_quality")
    if not isinstance(output, dict) or output.get("status") not in {"pass", "fail", "not_observable"}:
        return False
    for key in ("critical_failures", "baseline_critical_regressions", "material_improvements"):
        if not isinstance(output.get(key), list):
            return False
    if not isinstance(output.get("run_counts"), dict):
        return False
    if output.get("status") == "not_observable" and not _text(output.get("reason")):
        return False
    if output.get("status") != "not_observable":
        for key in ("with_skill_pass_rate", "baseline_pass_rate"):
            number = output.get(key)
            if not isinstance(number, (int, float)) or isinstance(number, bool) or not 0 <= number <= 1:
                return False

    efficiency = dimensions.get("efficiency")
    if not isinstance(efficiency, dict) or set(efficiency) != {"status", "metrics"}:
        return False
    if efficiency.get("status") not in {"observed", "partial", "not_observable"}:
        return False
    metrics = efficiency.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != _EFFICIENCY_METRICS:
        return False
    for metric in metrics.values():
        if not isinstance(metric, dict) or set(metric) != {"with_skill", "baseline", "delta"}:
            return False
        for config in ("with_skill", "baseline"):
            stats = metric.get(config)
            if not isinstance(stats, dict) or stats.get("status") not in {"observed", "partial", "not_observable"}:
                return False
            if not _nonnegative_int(stats.get("samples")):
                return False
            mean = stats.get("mean")
            if mean is not None and (not isinstance(mean, (int, float)) or isinstance(mean, bool) or mean < 0):
                return False

    if not _valid_gate(dimensions.get("verification")):
        return False
    if not _valid_gate(dimensions.get("abuse"), allow_not_observable=True):
        return False

    compatibility = dimensions.get("compatibility")
    if not isinstance(compatibility, dict) or set(compatibility) != {"status", "evidence"}:
        return False
    if compatibility.get("status") not in {"pass", "fail", "not_observable"} or not _text(compatibility.get("evidence")):
        return False

    human = dimensions.get("human_review")
    if not isinstance(human, dict) or set(human) != {"status", "reviewer", "date", "feedback"}:
        return False
    if human.get("status") not in {"pass", "fail", "pending"} or not isinstance(human.get("feedback"), list):
        return False
    if human.get("status") == "pending":
        if human.get("reviewer") is not None or human.get("date") is not None:
            return False
    elif not _text(human.get("reviewer")) or not _text(human.get("date")):
        return False

    rollback = dimensions.get("rollback")
    if not isinstance(rollback, dict) or set(rollback) != {"status", "verified", "evidence"}:
        return False
    if not isinstance(rollback.get("verified"), bool) or not _text(rollback.get("evidence")):
        return False
    if rollback.get("status") != ("pass" if rollback.get("verified") else "fail"):
        return False

    operational = dimensions.get("operational_telemetry")
    if not isinstance(operational, dict) or operational.get("behavioral_effectiveness_evidence") is not False:
        return False
    if operational.get("status") == "not_provided":
        if set(operational) != {"status", "behavioral_effectiveness_evidence", "totals", "groups"}:
            return False
        if operational.get("totals") != {} or operational.get("groups") != []:
            return False
    elif operational.get("status") not in {"observed", "truncated"}:
        return False
    return True


def _recognized_eval(value: dict[str, object], skill_id: str) -> int:
    if set(value) != _SCORECARD_KEYS:
        return 0
    if value.get("schema_version") != 1 or value.get("skill_id") != skill_id:
        return 0
    for field in ("adopted_content_sha256", "runtime_content_sha256"):
        digest = value.get(field)
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
            return 0
    disposition = value.get("recommended_disposition")
    blockers = value.get("blocking_reasons")
    if disposition not in _DISPOSITIONS:
        return 0
    if not isinstance(blockers, list) or not all(
        isinstance(item, str) and item.strip() for item in blockers
    ):
        return 0
    evaluation = value.get("evaluation")
    if not isinstance(evaluation, dict) or set(evaluation) != _EVALUATION_KEYS:
        return 0
    if not _valid_verified_at(evaluation.get("target_verified_at")):
        return 0
    if not isinstance(evaluation.get("adapter"), str) or not str(evaluation["adapter"]).strip():
        return 0
    if not isinstance(evaluation.get("isolation_method"), str) or not str(evaluation["isolation_method"]).strip():
        return 0
    revision = evaluation.get("eval_definition_revision")
    if not isinstance(revision, str) or _REVISION.fullmatch(revision) is None:
        return 0
    provenance = evaluation.get("definition_provenance")
    if not isinstance(provenance, dict) or set(provenance) != {"revision", "sha256"}:
        return 0
    if provenance.get("revision") != revision:
        return 0
    definition_hashes = provenance.get("sha256")
    if not isinstance(definition_hashes, dict) or len(definition_hashes) < 3:
        return 0
    if not all(
        _text(path)
        and isinstance(digest, str)
        and _SHA256.fullmatch(digest) is not None
        for path, digest in definition_hashes.items()
    ):
        return 0
    baseline = evaluation.get("baseline")
    if not isinstance(baseline, dict) or set(baseline) != {"kind", "identity"}:
        return 0
    if baseline.get("kind") not in {"no-skill", "previous-version"} or not _text(
        baseline.get("identity")
    ):
        return 0
    if not _valid_scorecard_dimensions(value.get("dimensions")):
        return 0
    fixture_candidates = value.get("fixture_candidates")
    if not isinstance(fixture_candidates, list):
        return 0
    for candidate in fixture_candidates:
        if not isinstance(candidate, dict) or set(candidate) != {"id", "summary", "fixture_candidate"}:
            return 0
        if not all(_text(candidate.get(key)) for key in ("id", "summary", "fixture_candidate")):
            return 0
    return 2


def _evaluation(repo_root: Path, entry: CatalogSkill) -> tuple[str, str | None, str | None, str | None, str | None, list[str]]:
    root = repo_root / ".work" / "evals" / entry.name
    if root.is_symlink():
        return "invalid", None, None, None, None, [f"linked evaluation directory rejected: {root}"]
    if not root.is_dir():
        return "not_recorded", None, None, None, None, []
    candidates: list[tuple[int, int, Path, dict[str, object]]] = []
    warnings: list[str] = []
    try:
        iteration_dirs = list(root.iterdir())
    except OSError as exc:
        return "invalid", None, None, None, None, [f"evaluation directory unreadable: {root}: {exc}"]
    for iteration_dir in iteration_dirs:
        match = _ITERATION.fullmatch(iteration_dir.name)
        if match is None:
            continue
        if iteration_dir.is_symlink():
            warnings.append(f"linked evaluation iteration rejected: {iteration_dir}")
            continue
        if not iteration_dir.is_dir():
            continue
        iteration = int(match.group(1))
        try:
            paths = list(iteration_dir.rglob("*.json"))
        except OSError as exc:
            warnings.append(f"evaluation iteration unreadable: {iteration_dir}: {exc}")
            continue
        for path in sorted(paths, key=lambda item: (str(item).casefold(), str(item))):
            value, error = _load_object(path, boundary=repo_root)
            if value is None:
                warnings.append(f"evaluation JSON invalid: {path}: {error}")
                continue
            rank = _recognized_eval(value, entry.name)
            if rank:
                candidates.append((iteration, rank, path, value))
    if not candidates:
        status = "invalid" if warnings else "not_recorded"
        return status, None, None, None, None, warnings
    _, _, path, value = max(
        candidates, key=lambda item: _candidate_order_key(item[0], item[1], item[2])
    )
    disposition = value.get("recommended_disposition")
    disposition_value = disposition if disposition in _DISPOSITIONS else None
    runtime_hash = value.get("runtime_content_sha256")
    runtime_value = runtime_hash if isinstance(runtime_hash, str) else None
    evaluation = value.get("evaluation")
    last = evaluation.get("target_verified_at") if isinstance(evaluation, dict) else None
    if not isinstance(last, str):
        last = value.get("target_verified_at")
    if not isinstance(last, str):
        review = value.get("human_review")
        last = review.get("date") if isinstance(review, dict) else None
    last_value = last if isinstance(last, str) and last else None
    status = disposition_value or "recorded"
    if runtime_value and entry.content_sha256 and runtime_value != entry.content_sha256:
        status = "stale"
        warnings.append("evaluation runtime hash does not match current canonical SKILL.md hash")
    return status, disposition_value, str(path), runtime_value, last_value, warnings


def collect_repository_evidence(
    repo_root: Path | str, entries: Iterable[CatalogSkill]
) -> dict[str, RepoEvidence]:
    root = Path(repo_root).resolve()
    result: dict[str, RepoEvidence] = {}
    for entry in sorted(entries, key=lambda item: item.name.casefold()):
        adoption_status, adopted_hash, adoption_path, adoption_warnings = _adoption(root, entry)
        eval_status, disposition, eval_path, runtime_hash, last, eval_warnings = _evaluation(root, entry)
        result[entry.name] = RepoEvidence(
            skill_id=entry.name,
            adoption_status=adoption_status,
            adopted_content_sha256=adopted_hash,
            adoption_path=adoption_path,
            evaluation_status=eval_status,
            evaluation_disposition=disposition,
            evaluation_path=eval_path,
            evaluation_runtime_sha256=runtime_hash,
            last_evaluated_at=last,
            warnings=tuple((*adoption_warnings, *eval_warnings)),
        )
    return result
