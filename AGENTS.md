# AGENTS.md

## Authority

`AGENTS.md` defines **how work is performed** in this repository, not **how adopted skills or supporting systems are implemented**.

**Rule:** If an agent needs the information before making its first edit, it belongs here. Otherwise, place it in the appropriate authoritative document and reference it.

## Purpose and Scope

This repository evaluates, adapts, validates, and maintains selected skills sourced from the shared Projects workspace catalogue, the Codex skills library, and other reference corpora. ChatGPT is the initial delivery target.

The shared canonical workspace catalogue is `C:\Projects\.agents\skills`. It is an operational catalogue, not repository authority: catalogue presence does not itself grant repository runtime admission, mutation authority, or enablement. The Codex library at `C:\Users\piete\.codex\skills` is an upstream candidate/source surface, not the canonical Projects workspace catalogue.

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

## Writing Style

Apply `writing-style` to all LLM-written output in this project, including plans, board or issue text, comments, documentation, summaries, reports, status updates, and closeout notes. For detailed Google style questions, start at `C:\Projects\References\google-developer-style-guide\000-index.md` and read only the relevant page or pages; project-specific authority still wins.

## Source and Reference Authority

- Treat `references/` as source evidence, comparative material, and implementation examples—not as repository policy or accepted project state.
- Treat the shared Projects workspace catalogue as an external operational catalogue. Its contents are discoverable skills, not automatically accepted repository state.
- Treat the Codex skills library, imported skills, plugins, commands, agents, hooks, scripts, workflows, templates, and manifests as adoption candidates only unless a repository-owned decision says otherwise.
- Route new or refreshed web-sourced material, including GitHub, through import-isolate and accept only finalized downstream handoffs; do not duplicate acquisition, isolation, scanning, cleanup, semantic-review, or neutralization work in this repository.
- Do not copy source behavior, metadata, structure, or tooling assumptions into adopted artifacts without assessing scope, provenance, license, compatibility, security, and validation requirements.
- Do not silently reconcile conflicting source guidance. Preserve the conflict, identify the alternatives, and record the repository-owned decision in the appropriate authoritative document.
- Distinguish portable Agent Skills requirements from client-specific extensions. Claude-specific fields, tools, invocation models, subagents, background processes, plugin data paths, viewers, publishing mechanisms, and permission semantics are non-portable until explicitly mapped to available ChatGPT capabilities.
- When summarizing or deriving work from source material, preserve what the sources support. Label repository decisions, adaptations, and inferences separately.
- Once material is deliberately adopted into an authoritative repository artifact, that artifact—not the source copy—governs future work.

## Repository Constraints

- Work only inside `C:\Projects\ChatGPT-skill` or its registered isolated worktrees under `C:\Projects\.kis\worktrees\chatgpt-skill`, except for controlled post-merge publication to the canonical workspace catalogue defined in [`docs/operations/workspace-skill-catalogue.md`](docs/operations/workspace-skill-catalogue.md).
- Use `.work/` for temporary, generated, exploratory, or otherwise unplaceable artifacts.
- Treat `C:\Projects\.agents\skills` and other external skill libraries as read-only except for the repository-owned post-merge publication path. Publish only accepted `origin/main` skill packages through `scripts/sync_workspace_catalogue.py`; never edit catalogue skills manually or publish branch/worktree state. Preserve evidence and update the source work record for every catalogue mutation.
- Repo at `https://github.com/NielPieterse0/chatgpt-skill.git`
- Preserve unrelated working-tree changes.
- Change only files required by the assigned scope.
- Do not commit, push, create branches, mutate remotes, or publish artifacts unless explicitly requested.
- Do not store credentials, secrets, tokens, personal data, or machine-specific sensitive values in the repository.
- Prefer authoritative project documents over duplicated guidance in `AGENTS.md` or `README.md`.

## Work Management Control Plane

- Use the currently commissioned KIS Work Management capabilities and workflows as the operational authority for tracked-work lifecycle state and capability routing. Do not depend on or infer authority from a particular KIS implementation repository or local checkout path.
- The repository-owned binding is [`settings/projects/chatgpt-skill.json`](settings/projects/chatgpt-skill.json), which records the required KIS capability families and operations, the GitHub user Project `NielPieterse0/1`, and the exact repository source-scope rule.
- Preserve GitHub issue-backed source identity. GitHub issues are authoritative for source identity and source open/closed status. KIS Work Management is authoritative for operational lifecycle state, ownership, priority, effort, dependencies, and eligibility; the shared GitHub Project projects that KIS state against the issue identity rather than replacing either authority.
- Before changing a Project record, require an exact source repository match to `NielPieterse0/chatgpt-skill`. Shared-Project items sourced from other repositories are out of scope.
- When a repository issue is created or becomes actionable, reconcile it into the Project immediately; an issue that is absent from the Project is not ready for execution.
- Before claiming work, reconcile the complete set of open `NielPieterse0/chatgpt-skill` issues against the Project, require every open issue to be represented under the current KIS metadata contract, then re-read the selected Project item and source issue. If another agent already owns the work or projection drift remains, do not claim it.
- Before closeout, repeat the complete source-to-Project reconciliation. Closed source issues remain in the Project as history, and work may reach `Done` only after applicable implementation, verification, review/merge, post-merge documentation, and Project reconciliation requirements pass. Treat missing items, stale dependencies, or required metadata gaps as blocking drift rather than silently continuing.
- Implement changes in clean issue worktrees under `C:\Projects\.kis\worktrees\chatgpt-skill`; never modify an unrelated dirty canonical checkout to make progress.
- Validate the repository-owned Work Management contract with `python scripts/project_contract.py validate --repo .` and use KIS capability discovery for the operations recorded there.

## Skill Security Gate

- Treat [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md) as the authority for skill import, adoption, discovery, activation, disablement, and rollback.
- Runtime discovery is limited to direct children matching `skills/*/SKILL.md`. Never discover, activate, import from, or execute content below `references/` or `.work/`.
- Every adopted repository skill requires a valid `adoption-manifest.json`, immutable source revision, reviewed license, content hash, permitted capability tier, bounded filesystem scope, human approval, and verified rollback.
- Reject `allowed-tools`, lifecycle hooks, remote MCP, runtime dependency installation, credentials, network access, external mutation, Git publication, deployment, and deletion under the P0 policy.
- Keep `config/runtime-control.json` disabled until Git-aware repository validation passes. Disable it immediately when provenance, validation, or runtime integrity is uncertain.
- Run `npm run verify` and `python scripts/skill_security.py validate --repo .` before treating any skill-security change as complete.

## Required Workflow

### Mandatory skill-development method

For any work that creates or materially revises an Agent Skill, load and follow the active catalogue `create-skill` workflow before the first skill edit. Also load `writing-skills` when behavioral instructions are being authored or materially changed so the revision is pressure-tested with a RED → GREEN → REFACTOR discipline.

For any work that evaluates an existing skill, load and follow `evaluate-skill`. When evaluation findings drive a revision, load and follow `improve-skill` before editing, while preserving the baseline and held-out evaluation set. Repository-owned package, security, evaluation, runtime, and lifecycle standards remain authoritative over these reusable methods.

Record which skill-development workflows were loaded in the change or evaluation evidence. Do not mass-normalize multiple skills from a shared template without independent per-skill source review, activation-boundary review, and technical-depth review. Human-review gates remain human-only; agent grading or skill workflows cannot substitute for named human evidence.

1. Read this file and any nested `AGENTS.md` files that govern the target path.
2. Inspect the live repository state before editing.
3. For work that creates, changes, evaluates, packages, enables, suspends, removes, or changes shared-catalogue status for a skill, read [`docs/research/skill-adoption-research-synthesis.md`](docs/research/skill-adoption-research-synthesis.md) and the linked authoritative owner documents before the first edit.
4. Identify the authoritative documents, source skill material, dependencies, constraints, provenance, acceptance criteria, selected runtime target, and whether the action affects repository runtime state, shared workspace catalogue state, or both.
5. Separate source-derived requirements from repository-owned decisions and adaptations; keep host-specific behavior within the responsible adapter boundary.
6. For non-trivial changes, establish or update the appropriate specification, decision record, or implementation plan before modifying implementation artifacts.
7. Make the smallest coherent change that satisfies the requested scope.
8. Validate the changed artifacts using repository-defined commands and targeted checks.
9. Review the final diff for unintended changes, duplicated authority, sensitive content, stale references, unsupported source claims, and unrecorded portability assumptions.
10. After an accepted merge that adds or changes `skills/*`, refresh `origin/main`, publish the affected merged skill packages with `scripts/sync_workspace_catalogue.py`, and verify workspace/KIS discovery before marking the work complete. Follow [`docs/operations/workspace-skill-catalogue.md`](docs/operations/workspace-skill-catalogue.md); a merge without successful catalogue publication is incomplete.

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
- when accepted work adds or changes a skill, the merged package is synchronized to the canonical workspace catalogue and discoverability is verified;
- remaining risks, assumptions, skipped checks, and follow-up work are reported.

Stop and request direction before proceeding when the task requires destructive action not explicitly authorized, expands beyond the stated scope, conflicts with a higher authority, or depends on missing information that would materially change the implementation.

## Authoritative References

- [`docs/research/skill-adoption-research-synthesis.md`](docs/research/skill-adoption-research-synthesis.md): accepted cross-source conclusions, requirements matrix, unresolved assumptions, and research-output status.
- [`docs/standards/skill-authority-lifecycle.md`](docs/standards/skill-authority-lifecycle.md): lifecycle composition and handoffs across create, evaluate, improve, admission, maintenance, suspension, and rollback.
- [`docs/standards/skill-package-standard.md`](docs/standards/skill-package-standard.md): canonical repository skill contents, progressive disclosure, resources, target overlays, and packaging exclusions.
- [`docs/testing/skill-evaluation-standard.md`](docs/testing/skill-evaluation-standard.md): trigger, output, efficiency, abuse, compatibility, human-review, and release-evidence requirements.
- [`docs/plans/skill-adoption-implementation-backlog.md`](docs/plans/skill-adoption-implementation-backlog.md): dependency-ordered active and historical implementation work and stop criteria.
- [`docs/operations/github-repository-hygiene.md`](docs/operations/github-repository-hygiene.md): accepted GitHub repository settings, main-branch controls, automation, and closeout requirements.
- [`docs/operations/workspace-skill-catalogue.md`](docs/operations/workspace-skill-catalogue.md): controlled post-merge publication from accepted repository skills into the canonical workspace catalogue and its discovery gate.
- [`SECURITY.md`](SECURITY.md): vulnerability reporting and immediate containment.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): contribution and pull-request workflow.
- [`README.md`](README.md): project overview, quick start, repository navigation, and common workflows.
- [`docs/architecture/skill-runtime-adapters.md`](docs/architecture/skill-runtime-adapters.md): authoritative portable-core and runtime-adapter boundary, including the ChatGPT-first and future Codex target strategy.
- [`docs/architecture/import-isolate-handoff.md`](docs/architecture/import-isolate-handoff.md): authoritative responsibility boundary for externally acquired source material and finalized import-isolate handoffs.
- [`docs/architecture/plugin-portfolio-methodology.md`](docs/architecture/plugin-portfolio-methodology.md): authoritative plugin portfolio boundaries, lifecycle states, intake/update methodology, pilot evidence rules, and dashboard requirements.
- Nested `AGENTS.md` files: path-specific working rules, when present.
- Documents under `docs/`: product, other architecture, decision, planning, coding, testing, and operational knowledge, when present.
- Adopted skill directories: skill-specific implementation and usage documentation.

External, non-authoritative inputs:

- Shared Projects workspace catalogue: `C:\Projects\.agents\skills`
- Codex skills library: `C:\Users\piete\.codex\skills`
- Codex skills index: `C:\Users\piete\.codex\skills\skills-index.json`
- Repository reference corpus: [`references/`](references/)

These external sources do not define accepted repository state until their relevant content is deliberately adopted into an authoritative repository artifact.