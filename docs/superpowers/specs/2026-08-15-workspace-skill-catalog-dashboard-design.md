# Workspace Skill Catalogue Dashboard Design

## Scope

Issue #56 adds a local, read-only inventory/reporting surface for the canonical Projects workspace skill catalogue. It must not mutate skills, lifecycle state, evaluation evidence, KIS telemetry, or Work Management.

## Sources and authority

1. Catalogue roots are explicit filesystem inputs, normally `C:\Projects\.agents\skills`. A direct child with `SKILL.md` is a candidate skill. The dashboard reads top-level `name`, `description`, optional `status`, and optional `category`; absent `status` defaults to `active`, matching the current KIS catalogue reader. Malformed entries remain visible with warnings rather than crashing aggregation.
2. Repository evidence is read from `skills/<skill>/adoption-manifest.json` and generated `.work/evals/<skill>/iteration-<n>/` JSON evidence when present. The highest numbered recognized iteration wins deterministically. Evaluation runtime hashes are compared with the current canonical `SKILL.md` hash so stale evidence is explicit.
3. KIS telemetry is operational context only. The preferred local source is the documented read-only SQLite store `<Projects>/.kis-mcp/telemetry/skills.sqlite3`; an exported `SkillTelemetryReport` JSON is also accepted. Telemetry never changes evaluation disposition.

## Data model

Each report row contains canonical identity/description/path/mtime/content hash/status plus separate repository and telemetry evidence objects. Missing evidence uses explicit `not_recorded`, `not_available`, or `not_observable` states rather than zero-like guesses. Warnings are stable strings and rows are sorted by canonical skill name.

Report summary fields include total canonical entries, active entries, repository-evaluated entries, unevaluated entries, and evaluation coverage. Active means canonical `status == "active"`; it is not inferred from runtime load counts.

Telemetry exposes the existing KIS counters independently. `last_used_at` is the latest retained load/resource-read/applied/completed/failed event when the SQLite event store is readable. Aggregate JSON cannot provide last-used timestamps, so that field is explicitly not observable there.

## Interfaces

- `python -m skill_catalog_dashboard --catalog-root <path>` emits JSON by default.
- Repeating `--catalog-root` supports multiple explicit roots; first-root precedence is deterministic on duplicate IDs and duplicates produce warnings.
- `--output <path>` writes the same JSON report.
- `--serve --host 127.0.0.1 --port <n>` starts a local read-only HTTP server with `/` and `/api/report` GET endpoints only.
- `--repo-root` selects repository evidence; default is the current directory.
- `--telemetry-db` or `--telemetry-json` overrides telemetry discovery. Without an override, the documented sibling KIS SQLite location is probed and absence is non-fatal.

Because this repository has no Python packaging configuration, a minimal root bootstrap package extends module lookup to `src/skill_catalog_dashboard`; all implementation remains under the requested `src/` package.

## Web surface

The HTML page is generated from the same immutable report object used by JSON output. It shows summary counts and a deterministic table with name, description, source, modified time, status, adoption/evaluation state, usage, last-used, and warnings. No forms, mutation endpoints, scripts that change state, or control-plane links are provided.

## Validation

Tests cover scalar and folded YAML frontmatter, missing/malformed `SKILL.md`, multiple catalogue roots and duplicate precedence, Windows-style paths, adoption/evaluation evidence and stale hashes, absent/malformed telemetry, SQLite aggregation and last-used timestamps, deterministic ordering/serialization, CLI smoke, and HTTP `/` plus `/api/report` smoke behavior.
