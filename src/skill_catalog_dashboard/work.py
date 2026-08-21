from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .fs import opened_path
from .models import WorkItem, WorkSnapshot
from .work_contract import WORK_CONTRACT_FINGERPRINT_KEYS

_BINDING_PATH = Path("settings/projects/chatgpt-skill.json")


@dataclass(frozen=True, slots=True)
class _WorkBinding:
    project_id: str
    repository: str
    contract_fingerprints: Mapping[str, str]


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text or null")
    return value or None


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text")
    return value.strip()


def _require_schema_v1(value: object, label: str) -> None:
    if type(value) is not int or value != 1:
        raise ValueError(f"{label} schema_version must be 1")


def _read_json(path: Path) -> Mapping[str, object]:
    with path.open("rb") as handle:
        actual = opened_path(handle)
        expected = Path(os.path.abspath(path))
        if os.path.normcase(str(actual)) != os.path.normcase(str(expected)):
            raise ValueError(f"opened JSON escaped validated path: {actual}")
        raw = handle.read()
    return _mapping(json.loads(raw.decode("utf-8")), f"JSON document {path}")


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_binding(repo_root: Path | str | None) -> _WorkBinding:
    root = Path(repo_root).expanduser().resolve() if repo_root is not None else _default_repo_root()
    payload = _read_json(root / _BINDING_PATH)
    _require_schema_v1(payload.get("schema_version"), "project binding")
    project_id = _required_text(payload.get("project_id"), "project binding project_id")
    repository = _mapping(payload.get("repository"), "project binding repository")
    full_name = _required_text(repository.get("full_name"), "project binding repository.full_name")
    work = _mapping(payload.get("work_management"), "project binding work_management")
    source_scope = _mapping(work.get("source_scope"), "project binding source_scope")
    scoped_repository = _required_text(
        source_scope.get("repository"), "project binding source_scope.repository"
    )
    if source_scope.get("exact_match_required") is not True or scoped_repository != full_name:
        raise ValueError("project binding must require exact repository source scope")
    fingerprints = _mapping(
        work.get("contract_fingerprints"), "project binding contract_fingerprints"
    )
    if set(fingerprints) != WORK_CONTRACT_FINGERPRINT_KEYS:
        raise ValueError("project binding must declare the canonical Work contract fingerprint identities")
    normalized_fingerprints: dict[str, str] = {}
    for name in sorted(WORK_CONTRACT_FINGERPRINT_KEYS):
        digest = _required_text(fingerprints.get(name), f"contract fingerprint {name}")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError(f"contract fingerprint {name} must be lowercase sha256")
        normalized_fingerprints[name] = digest
    return _WorkBinding(
        project_id=project_id,
        repository=full_name,
        contract_fingerprints=normalized_fingerprints,
    )


def _unwrap(payload: Mapping[str, object]) -> Mapping[str, object]:
    result = payload.get("result")
    if isinstance(result, dict) and "project_id" in result:
        _require_schema_v1(payload.get("schema_version"), "Work Management envelope")
        return result
    return payload


def _parse_card(value: object, binding: _WorkBinding) -> WorkItem:
    card = _mapping(value, "Work Management card")
    repository = _required_text(card.get("repository"), "Work Management card repository")
    if repository.casefold() != binding.repository.casefold():
        raise ValueError(f"Work Management card repository is outside {binding.repository}")
    number = card.get("number")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError("Work Management card number must be a positive integer")
    title = _required_text(card.get("title"), "Work Management card title")
    item_id = _required_text(card.get("item_id"), "Work Management card item_id")
    source_state = _required_text(
        card.get("source_state"), "Work Management card source_state"
    ).casefold()
    if source_state not in {"open", "closed"}:
        raise ValueError("Work Management card source_state must be open or closed")
    work_state = _required_text(card.get("work_state"), "Work Management card work_state")
    url = _required_text(card.get("url"), "Work Management card url")
    expected_url = f"https://github.com/{binding.repository}/issues/{number}"
    if url.casefold() != expected_url.casefold():
        raise ValueError("Work Management card must retain its issue-backed source URL")
    return WorkItem(
        item_id=item_id,
        number=number,
        title=title,
        url=url,
        repository=repository,
        source_state=source_state,
        work_state=work_state,
        priority=_optional_text(card.get("priority"), "priority"),
        effort=_optional_text(card.get("effort"), "effort"),
        execution_owner=_optional_text(card.get("execution_owner"), "execution_owner"),
        blocked_by=_optional_text(card.get("blocked_by"), "blocked_by"),
    )


def _order(item: WorkItem) -> tuple[int, str, str]:
    return (item.number, item.item_id.casefold(), item.item_id)


def _load_source_issues(
    path: Path | str, binding: _WorkBinding
) -> dict[int, str]:
    selected = Path(path).expanduser().resolve()
    if not selected.is_file():
        raise ValueError(f"source issue export unavailable: {selected}")
    payload = _read_json(selected)
    _require_schema_v1(payload.get("schema_version"), "source issue export")
    if payload.get("scope") != "open_issues":
        raise ValueError("source issue export scope must be open_issues")
    repository = _required_text(payload.get("repository"), "source issue export repository")
    if repository.casefold() != binding.repository.casefold():
        raise ValueError("source issue export repository does not match project binding")
    complete = payload.get("complete")
    truncated = payload.get("truncated")
    if complete is not True or truncated is not False:
        raise ValueError("source issue export must be complete and non-truncated")
    issues = payload.get("issues")
    if not isinstance(issues, list):
        raise ValueError("source issue export issues must be an array")
    states: dict[int, str] = {}
    for raw in issues:
        issue = _mapping(raw, "source issue")
        number = issue.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            raise ValueError("source issue number must be a positive integer")
        state = _required_text(issue.get("state"), "source issue state").casefold()
        if state != "open":
            raise ValueError("source issue export may contain only open issues")
        url = _required_text(issue.get("url"), "source issue url")
        expected_url = f"https://github.com/{binding.repository}/issues/{number}"
        if url.casefold() != expected_url.casefold():
            raise ValueError("source issue must retain its repository issue URL")
        if number in states:
            raise ValueError("source issue export contains duplicate issue numbers")
        states[number] = state
    return states


def _validate_schema_status(path: Path | str, binding: _WorkBinding) -> None:
    selected = Path(path).expanduser().resolve()
    if not selected.is_file():
        raise ValueError(f"Work Management schema-status export unavailable: {selected}")
    payload = _read_json(selected)
    _require_schema_v1(payload.get("schema_version"), "Work Management schema-status")
    if payload.get("project_id") != binding.project_id:
        raise ValueError("Work Management schema-status project_id does not match project binding")
    for field in ("missing_fields", "type_mismatches", "missing_options"):
        value = payload.get(field)
        if not isinstance(value, list):
            raise ValueError(f"Work Management schema-status {field} must be an array")
        if value:
            raise ValueError(f"Work Management schema-status reports {field}: {value}")
    if payload.get("fields_ready") is not True:
        raise ValueError("Work Management schema-status fields_ready must be true")


def _validate_contract_identity(path: Path | str, binding: _WorkBinding) -> None:
    selected = Path(path).expanduser().resolve()
    if not selected.is_file():
        raise ValueError(f"Work Management contract export unavailable: {selected}")
    payload = _read_json(selected)
    _require_schema_v1(payload.get("schema_version"), "Work Management contract")
    canonical = _mapping(payload.get("canonical_contracts"), "canonical Work contracts")
    fingerprints = _mapping(canonical.get("fingerprints"), "canonical Work fingerprints")
    if dict(fingerprints) != dict(binding.contract_fingerprints):
        raise ValueError(
            "Work Management contract fingerprints do not match the repository binding"
        )


def load_work_management_json(
    path: Path | str | None,
    *,
    repo_root: Path | str | None = None,
    source_issues_json: Path | str | None = None,
    schema_status_json: Path | str | None = None,
    contract_json: Path | str | None = None,
) -> WorkSnapshot:
    if path is None:
        return WorkSnapshot(items=(), status="not_available", source=None)
    selected = Path(path).expanduser().resolve()
    if not selected.is_file():
        return WorkSnapshot(items=(), status="not_available", source=str(selected))
    try:
        binding = _load_binding(repo_root)
        payload = _unwrap(_read_json(selected))
        _require_schema_v1(payload.get("schema_version"), "Work Management export")
        if payload.get("project_id") != binding.project_id:
            raise ValueError(
                f"Work Management export project_id must be {binding.project_id}"
            )
        repository = _required_text(payload.get("repository"), "Work Management export repository")
        if repository.casefold() != binding.repository.casefold():
            raise ValueError(
                f"Work Management export repository must be {binding.repository}"
            )
        complete = payload.get("complete")
        truncated = payload.get("truncated")
        if not isinstance(complete, bool) or not isinstance(truncated, bool):
            raise ValueError("Work Management export complete and truncated must be booleans")
        if not complete or truncated:
            reasons = []
            if not complete:
                reasons.append("incomplete evidence")
            if truncated:
                reasons.append("truncated evidence")
            return WorkSnapshot(
                items=(),
                status="incomplete",
                source=str(selected),
                warnings=("Work Management export reports " + " and ".join(reasons),),
            )
        cards = payload.get("cards")
        if not isinstance(cards, list):
            raise ValueError("Work Management export cards must be an array")
        parsed = [_parse_card(raw, binding) for raw in cards]
        item_ids = [item.item_id for item in parsed]
        issue_numbers = [item.number for item in parsed]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("Work Management export contains duplicate item_id values")
        if len(issue_numbers) != len(set(issue_numbers)):
            raise ValueError("Work Management export contains duplicate source issue numbers")
        open_items = [item for item in parsed if item.source_state == "open"]
        open_items.sort(key=_order)
        warnings: list[str] = []
        if payload.get("include_history") is not True:
            raise ValueError(
                "Work Management export must be requested with include_history=true"
            )
        if source_issues_json is None:
            warnings.append(
                "Work Management open-issue coverage is unverified; provide a complete open-issue export"
            )
        else:
            expected_open = set(_load_source_issues(source_issues_json, binding))
            projected_open = {item.number for item in open_items}
            missing = sorted(expected_open - projected_open)
            extra = sorted(projected_open - expected_open)
            if missing or extra:
                raise ValueError(
                    "Work Management open issue coverage mismatch: "
                    f"missing={missing}, extra={extra}"
                )
        if schema_status_json is None:
            warnings.append(
                "Work Management field-schema status is unverified; provide a KIS schema-status export"
            )
        else:
            _validate_schema_status(schema_status_json, binding)
        if contract_json is None:
            warnings.append(
                "Work Management contract identity is unverified; provide a KIS project_management_contract export"
            )
        else:
            _validate_contract_identity(contract_json, binding)
        if warnings:
            return WorkSnapshot(
                items=tuple(open_items),
                status="unverified",
                source=str(selected),
                warnings=tuple(warnings),
            )
        return WorkSnapshot(
            items=tuple(open_items),
            status="observed",
            source=str(selected),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return WorkSnapshot(
            items=(),
            status="invalid",
            source=str(selected),
            warnings=(f"Work Management export invalid: {exc}",),
        )
