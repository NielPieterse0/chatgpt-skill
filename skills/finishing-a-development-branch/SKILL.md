---
name: finishing-a-development-branch
description: Use when implementation is complete and verified, and a development branch needs a deliberate integration, retention, or cleanup decision.
license: MIT
---

# Finishing a Development Branch

Separate "the work is verified" from "the work should now be integrated." Preserve the deliberate closeout decision while deferring mutation authority to the repository's delivery workflow.

## 1. Verify before choosing an outcome

Run the required checks on the exact current head and read their results. If required verification fails, return to implementation; do not present the branch as ready.

Record the exact current head, current workspace or detached state, intended base, known findings, and whether the branch contains uncommitted work.

## 2. Resolve the environment and authority

Determine the base and permitted delivery paths from repository evidence rather than branch-name guesses.

For a KIS-managed repository, load `kis-mcp` and use the live KIS delivery/merge/worktree workflow. KIS and repository policy own publication, pull requests, merging, branch mutation, and cleanup eligibility.

For a repository without KIS authority, follow its native documented workflow and explicit user authorization.

## 3. Make the outcome explicit

Present only outcomes the repository actually permits, typically:

- integrate through the governed review/landing path;
- retain the verified branch/workspace for later work;
- abandon the change only when the user explicitly chooses that outcome and the repository provides a recoverable safe path.Do not invent an option that bypasses required review, exact-head checks, queue policy, or approval.

## 4. Execute through the owning workflow

Hand the selected outcome to `github-delivery` or the repository-authorized equivalent. Re-read provider evidence after any mutation. A request, queue entry, or intended merge is not proof of landing.

When integration is observed, refresh the repository's accepted default-branch truth and complete any required documentation or Work reconciliation before declaring Done.

## 5. Cleanup only after proof

Clean a worktree or local branch only when the owning workflow proves it is eligible, clean, and no longer needed. Preserve unrelated or unmerged work. Prefer recoverable handling whenever repository policy offers it.

## Red flags

- Treating passing tests as merge authorization.
- Guessing the base from common branch names.
- Reusing verification from an older head.
- Cleaning the workspace before landing is independently observed.
- Performing raw Git/GitHub mutation when KIS or another governed path exists.

## Completion

Closeout is complete only when the chosen outcome is explicit, required repository/KIS evidence matches the exact head, documentation/state reconciliation is complete where required, and cleanup is either safely verified or recorded as blocked.