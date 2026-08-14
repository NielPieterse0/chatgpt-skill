# OpenAI-Optimized MCP Skill Pack Evaluation

## Status

Evaluation evidence for issue #47, captured 2026-08-14 against the canonical Projects workspace catalogue at `C:\Projects\.agents\skills`.

These skills are operational shared-catalogue packages. They are not admitted into this repository's P0 `skills/` runtime.

## Candidate pack

| Skill | Active entrypoint SHA-256 | Files | Role |
|---|---|---:|---|
| `mcp-development` | `715ff50a8fc19bf21f5d5ff32a17c603dd85b79af78727171ef9ee8df9d3d174` | 4 | Protocol/interoperability umbrella |
| `openai-mcp-server` | `d79239e82c8b7e5f8b2978e67153527fa0e4bf24362d6063b44a5d1b6f465c54` | 1 | OpenAI-targeted MCP server implementation |
| `openai-mcp-app-ui` | `0cb19011cd042706510c8a72cca0028db6dedfa85492e8b69b4a36fd44e35854` | 1 | OpenAI-facing MCP Apps UI |
| `mcpb-local-packaging` | `b373a685dc233d16ffa7d80261e6bd75a2a619feb03d1bfce739400016aeefc8` | 3 | Anthropic MCPB local packaging |

KIS structural `evaluate_skill` passed for all four on snapshot `045d01d641888f56` with the hashes above. `search_skills("build-mcp")` returned no old specialist identities, and a bounded canonical-root content scan found no references to `build-mcp-server`, `build-mcp-app`, or `build-mcpb`.

## Source freshness verification

Current primary-source verification on 2026-08-14 supports the pack's key host/portability boundaries:

- OpenAI's current ChatGPT developer-mode guidance says ChatGPT connects to remote MCP servers rather than directly to local MCP servers, with Secure MCP Tunnel as the supported private/local reachability path.
- The same guidance says `search` and `fetch` tools are no longer required and documents explicit tool scanning/refresh behavior for changed app actions.
- OpenAI describes the Apps SDK as built on MCP and extending it with ChatGPT app logic/UI while retaining an open-standard basis.
- OpenAI's current Plugin model can combine skills and apps; app permissions remain the authority for connected data/actions.
- The official MCP Apps project identifies `2026-01-26` as its stable specification and documents `_meta.ui.resourceUri` as the preferred tool-to-UI linkage; the flat `_meta["ui/resourceUri"]` form is deprecated.
- MCP Apps keeps tool data and registered UI resources separate, and non-App hosts can retain the underlying standard tool behavior.

Verification sources:

- OpenAI: `https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt`
- OpenAI: `https://help.openai.com/en/articles/12515353-build-with-the-apps-sdk`
- OpenAI: `https://help.openai.com/en/articles/20001256-plugins-in-codexOpenAI`
- MCP Apps: `https://github.com/modelcontextprotocol/ext-apps`
- MCP Apps stable spec: `https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx`

No external source package was imported into repository authority during this verification; the checks validate the existing operational catalogue against current primary-source behavior.

## Trigger, output, and abuse definitions

Repository-owned definitions now exist under `tests/skills/` for all four active identities. Each contains 6 positives, 6 near-misses, 2 conflicts, 2 prompt-injection cases, 3 representative output cases, and 8 abuse cases.

`python -m unittest tests.test_mcp_skill_pack_evals -v` passes and checks the required evaluation minimums, confirms the operational packages are not repository runtime admissions, and prevents the three retired specialist identities from becoming repository test/runtime targets.

The cases exercise the critical pack boundaries: protocol review versus implementation, server versus custom UI, portable MCP Apps versus OpenAI extensions, and local MCPB packaging versus remote OpenAI deployment.

## Static boundary assessment

- **`mcp-development`: pass.** It owns protocol/interoperability architecture and explicitly routes straightforward OpenAI server, interactive UI, and MCPB packaging outcomes to specialists.
- **`openai-mcp-server`: pass.** It owns OpenAI-targeted server construction and tool/server metadata while routing protocol-centric review, custom UI, and MCPB distribution elsewhere.
- **`openai-mcp-app-ui`: pass.** It requires a useful underlying tool first, uses portable MCP Apps semantics before OpenAI-only extensions, and rejects ordinary frontend work or text-only tool changes.
- **`mcpb-local-packaging`: pass.** It is explicitly scoped to Anthropic local stdio distribution and states that MCPB is packaging rather than MCP transport, authorization, or ChatGPT deployment.

## Limitations

- The current environment exposes structural skill evaluation but not isolated automatic activation scoring, so trigger precision/recall is unmeasured.
- The output cases are regression definitions and instruction-contract review evidence; repeated candidate-vs-baseline model executions have not been run, so no quantitative quality delta is claimed.
- This issue does not change repository P0 skill admission or enable `config/runtime-control.json`.

## Release assessment

The four-skill pack has distinct user-intent ownership, current specialist identities, no stale `build-mcp-*` catalogue references, current primary-source alignment for OpenAI and MCP Apps boundaries, and repository-owned trigger/output/abuse regression definitions.

It is suitable to remain active in the canonical Projects workspace catalogue. Governed repository closeout still requires repository-wide verification, review/merge, observed `main`, and Project/source reconciliation.
