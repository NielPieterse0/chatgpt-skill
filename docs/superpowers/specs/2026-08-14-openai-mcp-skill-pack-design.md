# OpenAI-Optimized MCP Skill Pack Design

## Status

Issue #47 defines the shared-catalogue MCP pack boundary. The target is the operational Projects catalogue at `C:\Projects\.agents\skills`; these packages are not repository-runtime admissions.

## Decision

Keep four intent-separated skills:

| Skill | Owned outcome |
|---|---|
| `mcp-development` | Protocol-centric architecture, interoperability, modernization, version/transport/auth review, and portable-vs-host boundary decisions |
| `openai-mcp-server` | Straightforward MCP server construction or material server changes for ChatGPT, Codex, or an OpenAI plugin |
| `openai-mcp-app-ui` | Interactive MCP Apps UI for ChatGPT/OpenAI, with portable MCP Apps semantics first and OpenAI extensions only when needed |
| `mcpb-local-packaging` | Anthropic MCPB packaging and validation for local stdio distribution |

The superseded identities `build-mcp-server`, `build-mcp-app`, and `build-mcpb` must not remain discoverable.

## Routing rules

1. Choose by the user's dominant outcome, not by the word `MCP` alone.
2. Prefer the narrow OpenAI server skill when implementation is the task and protocol architecture is already settled.
3. Prefer the UI specialist only when interactive UI materially improves the outcome; plain structured/text output stays with the server skill.
4. Prefer MCPB only when local Anthropic packaging/distribution is explicitly required.
5. Use `mcp-development` when cross-host correctness, protocol interpretation, or architecture/review is dominant.
6. Compose specialists only when the task genuinely crosses their boundaries; do not duplicate their workflows.

## Source and portability boundary

- Core MCP requirements remain standards-first and are not inferred from OpenAI product behavior.
- OpenAI-specific deployment, developer-mode, plugin, Apps SDK, UI, and host-extension behavior is version-sensitive and must be verified against current official OpenAI documentation when used.
- MCP Apps is treated as an MCP extension with a portable shared contract; OpenAI-only behavior remains an explicit host extension.
- MCPB is a host/package distribution concern, not an MCP transport, authorization model, or OpenAI deployment requirement.
- Live web verification may confirm target behavior, but externally acquired source material is not imported into repository authority outside the `import-isolate` boundary.

## Evaluation contract

Each skill requires repository-owned definitions with at least:

- 6 positive trigger cases;
- 6 near-miss negative cases;
- 2 adjacent-skill conflict cases;
- 2 prompt-injection cases;
- 3 representative output/workflow cases;
- 8 abuse-boundary cases.

Static definitions prove boundary coverage, not measured model activation. Quantitative trigger precision/recall remains unclaimed unless a runtime exposes isolated activation observations.

## Completion criteria

Issue #47 is ready for governed closeout only when:

- the four active identities and descriptions are structurally valid and distinct;
- old `build-mcp-*` identities are absent from the active catalogue;
- cross-skill references use the current identities;
- current OpenAI product behavior and MCP Apps portability assumptions have been checked against primary sources;
- regression definitions satisfy the repository evaluation minimums;
- repository-wide verification passes;
- the exact change is reviewed, merged, and post-merge tracking is reconciled before Project `Done`.
