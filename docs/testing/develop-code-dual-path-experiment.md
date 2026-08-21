# Develop-code Dual-path Experiment

## Authority

Issue #93 runs the first natural-competition pilot for the canonical `develop-code` skill. The canonical workspace remains the skill-content authority, KIS remains the telemetry authority, and the repository read-only MCP adapter remains the transport implementation under test.

This report does not create telemetry, infer missing events, or authorize changes to the `kis-mcp` repository.

## Experiment invariant

Both delivery arms must expose the same immutable skill identity before any transport comparison is valid:

- skill: `develop-code`;
- canonical `SKILL.md` SHA-256: `10ab0e8457b53d1940d27cb70ac3a96d0088636e7c5437a17fc769c68d4a5288`;
- native arm: commissioned KIS Skills delivery;
- MCP arm: read-only `skill://develop-code/SKILL.md` resource delivery;
- catalogue enumeration is exposure only and is not meaningful use.

The skill description, package bytes, permissions, scripts, and support resources must not differ between arms.

## Evidence snapshot — 2026-08-21

The live KIS `skill_delivery_telemetry_report` for `develop-code` is complete (`truncated: false`) and contains four `kis_native` groups at the exact canonical hash. Across those groups it records 162 entrypoint loads, 78 support-resource reads, one completion, and no failures or errors.

The unscoped native group alone records 92 loads and 33 resource reads, confirming that `develop-code` has enough natural native activity to remain the preferred pilot candidate.

## MCP arm readiness

The repository adapter can already project and serve the same canonical bytes. A direct local adapter check against the canonical workspace produced:

- entry URI `skill://develop-code/SKILL.md`;
- 8 projected resources;
- successful `skills/get` for the entry URI;
- successful `resources/read` for `SKILL.md`;
- returned-byte SHA-256 exactly equal to `10ab0e8457b53d1940d27cb70ac3a96d0088636e7c5437a17fc769c68d4a5288`.

This proves repository-side transport parity. It does not prove that a client currently sees or naturally selects that MCP arm.

## Current comparison

KIS currently reports no `mcp_resource` group for `develop-code` at any project scope. The repository projection therefore returns:

- `comparable_identity_count: 0`;
- native totals: 162 loads and 78 resource reads;
- MCP totals: 0 loads and 0 resource reads;
- comparison reason for every observed identity: `missing_mcp_resource`.

The source report is complete, so these zero MCP counts are evidence of an absent observed arm, not report truncation. They are not evidence that users prefer native delivery because the MCP arm is not currently observed as simultaneously available.

## Decision

**Pilot status: blocked on external MCP-arm exposure/telemetry.** Repository-side content parity and read-only MCP serving are ready, but natural competition has not started. Do not infer selection rate, relative effectiveness, or transport preference from this snapshot, and do not start catalogue-wide rollout under #95.

## External KIS handoff

KIS implementation owners need to make the already-built read-only MCP Skills arm available for `develop-code` in the same client/runtime population as the native arm and ensure actual MCP entrypoint/resource reads reach the existing delivery telemetry plane.

Required semantics:

1. Use canonical skill ID `develop-code` and exact content SHA-256 `10ab0e8457b53d1940d27cb70ac3a96d0088636e7c5437a17fc769c68d4a5288`.
2. Do not alter or copy the canonical skill package to create the MCP arm.
3. Keep passive catalogue/startup discovery outside meaningful load/read counts.
4. Emit `mcp_resource` only for actual served/read content and retain digest verification.
5. Preserve current `kis_native` behavior and the existing `skill_delivery_telemetry_report` contract.
6. Do not grant script execution, new permissions, or mutation authority through MCP exposure.

Acceptance evidence for the handoff is one natural client-visible period in which `skill_delivery_telemetry_report(skill_id="develop-code")` contains same-hash `kis_native` and `mcp_resource` groups, with clean MCP digest coverage and no catalogue-enumeration inflation. Once that exists, rerun this experiment before deciding transport viability.

## Reproduction

Save the filtered KIS report to `.work/evals/develop-code/delivery-experiment/kis-delivery-report.json`, then run:

```text
python scripts/skill_delivery_comparison.py --input .work/evals/develop-code/delivery-experiment/kis-delivery-report.json --output .work/evals/develop-code/delivery-experiment/projection.json --skill develop-code --content-sha256 10ab0e8457b53d1940d27cb70ac3a96d0088636e7c5437a17fc769c68d4a5288
```
