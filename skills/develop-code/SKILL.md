---
name: develop-code
description: 'Use when creating, changing, fixing, refactoring, or completing production code where requirements, planning, implementation, review, verification, and closeout must stay aligned. Applies to bounded fixes through cross-component or high-risk delivery; not for read-only explanation, standalone review with no requested changes, or pure research.'
---

# Develop Code

Own the lifecycle and evidence chain:

`Understand -> classify -> specify -> plan -> implement -> review -> verify -> close`

Project instructions and canonical repository documentation override this skill. This skill owns development lifecycle semantics, classification, artifact contracts, traceability, and quality gates; it does not override repository workflow authority.

## Repository authority

Before mutating a repository, determine its declared workflow authority.

- For a KIS-managed repository, load `kis-mcp` first. Use KIS for Work Management state, governed repository/GitHub operations, bounded verification and review, integration, and worktree/repository hygiene.
- Do not bypass KIS with direct Git, GitHub, or process actions when a governed route exists. Do not create a worktree when repository policy prohibits it.
- Specialist skills may provide methods such as brainstorming, planning, TDD, debugging, or focused review, but they remain subordinate to repository instructions and KIS authority.
- If a named specialist is unavailable, apply this skill's base contract directly and record the missing specialization; runtime-specific skill availability is not itself a blocker unless repository policy makes it one.
- For repositories that do not declare KIS as authority, follow their native workflow and explicit user authorization.

## Start

1. Read applicable project instructions and authoritative docs. Inspect current state and preserve unrelated changes.
2. Discover the repository's test, build, lint, security, release, documentation, and Git conventions. Never assume a language or package manager.
3. Define the requested outcome, boundaries, exclusions, constraints, unknowns, recovery needs, and evidence expected.
4. Load [classification](./references/classification.md), state `Development level: Small|Medium|Complex` with reasons, and create lifecycle tasks scaled to that level.
5. Resolve artifact locations using [artifact contracts](./references/artifact-contracts.md). Existing repository locations win; otherwise use the defaults there.

Classify before implementation. Reclassify when scope, uncertainty, reversibility, data impact, or risk changes. Escalate immediately when any higher-level trigger appears; never downgrade only because the diff is small.

## Run The Lifecycle

Load [lifecycle](./references/lifecycle.md) and enforce every applicable gate.

### Small

- Write a compact specification and inline plan.
- Implement one bounded change.
- For a behavior change, apply `test-driven-development` only when repository/KIS authority permits or selects that specialist method.
- Review the final diff against the brief, then verify with current evidence.
- Apply `verification-before-completion` only as a specialist evidence method within the repository-authorized completion gate.

### Medium

- Create an explicit specification and implementation plan with traceable reviewable tasks.
- If requirements or design are unclear, use `brainstorming` only when repository/KIS authority permits or selects that specialist method.
- Use `writing-plans` only when repository/KIS authority permits or selects it; this skill's artifact contract remains controlling.
- For behavior changes, use `test-driven-development` only when repository/KIS authority permits or selects that specialist method.
- At review checkpoints, use `requesting-code-review` only when repository/KIS authority permits or selects it; otherwise perform the base review contract.
- Use `verification-before-completion` only as a specialist evidence method inside the repository-authorized closeout gate.

### Complex

- Create the detailed specification and plan defined by the artifact contract. Preserve unresolved decisions; do not invent product or risk decisions.
- If requirements, architecture, or trade-offs are not already approved, use `brainstorming` only when repository/KIS authority permits or selects that specialist method.
- Require human review and approval of the written specification, then use `writing-plans` only when repository/KIS authority permits or selects it.
- Require human review and approval of the written plan before implementation.
- Select an executor only through repository/KIS authority; `subagent-driven-development` and `executing-plans` are optional specialist execution methods, not lifecycle authorities.
- For behavior changes, use `test-driven-development` only when repository/KIS authority permits or selects that specialist method.
- At task and whole-change gates, use `requesting-code-review` only when repository/KIS authority permits or selects it; otherwise perform the base review contract.
- Use `verification-before-completion` only as a specialist evidence method inside the repository-authorized closeout gate.
- For branch closeout, `finishing-a-development-branch` may supply method guidance only after KIS or other repository authority selects and authorizes that path.

Do not reproduce or approximate an unavailable specialist from memory. When a specialist is selected and available, invoke it explicitly, follow it within project and KIS authority, record its result, then return to the current lifecycle gate. Otherwise execute this skill's base gate directly and disclose the missing specialization.

## Review Contract

Review the current specification, plan, documentation, implementation diff, tests, and fresh evidence together. Record findings by severity with paths and evidence. Cover:

- specification and acceptance-criteria compliance;
- plan/task compliance and traceability;
- correctness, edge cases, error handling, and regressions;
- security, privacy, secrets, authorization, and data handling;
- test relevance, red/green evidence when TDD applies, and failure-path quality;
- maintainability, readability, and repository conventions;
- unnecessary complexity and opportunities for a smaller correct design;
- scope discipline, exclusions, and unrelated changes;
- freshness and sufficiency of verification evidence;
- rollback, recovery, migration, and operational readiness when applicable.

Use the mapping in [Specialist integration](./references/superpowers-integration.md) only to select specialist methods permitted by repository/KIS authority. `security-review`, `code-review`, `simpler-code`, or `smarter-code` may contribute evidence when selected; none of them independently creates a review gate or mutation authority. Their absence never converts an unperformed base Review Contract into a pass.

Fix blocking findings, rerun affected checks, and re-review the changed scope. Do not let an earlier approval or test run cover later edits.

## Close Gate

Close only when applicable requirements are satisfied, spec and plan mappings reconcile, blocking findings are resolved, required checks pass on the current state, evidence is recorded, recovery is understood, and every remaining item is explicitly optional or out of scope. In a KIS-managed repository, KIS review/verification and Work Management projection must also reflect the current state before closeout.

Report the development level, artifacts, implemented scope, review findings or clean result, exact verification commands and outcomes, recovery/rollback, skipped checks, residual risks, and optional follow-ups. Never describe unverified behavior as complete.

