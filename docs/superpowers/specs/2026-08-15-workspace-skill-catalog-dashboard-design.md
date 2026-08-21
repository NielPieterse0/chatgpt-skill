# Workspace Skill Catalogue Dashboard Design

## Scope

Issue #56 adds a local, read-only inventory/reporting surface for the canonical Projects workspace skill catalogue. It must not mutate skills, lifecycle state, evaluation evidence, KIS telemetry, or Work Management.

## Sources and authority

1. Catalogue roots are explicit filesystem inputs, normally `C:\Projects\.agents\skills`. A direct child with `SKILL.md` is a candidate skill. The dashboard reads top-level `name`, `description`, optional `status`, and optional `category`; absent `status` defaults to `active`, matching the current KIS catalogue reader. Malformed entries remain visible with warnings rather than crashing aggregation.
2. Repository evidence is read from `skills/<skill>/adoption-manifest.json` and generated `.work/evals/<skill>/iteration-<n>/` JSON evidence when present. The highest numbered recognized iteration wins deterministically. Evaluation runtime hashes are compared with the current canonical `SKILL.md` hash so stale evidence is explicit.
3. KIS telemetry is operational context only. The preferred local source is the documented read-only SQLite store `<Projects>/.kis-mcp/telemetry/skills.sqlite3`; an exported `SkillTelemetryReport` JSON is also accepted. Telemetry never changes evaluation disposition.
4. Work Management projection uses the repository-owned binding in `settings/projects/chatgpt-skill.json`; dashboard code must not duplicate the project ID or repository identity. GitHub issues are authoritative for source identity and source open/closed status. KIS Work Management is authoritative for operational lifecycle state, ownership, priority, effort, dependencies, and eligibility. An exported `project_management_board_data` snapshot provides KIS fields and must be complete, non-truncated, and requested with `include_history=true`. A separate complete `open_issues` source export verifies the exact current open GitHub issue population; exported KIS `project_management_schema_status` verifies field commissioning (`fields_ready` with no missing fields, type mismatches, or missing options); exported KIS `project_management_contract` must match the canonical Work contract fingerprints pinned in the repository binding. Until all checks pass, Work rows may be displayed only as `unverified` and aggregate Work counts remain unavailable. Next-work eligibility is intentionally not part of the dashboard contract.

## Data model

Each report row contains canonical identity/description/path/mtime/content hash/status plus separate repository and telemetry evidence objects. Missing evidence uses explicit `not_recorded`, `not_available`, or `not_observable` states rather than zero-like guesses. Warnings are stable strings and rows are sorted by canonical skill name.

Report schema version 2 adds a top-level `work` projection and `sources.work_management`. Work rows preserve issue identity plus KIS-provided lifecycle fields verbatim. `work_item_count` and `work_state_counts` are populated only when exact open-issue coverage, `include_history=true`, KIS field-schema readiness, and the repository-pinned KIS Work contract identity have all been independently verified; otherwise they are null so missing evidence cannot look like an empty queue. No next-work or eligibility marker is serialized.

Report summary fields also include total canonical entries, active entries, repository-evaluated entries, unevaluated entries, and evaluation coverage. Active means canonical `status == "active"`; it is not inferred from runtime load counts.

Telemetry exposes the existing KIS counters independently. `last_used_at` is the latest retained load/resource-read/applied/completed/failed event when the SQLite event store is readable. Aggregate JSON cannot provide last-used timestamps, so that field is explicitly not observable there.

## Interfaces

- `python -m skill_catalog_dashboard --catalog-root <path>` emits JSON by default.
- Repeating `--catalog-root` supports multiple explicit roots; first-root precedence is deterministic on duplicate IDs and duplicates produce warnings.
- `--output <path>` writes the same JSON report.
- `--serve --host 127.0.0.1 --port <n>` starts a local read-only HTTP server with `/` and `/api/report` GET endpoints only.
- `--repo-root` selects repository evidence and the repository-owned Work Management binding; default is the current directory.
- `--telemetry-db` or `--telemetry-json` overrides telemetry discovery. Without an override, the documented sibling KIS SQLite location is probed and absence is non-fatal.
- `--work-management-json` accepts an exported KIS `project_management_board_data` snapshot. The snapshot must be complete, non-truncated, scoped to the bound repository, and requested with `include_history: true`; otherwise it is invalid and no Work rows are exposed.
- `--source-issues-json` optionally verifies current open-issue coverage. It accepts schema version 1 with `scope: "open_issues"`, repository identity, `complete: true`, `truncated: false`, and an `issues` array of open `{number, state, url}` records. The issue numbers must exactly match open Project cards; mismatches fail closed as `invalid`.
- `--work-schema-status-json` optionally accepts exported KIS `project_management_schema_status`. `fields_ready` must be true and `missing_fields`, `type_mismatches`, and `missing_options` must all be empty. View readiness is intentionally not used as a metadata gate.
- `--work-contract-json` optionally accepts exported KIS `project_management_contract`. Its canonical Work fingerprints must exactly match `work_management.contract_fingerprints` in the repository binding. Open-issue coverage, history inclusion, field-schema evidence, and contract identity are all required before Work status becomes `observed`.
- The dashboard never publishes next-work eligibility. Call live KIS `project_management_next_work` or the take-next workflow for selection and claiming.

Because this repository has no Python packaging configuration, a minimal root bootstrap package extends module lookup to `src/skill_catalog_dashboard`; all implementation remains under the requested `src/` package.

## Web surface

The HTML page is generated from the same immutable report object used by JSON output. It shows summary counts and a deterministic table with name, description, source, modified time, status, adoption/evaluation state, usage, last-used, and warnings. No forms, mutation endpoints, scripts that change state, or control-plane links are provided.

## Validation

Tests cover scalar and folded YAML frontmatter, missing/malformed `SKILL.md`, multiple catalogue roots and duplicate precedence, Windows-style paths, adoption/evaluation evidence and stale hashes, absent/malformed telemetry, SQLite aggregation and last-used timestamps, deterministic ordering/serialization, CLI smoke, and HTTP `/` plus `/api/report` smoke behavior.
