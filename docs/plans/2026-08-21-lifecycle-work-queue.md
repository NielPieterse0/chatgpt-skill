# Lifecycle Work Queue Plan

## Scope

Issue #79 makes pending lifecycle work visible without turning the dashboard into a control plane.

The dashboard will consume an optional exported KIS Work Management `project_management_board_data` snapshot. GitHub issues remain authoritative for source identity and source open/closed status. KIS Work Management remains authoritative for operational lifecycle state, ownership, priority, effort, dependencies, and eligibility. The dashboard is a read-only projection of those separate authorities.

## Implementation

1. Reconcile the complete repository issue set into Work Project `NielPieterse0/1`; every open issue must be present, closed issues remain historical records, and current KIS metadata/dependency rules apply before claim or closeout.
2. Encode that completeness rule in `settings/projects/chatgpt-skill.json` and validate it in `scripts/project_contract.py` so future agents cannot treat partial Project coverage as acceptable.
3. Add a bounded Work Management snapshot loader that accepts the KIS result object or result envelope, reads project identity from the repository-owned binding, rejects foreign-repository cards, requires complete non-truncated evidence, and validates issue-backed identity. Validate any raw `next_eligible_item_id` only for referential integrity; do not publish it through the dashboard.
4. Project open source-issue cards into a separate lifecycle work queue with source issue URL and KIS-provided Work state, priority, effort, blocker, and execution owner. Preserve KIS lifecycle values verbatim; do not locally redefine their enums or validity rules.
5. Keep Work rows outside skill catalogue/evaluation totals and intake candidate totals. Plugin-related Work rows remain in this separate population until issue #76 adds the dedicated plugin projection.
6. Add `--work-management-json`, optional `--source-issues-json`, optional `--work-schema-status-json`, and optional `--work-contract-json` to the read-only dashboard CLI and expose the same queue in JSON and HTML. The source export verifies the complete current open GitHub issue population; `include_history=true` on the KIS board export proves historical Project rows were requested; KIS schema-status evidence verifies required Work fields/types/options; KIS contract evidence must match the repository-pinned canonical Work contract fingerprints. Bump the dashboard report schema to version 2 for the new public `work` projection.
7. Group verified rows by their verbatim KIS lifecycle state. Keep unverified rows visibly `unverified`. The dashboard deliberately does not expose next-work eligibility; selection and claiming remain live KIS `project_management_next_work` / take-next operations.
8. Add focused tests for source-scope rejection, incomplete evidence, identity integrity, KIS-field preservation, deterministic ordering, count isolation, CLI input, and HTML visibility.

## Gates

- Source-to-Project completeness is fail-closed: missing open issues, stale dependency state, or current KIS metadata gaps block claim and closeout until reconciled.
- The dashboard must remain read-only and must never create or update Work records.
- Every projected Work row must retain an issue-backed source link.
- Missing or unverified Work evidence must remain explicit (`not_available`, `invalid`, `incomplete`, or `unverified`); schema-v2 aggregate Work counts remain unavailable unless complete open-issue coverage, `include_history=true`, KIS field-schema readiness, and the repository-pinned KIS Work contract identity are all verified. Next-work eligibility is never serialized by the dashboard.
- Plugin Work rows must not change skill coverage denominators.
- Focused dashboard tests, project contract validation, `git diff --check`, and repository verification must pass before closeout.
