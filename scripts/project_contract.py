from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path("settings/projects/chatgpt-skill.json")
EXPECTED_REPOSITORY = "NielPieterse0/chatgpt-skill"
EXPECTED_WORK_AUTHORITY = "commissioned_kis_work_management"
EXPECTED_DISCOVERY = "capability_driven"
REQUIRED_CAPABILITIES = {
    "project_management.read",
    "project_management.write",
    "work.reconcile",
}
REQUIRED_OPERATIONS = {
    "runtime.project_management_inventory",
    "runtime.project_management_reconcile",
    "runtime.project_management_schema_status",
    "runtime.project_management_verify_traceability",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _strings(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def validate_project_contract(repo: Path) -> list[ValidationIssue]:
    path = repo / CONFIG_PATH
    if not path.is_file():
        return [ValidationIssue("PROJECT_CONTRACT_MISSING", f"missing {CONFIG_PATH.as_posix()}")]
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return [ValidationIssue("PROJECT_CONTRACT_INVALID_JSON", str(exc))]

    issues: list[ValidationIssue] = []
    repository = _mapping(data.get("repository"))
    work = _mapping(data.get("work_management"))
    project = _mapping(work.get("github_project"))
    source_scope = _mapping(work.get("source_scope"))
    identity = _mapping(work.get("identity"))

    checks = [
        (data.get("project_id") == "chatgpt-skill", "PROJECT_ID_INVALID", "project_id must be chatgpt-skill"),
        (repository.get("full_name") == EXPECTED_REPOSITORY, "REPOSITORY_INVALID", f"repository.full_name must be {EXPECTED_REPOSITORY}"),
        (work.get("authority") == EXPECTED_WORK_AUTHORITY, "WORK_AUTHORITY_INVALID", f"work_management.authority must be {EXPECTED_WORK_AUTHORITY}"),
        (work.get("discovery") == EXPECTED_DISCOVERY, "WORK_DISCOVERY_INVALID", f"work_management.discovery must be {EXPECTED_DISCOVERY}"),
        (project == {"owner": "NielPieterse0", "owner_type": "user", "number": 1}, "PROJECT_BINDING_INVALID", "github_project must bind user project NielPieterse0/1"),
        (source_scope.get("repository") == EXPECTED_REPOSITORY and source_scope.get("exact_match_required") is True, "SOURCE_SCOPE_UNSAFE", "source_scope must require an exact NielPieterse0/chatgpt-skill match"),
        (identity.get("source_kind") == "issue" and identity.get("preserve_issue_backed_identity") is True and identity.get("projection") == "github_project", "IDENTITY_CONTRACT_INVALID", "issue-backed identity must be preserved and Project treated as projection"),
    ]
    for passed, code, message in checks:
        if not passed:
            issues.append(ValidationIssue(code, message))

    missing_capabilities = sorted(REQUIRED_CAPABILITIES - _strings(work.get("required_capability_families")))
    if missing_capabilities:
        issues.append(ValidationIssue("CAPABILITY_CONTRACT_INCOMPLETE", "missing capability families: " + ", ".join(missing_capabilities)))
    missing_operations = sorted(REQUIRED_OPERATIONS - _strings(work.get("required_operations")))
    if missing_operations:
        issues.append(ValidationIssue("OPERATION_CONTRACT_INCOMPLETE", "missing operations: " + ", ".join(missing_operations)))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the repository Work Management project contract.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate settings/projects/chatgpt-skill.json")
    validate.add_argument("--repo", default=".", help="repository root (default: current directory)")
    args = parser.parse_args()

    issues = validate_project_contract(Path(args.repo).resolve())
    if issues:
        print(json.dumps({"ok": False, "errors": [issue.__dict__ for issue in issues]}, indent=2))
        return 1
    print(json.dumps({"ok": True, "contract": CONFIG_PATH.as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
