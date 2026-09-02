---
name: github-delivery
description: Use this skill when verified repository work must be delivered through GitHub from a governed local change to a reviewable pull request, exact-head readiness, merge or merge-queue landing, post-merge reconciliation, and safe branch/worktree cleanup. Orchestrate live KIS Work Management and registered GitHub workflows instead of raw push or merge commands. Do not use for general GitHub triage or for repairing an existing PR when delivery/landing is not the requested outcome.
---

# GitHub Delivery

Move verified repository work through the governed GitHub lifecycle without creating a second publication or landing authority.

## Boundaries

- Follow the target repository's instructions, merge policy, source issue/change record, and Git evidence first.
- For KIS-managed work, resolve the live Work Management authority map and current claim/readiness/hold state before mutation.
- Preserve repository-governed `complexity` and additive `risk_triggers` when the target uses them.
- Use live KIS capabilities and workflows for registered publication, PR preparation, exact-head checks, merge/queue execution, reconciliation, branch cleanup, and worktree cleanup.
- Never substitute raw `git push`, `gh pr create`, `gh api`, custom merge/watcher scripts, force push, admin bypass, or direct default-branch mutation for an available governed path.
- A workflow recommendation or capability match is routing evidence, not authorization. Respect each operation's live approval, idempotency, readiness, and effect contract.

## 1. Establish the delivery contract

Resolve:

1. project and repository identity;
2. authoritative source issue/change record and current operational intent;
3. exact local change/commit that is intended for delivery;
4. target default branch and repository merge policy;
5. required verification, review, documentation impact, complexity, and risk triggers;
6. any active hold, defer, dependency, or conflicting claim.

Do not manufacture missing Work Management fields. If the live Project/schema cannot represent required source metadata, keep source truth authoritative and report the projection limitation.

## 2. Prepare verified local work

For a new implementation slice, prefer the live KIS isolated-development workflow when available. It should refresh the registered default tracking ref before creating governed isolation, preserve claims, implement within scope, run required checks, and produce reviewable commits.

When the implementation already exists, inspect the exact intended commit rather than inferring it from a clean working tree. Run the repository's governed verification/review path for that exact change before publication.

Do not absorb unrelated dirty work or silently widen the change boundary.

## 3. Prepare a reviewable pull request

Prefer the live KIS `prepare-reviewable-pull-request` workflow when available. It is responsible for verifying the immutable source commit, reconciling its exact tree onto current remote-default truth when permitted, publishing the registered review head, and creating the exact open reviewable PR.

Record the resulting repository, PR, base, head SHA, source commit, and verification evidence. Do not claim publication or PR creation from an intended action; verify the provider result.

If reconciliation reports a real semantic conflict, route the conflict to `github-pr-maintenance` / `merge-conflict-resolution` rather than force a new base or rewrite published history.

## 4. Maintain readiness at the current head

If review feedback, requested changes, exact-head CI failure, base drift, or conflicts prevent readiness, invoke `github-pr-maintenance` for the existing PR.

Any changed PR head invalidates prior head-specific CI, review, readiness, or landing evidence where the repository/KIS policy requires freshness. Re-resolve the exact head after every repair/publication cycle.

Do not duplicate the repair workflow here.

## 5. Select the governed landing path

Determine landing strategy from target-repository authority and current KIS capability evidence:

- use the managed pull-request completion workflow when repository policy permits the ordinary registered merge path;
- use the managed/speculative merge-queue workflow when repository policy, concurrency, or an explicit operator decision requires queue landing;
- if the required strategy is not supported by the current KIS operation, stop with a capability/policy mismatch rather than choosing another merge method.

Before landing, require the current Work Management readiness gate when applicable and provider-native GitHub Actions evidence for the exact approved PR head. Queue workflows additionally bind evidence to the exact cumulative candidate SHA and generation/base contract.

Never reuse approval or readiness evidence from an older head or queue generation.

## 6. Observe landing and reconcile source truth

Do not treat merge enrollment, queue entry, or a submitted mutation as completion. Verify GitHub observes the exact intended work as landed according to the selected workflow.

After landing:

1. refresh the registered default-branch tracking ref to exact GitHub truth using the bounded KIS operation;
2. record required post-merge documentation reconciliation in Work Management/source records;
3. keep work non-final while `post_merge_complete`, required documentation, approval, or an operator hold remains outstanding;
4. only after verified merge and reconciliation, use the governed branch cleanup and worktree cleanup path.

Cleanup must be non-forced, preserve unrelated work, and fail closed if the branch/worktree cannot be proven eligible.

## 7. Completion state

Work is Done only when all applicable evidence exists:

- exact intended source change/commit was verified;
- an exact reviewable PR existed at the current approved head;
- required review and exact-head CI gates passed;
- the repository-approved merge or queue path landed the intended head/candidate;
- GitHub and registered default tracking agree on landed truth;
- required documentation reconciliation is complete;
- source issue/Work Management lifecycle is reconciled without overriding repository evidence;
- eligible remote branch/worktree cleanup is verified, or a concrete cleanup blocker is recorded.

Report the exact PR/head/landing evidence, verification performed, Work Management state, documentation status, cleanup result, and any residual blocker. Never describe a queued or requested landing as merged before the governed workflow observes it.