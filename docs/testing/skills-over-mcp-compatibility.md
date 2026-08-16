# Skills over MCP Compatibility Evaluation

## Scope

Issue 030 / #50 evaluates whether the emerging MCP Skills transport should replace, complement, or be deferred relative to the current KIS Skills module. This evaluation is bounded to compatibility; it does not perform #54/#55 catalogue effectiveness work or #56 dashboard work.

## Current external status

Verified 2026-08-15 against the canonical MCP repository:

- SEP-2640 remains an open **Draft Extensions Track** proposal at head `d29bd05222b4732d7b665b552abee532a8c200fa`.
- The current draft exposes Agent Skills over MCP through `skills/list`, `skills/get`, ordinary resources, and optional `resources/directory/read`.
- Current entries bind the top-level `SKILL.md` URI and the complete supporting-file set to SHA-256 digests when the content is pre-digestible.
- The draft forbids implicit host-side execution or implicit `allowed-tools` permission elevation for MCP-origin skills.
- The cited TypeScript reference work is `modelcontextprotocol/experimental-ext-skills#71`; that PR is closed without merge. Working Group notes describe a transition toward official SDK integration as the extension stabilizes.

## KIS real-skill execution

Shared skill: `modularity-assessment`

Observed through the live KIS Skills surface:

| Check | Observation |
|---|---|
| `search_skills` | Returned active `modularity-assessment`. |
| `load_skill` | Snapshot `c4ada48dff958cd9`; entrypoint SHA-256 `f5f251f3a4aeb310d752b5e5624c080461db761cd1b31222bd9c985c4d2f54fb`; 7 files. |
| `search_skill_files("md")` | `SKILL.md` plus four reference files. |
| `search_skill_files("py")` | `scripts/seams.py`. |
| `search_skill_files("agents")` | `agents/openai.yaml`. |
| `read_skill_file` | `references/output-spec.md` read successfully with SHA-256 `ca776a523348c2b2342c41071a0e6bda7d100868947f8f3f9816fd6489ae3efb`. |
| KIS telemetry | 1 load, 1 resource read, 0 errors for this activation/version/project; 2 duration samples; tokens/tool calls/retries/verification samples unavailable. |

This confirms KIS already provides progressive disclosure, snapshot identity, per-resource integrity, and activation-linked operational telemetry.

## Experimental MCP projection

Command:

```powershell
python scripts/skills_over_mcp_compat.py `
  --skill-dir 'C:\Projects\.agents\skills\modularity-assessment' `
  --skill-id modularity-assessment `
  --entrypoint-sha256 f5f251f3a4aeb310d752b5e5624c080461db761cd1b31222bd9c985c4d2f54fb `
  --file-count 7 `
  --snapshot-id c4ada48dff958cd9 `
  --resource-hash 'references/output-spec.md=ca776a523348c2b2342c41071a0e6bda7d100868947f8f3f9816fd6489ae3efb' `
  --output '.work\skills-over-mcp\modularity-assessment-projection.json'
```

Observed result:

- KIS skill ID matched frontmatter name and directory identity.
- KIS entrypoint hash matched the local canonical bytes.
- KIS file count matched exactly: 7.
- The KIS supporting-file digest matched the projected `references/output-spec.md` bytes exactly.
- All 7 files were emitted as individual `skill://modularity-assessment/...` resources with SHA-256 digests.
- Supporting files included references, `scripts/seams.py`, and `agents/openai.yaml`.
- No permission grant or script execution occurred.

Generated evidence: `.work/skills-over-mcp/modularity-assessment-projection.json`.

## Automated compatibility tests

`python -m unittest tests.test_skills_over_mcp_compat -v`

Result: **9 tests run; 7 passed; 2 Windows symlink tests skipped because symlink creation may require developer privileges.**

Covered behavior:

- complete resource enumeration across `SKILL.md`, references, scripts, and assets;
- `skill://<name>/<path>` mapping;
- `sha256:<hex>` digest generation;
- preservation of frontmatter in the transport projection without applying `allowed-tools` permissions;
- fail-closed KIS entrypoint-hash mismatch;
- fail-closed KIS file-count mismatch;
- fail-closed supporting-resource digest mismatch;
- nonexistent-directory and missing-`SKILL.md` rejection;
- root and internal linked-path rejection where symlink testing is supported.

## Evaluation-standard mapping

| Layer | #50 evidence | Result |
|---|---|---|
| Structural correctness | Real skill parses and all files project deterministically. | Pass |
| Trigger behavior | Transport does not alter the skill description or activation policy; no new repeated model trigger runs were executed. | Not newly observed |
| Output quality | Transport does not alter instruction bytes; no new candidate-vs-baseline model output runs were executed. | Not newly observed |
| Efficiency | KIS exposed duration samples for load/read; token/tool/retry samples were unavailable. | Partially observed |
| Abuse/safety | Projector is read-only, rejects linked paths, fails closed on identity/digest mismatch, and never applies permission grants. | Pass for implemented slice |
| Runtime compatibility | KIS-delivered skill maps losslessly to the draft URI/resource/digest shape for the tested package. | Pass for experimental projection |

The unobserved trigger/output dimensions are not treated as passes. A production MCP adapter would require fresh isolated model runs under the repository evaluation standard.

## Differences and unsupported behavior

- KIS has searchable local catalogue semantics; draft `skills/list` may be partial/empty and does not standardize semantic search.
- KIS has activation/project/request telemetry and outcome reporting; SEP-2640 does not mandate equivalent usage reporting.
- KIS snapshot IDs provide catalogue-wide immutable identity; SEP entries bind content by URI+digest set rather than a catalogue snapshot ID.
- SEP origin/collision/approval semantics are host concerns and are not implemented by this evidence projector.
- Remote resource fetching, origin-scoped reads, content-bound approval persistence, cache isolation, capability negotiation, `skills/list`, `skills/get`, and `resources/directory/read` are intentionally not implemented.
- No production server or host has been changed.

## Disposition

**Compatibility: complement. Production adoption: defer. Replacement: reject at this stage.**

The draft transport is structurally compatible with KIS skill bytes and can add future cross-server distribution value, but it does not replace KIS governance, search, snapshot authority, or telemetry. The implemented projector preserves that boundary and gives a reproducible compatibility check without creating duplicate authority.
