# AGENTS.md

## Authority

`AGENTS.md` defines **how work is performed** in this repository, not **how adopted skills or supporting systems are implemented**.

**Rule:** If an agent needs the information before making its first edit, it belongs here. Otherwise, place it in the appropriate authoritative document and reference it.

## Purpose and Scope

This repository evaluates, adapts, validates, and maintains selected skills sourced from the Codex global skills library and other reference corpora. ChatGPT is the initial delivery target.

Keep the adoption methodology and portable skill model host-independent. Isolate ChatGPT-specific behavior behind runtime adapters so a future Codex adapter can use the same canonical adopted skills, admission decisions, provenance, security controls, and evaluation model. Follow [`docs/architecture/skill-runtime-adapters.md`](docs/architecture/skill-runtime-adapters.md) for the authoritative boundary.

The live repository is the sole source of truth for accepted project state. External skill libraries, imported reference corpora, indexes, prior conversations, and notes are inputs only until their relevant content is deliberately adopted into authoritative repository artifacts.

## Authority Order

Apply instructions in this order:

1. Explicit human instruction for the current task.
2. This root `AGENTS.md`.
3. A nested `AGENTS.md` governing the edited path.
4. Authoritative repository documents explicitly referenced by the applicable `AGENTS.md`.
5. Adopted repository implementation and its colocated documentation.
6. Other repository documentation and code comments.
7. Source material under `references/` and external libraries.

When authorities conflict, follow the highest applicable authority and report the conflict.

## Source and Reference Authority

- Treat `references/` as source evidence, comparative material, and implementation examples—not as repository policy or accepted project state.
- Treat imported skills, plugins, commands, agents, hooks, scripts, workflows, templates, and manifests as adoption candidates only.
- Do not copy source behavior, metadata, structure, or tooling assumptions into adopted artifacts without assessing scope, provenance, license, compatibility, security, and validation requirements.
- Do not silently reconcile conflicting source guidance. Preserve the conflict, identify the alternatives, and record the repository-owned decision in the appropriate authoritative document.
- Distinguish portable Agent Skills requirements from client-specific extensions. Claude-specific fields, tools, invocation models, subagents, background processes, plugin data paths, viewers, publishing mechanisms, and permission semantics are non-portable until explicitly mapped to available ChatGPT capabilities.
- When summarizing or deriving work from source material, preserve what the sources support. Label repository decisions, adaptations, and inferences separately.
- Once material is deliberately adopted into an authoritative repository artifact, that artifact—not the source copy—governs future work.

## Repository Constraints

- Work only inside `C:\Projects\ChatGPT-skill-adoption`.
- Use `.work/` for temporary, generated, exploratory, or otherwise unplaceable artifacts.
- Do not write to or modify the external Codex skills library.
- Repo at `https://github.com/NielPieterse0/chatgpt-skill-adoption.git`
- Preserve unrelated working-tree changes.
- Change only files required by the assigned scope.
- Do not commit, push, create branches, mutate remotes, or publish artifacts unless explicitly requested.
- Do not store credentials, secrets, tokens, personal data, or machine-specific sensitive values in the repository.
- Prefer authoritative project documents over duplicated guidance in `AGENTS.md` or `README.md`.

## Skill Security Gate

- Treat [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md) as the authority for skill import, adoption, discovery, activation, disablement, and rollback.
- Runtime discovery is limited to direct children matching `skills/*/SKILL.md`. Never discover, activate, import from, or execute content below `references/` or `.work/`.
- Every adopted skill requires a valid `adoption-manifest.json`, immutable source revision, reviewed license, content hash, permitted capability tier, bounded filesystem scope, human approval, and verified rollback.
- Reject `allowed-tools`, lifecycle hooks, remote MCP, runtime dependency installation, credentials, network access, external mutation, Git publication, deployment, and deletion under the P0 policy.
- Keep `config/runtime-control.json` disabled until Git-aware repository validation passes. Disable it immediately when provenance, validation, or runtime integrity is uncertain.
- Run `npm run verify` and `python scripts/skill_security.py validate --repo .` before treating any skill-security change as complete.

## Required Workflow

1. Read this file and any nested `AGENTS.md` files that govern the target path.
2. Inspect the live repository state before editing.
3. Identify the authoritative documents, source skill material, dependencies, constraints, provenance, acceptance criteria, and selected runtime target relevant to the task.
4. Separate source-derived requirements from repository-owned decisions and adaptations; keep host-specific behavior within the responsible adapter boundary.
5. For non-trivial changes, establish or update the appropriate specification, decision record, or implementation plan before modifying implementation artifacts.
6. Make the smallest coherent change that satisfies the requested scope.
7. Validate the changed artifacts using repository-defined commands and targeted checks.
8. Review the final diff for unintended changes, duplicated authority, sensitive content, stale references, unsupported source claims, and unrecorded portability assumptions.

## Validation

Use the validation commands documented by the relevant authoritative repository files. Run the narrowest applicable checks first, then the repository-wide checks required for completion.

For documentation-only changes, at minimum verify:

- Markdown structure and internal consistency;
- referenced paths and links exist or are explicitly marked as planned;
- source-derived statements are supported by the cited or inspected source material;
- repository decisions and adaptations are distinguishable from imported guidance;
- no product, architecture, coding, testing, or operational guidance is duplicated from an authoritative document;
- `git diff --check` passes when Git metadata is available.

Do not claim a check passed unless it was run successfully. Report unavailable or skipped checks explicitly.

## Completion and Stop Criteria

Stop when all of the following are true:

- the requested scope is complete;
- applicable validation has passed;
- authoritative documentation is updated without unnecessary duplication;
- source authority and repository decisions are unambiguous;
- the final diff contains no unrelated changes;
- remaining risks, assumptions, skipped checks, and follow-up work are reported.

Stop and request direction before proceeding when the task requires destructive action, expands beyond the stated scope, conflicts with a higher authority, or depends on missing information that would materially change the implementation.

## Authoritative References
- [`docs/operations/github-repository-hygiene.md`](docs/operations/github-repository-hygiene.md): accepted GitHub repository settings, main-branch controls, automation, and closeout requirements.
- [`SECURITY.md`](SECURITY.md): vulnerability reporting and immediate containment.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): contribution and pull-request workflow.

- [`README.md`](README.md): project overview, quick start, repository navigation, and common workflows.
- [`docs/architecture/skill-runtime-adapters.md`](docs/architecture/skill-runtime-adapters.md): authoritative portable-core and runtime-adapter boundary, including the ChatGPT-first and future Codex target strategy.
- Nested `AGENTS.md` files: path-specific working rules, when present.
- Documents under `docs/`: product, other architecture, decisions, plans, standards, testing, and operational knowledge, when present.
- Adopted skill directories: skill-specific implementation and usage documentation.

Non-authoritative source inputs:

- Repository reference corpus: [`references/`](references/)
- Codex skills library: `C:\Users\piete\.codex\skills`
- Codex skills index: `C:\Users\piete\.codex\skills\skills-index.json`

These sources are read-only inputs. They do not define accepted repository state until their relevant content is deliberately adopted into an authoritative repository artifact.
