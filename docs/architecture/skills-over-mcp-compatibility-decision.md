# Skills over MCP Compatibility Decision

## Decision

**Complement KIS with a read-only compatibility projection and defer production MCP Skills adoption until SEP-2640 is stable.**

KIS remains the authority for the canonical workspace catalogue, skill discovery/load/resource reads, activation identity, telemetry, Work Management, and execution controls. Draft MCP Skills is treated as a transport/distribution shape that can project the same approved skill bytes outward; it is not a replacement lifecycle, permission model, or second source of truth.

## Status verified 2026-08-15

- Canonical MCP PR `modelcontextprotocol/modelcontextprotocol#2640` is still open and labels the proposal **Draft / Extensions Track**. Verified head: `d29bd05222b4732d7b665b552abee532a8c200fa`.
- The current draft uses extension identifier `io.modelcontextprotocol/skills` and defines `skills/list`, `skills/get`, individual skill files as MCP resources, and optional `resources/directory/read`.
- A skill entry carries its frontmatter, `skill://.../SKILL.md` URI, and a complete per-file SHA-256 resource set unless the skill is dynamically generated. Hosts must verify listed digests before using content.
- The draft explicitly treats remote skill content as untrusted host-side input: no implicit code execution, no implicit `allowed-tools` permission grants, origin-scoped reads, per-origin name handling, and content-bound approval.
- The SEP currently cites the TypeScript reference work in `experimental-ext-skills#71`, prototype hosts, and a GitHub MCP Server prototype. PR #71 is closed without merge in the experimental repository; Working Group notes describe movement toward official SDK integration once the extension stabilizes.

Primary references:

- `https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2640`
- `https://github.com/modelcontextprotocol/modelcontextprotocol/blob/d29bd05222b4732d7b665b552abee532a8c200fa/docs/seps/2640-skills-extension.mdx`
- `https://github.com/modelcontextprotocol/experimental-ext-skills/pull/71`
- `https://github.com/modelcontextprotocol/experimental-ext-skills`
- `https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2941`

## Compatibility assessment

| Dimension | KIS Skills today | Draft SEP-2640 | Decision |
|---|---|---|---|
| Discovery | `list/search_skills` over one validated active snapshot | `skills/list`; listing may be empty/partial; direct URI retrieval via `skills/get` | Complement. KIS search remains local authority; MCP can expose transport discovery. |
| Progressive disclosure | `load_skill` returns entrypoint; `read_skill_file` loads bounded support files | `SKILL.md` resource plus on-demand `resources/read`; optional directory read | Compatible. Both preserve staged loading. |
| Identity | Canonical `skill_id` plus snapshot ID | Origin-scoped URI + frontmatter name | Preserve KIS identity internally; map to origin-scoped MCP URI externally. |
| Integrity/version | Entry-point SHA-256, per-file SHA-256, immutable snapshot fingerprint | Complete URI+digest set; no mandatory semantic version | Strong mapping. Digest set is transport integrity, not trust or authorship. |
| References/scripts/assets | Validated files grouped and read from active snapshot | Every file is an individually addressable resource | Compatible, but MCP-origin scripts remain data until separately approved for host execution. |
| Activation observability | `activation_id`, project ID, request correlation, observed/reported events, cost/verification samples when available | No mandatory execution/usage reporting in SEP; WG treats attribution as host/observability concern | KIS is stronger and remains authoritative. Do not regress telemetry. |
| Permissions/governance | KIS capability policy, runtime controls, Work Management, catalogue authority | Host policy controls load/execution; draft forbids implicit permission elevation | MCP transport must sit below KIS governance, never bypass it. |
| Portability | Local/project KIS surface | Cross-MCP-server transport convention | Potential value, but only after draft stability and host support justify production code. |

## Implemented compatibility slice

`scripts/skills_over_mcp_compat.py` is an **offline evidence projector**, not an MCP server.

It:

1. reads one canonical skill directory without mutation;
2. requires caller-supplied KIS identity evidence (`skill_id`, entrypoint hash, file count, optional support-file hashes);
3. fails closed if those values disagree with local bytes;
4. emits a draft SEP-shaped skill entry with complete `skill://` resources and `sha256:<hex>` digests;
5. records that no permission grant was applied.

It deliberately does not register `io.modelcontextprotocol/skills`, implement RPC methods, cache remote skills, execute scripts, mutate catalogue state, or change runtime admission.

## Real-skill proof

The canonical shared `modularity-assessment` skill was exercised through KIS and projected from the same workspace bytes:

- KIS snapshot: `c4ada48dff958cd9`
- KIS entrypoint SHA-256: `f5f251f3a4aeb310d752b5e5624c080461db761cd1b31222bd9c985c4d2f54fb`
- KIS file count: `7`
- KIS `references/output-spec.md` SHA-256: `ca776a523348c2b2342c41071a0e6bda7d100868947f8f3f9816fd6489ae3efb`
- Projection: all identity checks passed; all seven files became digest-bound resources; the KIS support-file hash matched exactly.

Generated proof remains at `.work/skills-over-mcp/modularity-assessment-projection.json` and is intentionally not repository authority.

## Behavioral evaluation interpretation

The transport experiment does not create new model behavior, so it must not manufacture trigger or output-quality deltas. Existing repository-owned trigger/output/abuse definitions remain the behavioral contract. This issue directly measures transport compatibility, identity, support-file loading, verification, and KIS operational telemetry. Any future production adapter must run the same isolated candidate-vs-baseline model evaluations required by `docs/testing/skill-evaluation-standard.md` before admission.

## Production adoption gate

Revisit production MCP Skills support only when all of the following are true:

1. SEP-2640 is accepted/stable enough that wire semantics are not a moving draft target.
2. A supported MCP SDK/host path is available for the target runtime.
3. KIS authority remains singular: remote transport cannot write or shadow the canonical workspace catalogue implicitly.
4. Remote-origin content is isolated from filesystem-skill trust and cannot grant execution/tool permissions implicitly.
5. Per-file digest verification, origin binding, collision handling, and approval invalidation are implemented and tested.
6. KIS activation/outcome telemetry is preserved or deliberately bridged; transport adoption may not erase observability.
7. Controlled trigger/output/efficiency/abuse/compatibility evaluation shows material value over the existing KIS path.

Until then, **production disposition: defer; compatibility disposition: complement via evidence-only projection.**
