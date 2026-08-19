# Skills over MCP Compatibility Plan

## Objective

Complete issue 030 / #50 by testing the current draft MCP Skills Extension against the existing KIS Skills delivery contract and implementing only the smallest compatibility boundary justified by evidence.

## Current-state constraint

SEP-2640 is still a Draft Extensions Track proposal. The repository therefore must not replace or weaken KIS Skills authority, runtime controls, Work Management governance, or canonical workspace ownership merely to match a draft transport.

## Design

1. Use one real canonical workspace skill (`modularity-assessment`) through KIS `search_skills`, `load_skill`, `search_skill_files`, and `read_skill_file`.
2. Record the KIS snapshot ID, entrypoint SHA-256, file count, resource paths, and at least one supporting-file SHA-256.
3. Add an offline `scripts/skills_over_mcp_compat.py` projector that reads a canonical skill directory without mutation and emits a draft SEP-2640 skill entry:
   - `skill://<name>/SKILL.md` identity;
   - verbatim parsed frontmatter;
   - a complete resource list;
   - `sha256:<hex>` digest for every file.
4. Require caller-supplied KIS identity evidence (skill ID, entrypoint hash, file count) and optional resource hashes; fail closed when the filesystem projection does not match that evidence.
5. Keep the output an evidence envelope, not a production server implementation. It must not register MCP capabilities, mutate the shared catalogue, grant tools, execute scripts, or create a second lifecycle authority.
6. Test resource exposure for `SKILL.md`, references, scripts, assets, digest mismatch, identity mismatch, and linked-path rejection.
7. Run the projector against the live shared `modularity-assessment` directory and store generated evidence under `.work/skills-over-mcp/`.
8. Compare KIS and draft SEP semantics for discovery, progressive disclosure, identity/integrity, supporting files, observability, permissions/governance, and portability.
9. Record the architecture decision as `complement + defer production adoption`: preserve KIS as authority and retain the projection as an experimental compatibility/evidence adapter until SEP-2640 stabilizes.

## Evaluation boundary

Use the existing skill evaluation standard. Structural compatibility and resource loading are directly observable. Trigger precision and candidate-versus-baseline output quality are not transport properties and must not be fabricated; reuse existing repository-owned behavioral definitions and record them as unchanged/not newly observed by this transport experiment. Duration, tokens, tool calls, and retries are recorded only where the KIS telemetry surface actually exposes samples.

## Verification

Run targeted compatibility tests, the live projection, `python scripts/project_contract.py validate --repo .`, `npm run verify`, `git diff --check`, and final change review. Generated experiment output remains under `.work/` and is not committed.

## Out of scope

- #54 top-five skill evaluation work.
- #55 catalogue evaluation programme.
- #56 workspace dashboard.
- Any change to the KIS implementation or runtime repository.
- Production MCP Skills capability registration or server implementation.
- Shared lifecycle or runtime-adapter authority changes.
