# Develop Workflow Skills Admission Evidence

## Decision

`develop-code` and `develop-docs` are accepted as canonical Tier 2 project-content workflow skills. Runtime enablement remains separate and the repository kill switch stays disabled.

## Source and integrity

- Source repository: `NielPieterse0/kis-mcp`.
- Immutable source revision: `5ab2aa1e71852363b0a872e1d9a44f3c70298a42`.
- Current source HEAD checked on 2026-08-13: `5f9c60c1bdf363207cddd4a5fa24cc4d006b3e6f`.
- No source-package changes were found after the immutable revision.
- `develop-code` content hash: `07135ba9e509076f002cd550c8e50ee2251e598979425db93178aa44e471a871`.
- `develop-docs` content hash: `6bdd16158102e3339ade10e36be4ca065dfd866da4888b8f67e9f8242cabc1ca`.
- License record: `LicenseRef-Repository-Owned`.

## Existing candidate evidence

On 2026-07-31 both candidates were pressure-tested in fresh read-only agent contexts against no-skill baselines. The preserved local evidence is normalized under `.work/evals/<skill>/iteration-1/` for this change.

`develop-code` GREEN evidence covered production-auth risk classification, unresolved cross-component product decisions, stale verification, a bounded bug fix, a medium API/UI change, and late risk escalation. `develop-docs` GREEN evidence covered bounded README correction, multi-guide terminology work, high-risk runbook control changes, machine-friendly policy writing, stale checks, and generated-document scope escalation.

## Tracked evaluation definitions

Each skill now has tracked trigger, output, and abuse definitions under `tests/skills/<skill>/`.

Trigger coverage per skill: 6 positive cases, 6 realistic near-misses, 2 competing-workflow conflicts, and 2 prompt-injection cases. Output coverage contains three candidate-vs-baseline cases with critical assertions. Abuse definitions cover project-scope boundaries, untrusted repository instructions, redirected paths, sensitive input, undeclared dependencies, authority expansion, retry safety, and stale evidence.

Direct target activation observability is not available in this repository workflow, so trigger precision is not claimed. The tracked cases are the release definitions for future adapter/runtime execution.

## Admission checks

The repository validator checks frontmatter, manifest structure, capability tier, declared filesystem scope, content hashes, package-tree hazards, Git identity, and the disabled runtime state. Tier 2 policy tests additionally cover repository-root project scope, empty-scope rejection, and direct repository-control-metadata scope rejection.

The `improve-skill` CLI dependency (`plugin-eval`) was not installed in the execution environment. No plugin-eval score is claimed. Its relevant compactness and trigger-boundary concerns were checked through the repository package rules, tracked trigger cases, and final review instead.

## Human review

Repository-owner approval for Tier 2 repository-root project-content scope was given on 2026-08-13. Repository verification and final diff review passed on 2026-08-13. GitHub closeout evidence for the exact delivered revision remains required.
