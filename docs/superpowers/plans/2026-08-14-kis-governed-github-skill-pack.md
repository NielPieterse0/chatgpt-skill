# KIS-Governed GitHub Skill Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace overlapping GitHub workflow skills in the canonical Projects catalogue with three KIS-governed skills and safely retire superseded packages.

**Architecture:** Repository source records and Git/GitHub evidence remain authoritative; KIS supplies live Work Management/provider/workflow execution; skills supply stable intent, reasoning, sequencing, and handoffs. New skills are single-file portable packages so KIS can publish them atomically with the current Skills API.

**Tech Stack:** Agent Skills Markdown, KIS Skills catalogue, KIS GitHub MCP/provider workflows, GitHub Issues/PRs, repository Markdown evaluation evidence.

## Global Constraints

- Preserve the dirty historical checkout; use the isolated Change 021 worktree for repository artifacts.
- Do not admit these KIS-operational skills into repository `skills/` under the current P0 security policy.
- Do not duplicate Change 020 portability remediation.
- Discover live KIS authority/workflow/provider capability before relying on mutable runtime semantics.
- Use recoverable catalogue mutation and atomic refresh; no raw deletion.
- Never replace KIS registered publication/landing with `git push`, `gh`, unrestricted GraphQL, admin/force/bypass, or custom landing scripts.

---

### Task 1: Establish repository authority and baseline evidence

**Files:**
- Create: `docs/superpowers/specs/2026-08-14-kis-governed-github-skill-pack-design.md`
- Create: `docs/superpowers/plans/2026-08-14-kis-governed-github-skill-pack.md`

**Interfaces:**
- Consumes: Change 019 evaluation, issues #31–#36, live KIS backlog/capabilities.
- Produces: approved architecture and rollout contract for all later tasks.

- [x] Record the approved authority split, skill boundaries, KIS in-flight dependencies, rollout order, evaluation contract, rollback, and P0 admission boundary.
- [x] Run `git diff --check` and Markdown/path review in the isolated worktree.
- [x] Commit the source-of-truth design/plan after validation.

### Task 2: Capture pre-change catalogue evidence

**Files:**
- Generated evidence only under `.work/evals/github-skill-pack/` when repository-local evidence is required.

**Interfaces:**
- Consumes: current active KIS skill snapshot.
- Produces: current hashes/content identity for `github` and all superseded specialists.

- [x] Run KIS structural evaluation for `github`, `gh-address-comments`, `gh-review-comment-triage`, `gh-fix-ci`, `yeet`, `take-pr-to-completion`, `commit-workspace-changes`, and retained generic dependencies.
- [x] Search the complete catalogue for references to superseded skill names.
- [x] Record baseline limitations without claiming unavailable activation metrics.

### Task 3: Create `github-pr-maintenance`

**Files:**
- Create in canonical catalogue: `github-pr-maintenance/SKILL.md`

**Interfaces:**
- Consumes: live provider thread/PR/Actions evidence, `code-work`, `merge-conflict-resolution`, KIS verification workflows.
- Produces: exact-head PR repair/readiness evidence; no landing mutation.

- [x] Define trigger cases and near-miss/conflict/injection boundaries for the description.
- [x] Create a single-file skill with thread triage, exact-head CI classification, code/conflict handoffs, verification, and authorized reply behavior.
- [x] Explicitly fail closed when review-thread resolution is requested but no approved live operation exists.
- [x] Refresh the catalogue atomically, load the new skill, and run structural evaluation.
- [x] Review representative review-feedback, CI-failure, and missing-capability contracts; repeated isolated model execution remains unavailable and is recorded in the evaluation report.

### Task 4: Create `github-delivery`

**Files:**
- Create in canonical catalogue: `github-delivery/SKILL.md`

**Interfaces:**
- Consumes: live Work Management authority, KIS registered publication/PR/merge/queue/cleanup workflows, `github-pr-maintenance`.
- Produces: governed repository delivery through post-merge reconciliation and cleanup.

- [x] Define trigger cases and near-miss/conflict/injection boundaries for the description.
- [x] Create a single-file orchestration skill preserving exact-head evidence invalidation and complexity/risk-trigger governance.
- [x] Route repair loops to `github-pr-maintenance` and select ordinary managed merge versus queue from repository policy/live KIS capability.
- [x] Prevent Done before required verification/documentation/hold completion.
- [x] Refresh, load, structurally evaluate, and review ordinary merge, merge-queue, stale-head, and blocked-capability contracts; repeated isolated model execution remains unavailable and is recorded in the evaluation report.

### Task 5: Rewrite the `github` umbrella

**Files:**
- Modify in canonical catalogue: `github/SKILL.md`

**Interfaces:**
- Consumes: verified `github-pr-maintenance`, verified `github-delivery`, bounded GitHub provider reads/writes.
- Produces: stable triage/router entrypoint without duplicate implementation authority.

- [x] Define positive/near-miss/conflict/injection boundary cases against the two new specialists and generic code skills.
- [x] Replace connector/`gh` hybrid assumptions with project-neutral KIS-aware routing and live capability discovery.
- [x] Keep general repository/issue/PR triage in the umbrella; immediately route maintenance and delivery outcomes.
- [x] Refresh, load, structurally evaluate, and review representative triage/routing contracts; repeated isolated model execution remains unavailable and is recorded in the evaluation report.

### Task 6: Reconcile dependent generic commit workflow and retire old specialists

**Files:**
- Conditionally modify in canonical catalogue: `commit-workspace-changes/SKILL.md`
- Withdraw recoverably after replacement: `gh-address-comments`, `gh-review-comment-triage`, `gh-fix-ci`, `yeet`, `take-pr-to-completion`.

**Interfaces:**
- Consumes: complete catalogue reference search and verified three-skill pack.
- Produces: no dangling old workflow routes and a recoverable consolidated catalogue.

- [x] Search again for every superseded skill name after new-pack rollout.
- [x] Reconcile `commit-workspace-changes`: it is already absent from the canonical shared root, so no stale handoff mutation is required in Change 024.
- [x] Reconcile retirement without destructive mutation: all superseded package directories were already absent from the canonical shared root, so no quarantine/delete action was necessary.
- [x] Refresh the catalogue atomically and prove superseded packages are absent from the active Skills snapshot while retained generic specialists remain present in the canonical root.
- [x] Re-verify capability discovery after runtime refresh: the stale removed-skill contribution no longer reproduces on current `kis-op`; keep kis-mcp #183 open for regression coverage and durable root-cause closeout without blocking Change 024 package retirement.

### Task 7: Evaluate, document, and deliver repository source records

**Files:**
- Create/update evaluation evidence outside runtime packages.
- Update only repository-owned authoritative summary/backlog artifacts if the implemented result changes them.

**Interfaces:**
- Consumes: final active catalogue, KIS structural evidence, trigger/output/abuse review, GitHub source issues.
- Produces: reviewable Change 019 completion evidence and repository PR.

- [x] Review at least 6 positive, 6 near-miss, 2 conflict, and 2 injection cases per new/revised skill; activation precision is explicitly unmeasured because direct activation observability is unavailable.
- [x] Review at least three representative workflow/output cases per skill, including missing-capability and stale-head boundaries; no repeated isolated model benchmark is claimed.
- [x] Run catalogue refresh/evaluation and search for dangling references.
- [x] Run repository `git diff --check`, focused eval tests, and the full repository `npm run verify` gate.
- [ ] Update issues #31/#33–#36 with exact verification, blockers, residual limitations, and lifecycle status.
- [ ] Commit the isolated repository change, prepare a reviewable PR through KIS, require exact-head CI, and close out through the repository's governed merge path.
