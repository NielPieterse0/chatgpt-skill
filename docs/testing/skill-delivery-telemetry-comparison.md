# Skill Delivery Telemetry Comparison

## Authority

Issue #92 consumes the commissioned KIS `skill_delivery_telemetry_report`. KIS remains authoritative for telemetry emission, persistence, event semantics, correlation, and delivery-path aggregation.

This repository adds only a strict validation/projection layer for evaluation and later dashboard consumption. It does not read or write KIS event storage, emit synthetic telemetry, or create an MCP-only telemetry authority.

## Current commissioned contract

Verified on 2026-08-21, the live report groups the same canonical skill identity by:

- `skill_id`;
- exact `content_sha256`;
- optional `project_id`;
- `delivery_path`: `kis_native` or `mcp_resource`.

Meaningful counts cover load, resource read, application, completion, failure, error, and MCP digest verification. Passive catalogue exposure is reported separately as `catalogue_exposure_count`; it must not be reclassified as meaningful use.

## Comparison rule

A transport identity comparison is valid only when both delivery paths exist for the same tuple of `skill_id`, `content_sha256`, and `project_id`. A native row at one hash and an MCP row at another hash are two non-comparable identities, never a transport pair. For a claimed same-hash MCP pair, every meaningful MCP load or resource read must have exactly one digest-verification result, and all of those results must pass.

The repository validator independently derives that rule from the groups and requires KIS's supplied `comparisons` entries to agree. Unknown fields, duplicate path groups, missing comparison rows, invalid counts, unsupported paths, inconsistent comparison reasons, missing MCP digest verification, or any MCP digest failure fail closed.

The validator can filter by skill, project, and content hash, but filtering never changes the comparison semantics or merges identities. `comparisons[].comparable` means the canonical identity pair is valid; it does not mean aggregate usage totals are complete. When KIS marks the source report `truncated`, the projection preserves the identity pairing but sets `metric_comparison_eligible: false` and `metric_comparison_status: truncated`, so downstream evaluation cannot treat partial counts as a complete native-vs-MCP metric comparison.

## Observability gap

The current aggregate report does not expose resource URI/class, MCP server/origin identity, or request/activation correlation. Those details remain an explicit KIS-side handoff recorded on #92. This repository must not infer them from aggregate counts.

## Usage

```text
python scripts/skill_delivery_comparison.py --input <kis-delivery-report.json> --output <projection.json>
```

Optional `--skill`, `--project <id>`, and `--content-sha256` filters produce a bounded derived view. Use `--null-project` to select the distinct `project_id: null` identity; omitting both project options means all projects. The output records that filter mode explicitly.

When `--output` is used, an existing projection is removed before input validation and a successful result is published atomically. A failed rerun therefore cannot leave an older projection looking current. Input and output paths must be different.

The output is operational context only and must not alter behavioral effectiveness or release disposition.
