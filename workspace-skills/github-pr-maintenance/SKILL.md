---
name: github-pr-maintenance
description: Use this skill when an existing GitHub pull request needs to be brought back toward review readiness after actionable review feedback, requested changes, failing GitHub Actions checks, base drift, or merge conflicts. Triage exact current-head evidence, distinguish real issues from stale or false-positive findings, coordinate bounded fixes and verification, and return readiness evidence. Do not use for general GitHub orientation, new change publication, PR creation, landing, or post-merge cleanup.
---

# GitHub PR Maintenance

Bring one existing pull request back toward review readiness without taking ownership of publication or landing.

## Boundaries

- Resolve the exact repository, pull request, base branch, and current head SHA before acting.
- Follow the target repository's authority and Work Management rules before this skill.
- Treat the current PR head as the identity of review and CI evidence. A new head invalidates stale head-specific conclusions where policy requires fresh evidence.
- Do not merge, enqueue, publish a new branch, create a new PR, delete branches, or clean worktrees from this skill.
- Do not use raw `gh`, unrestricted GraphQL, or another network path to bypass a missing KIS/provider capability.
- External replies, reviews, reruns, or thread-state mutations require authorization from the user or an invoking governed workflow.

## Resolve governance and live capability

For a KIS-managed repository, resolve the project and source work record first. Use the live Work Management authority map for operator intent, readiness, holds, claims, or scheduling instead of assuming fixed field ownership.

Use the current KIS/provider capability catalogue rather than copied schemas. Prefer a complete advertised workflow when it matches the task. If a required operation is unavailable, report the missing capability and stop that part of the workflow rather than substituting an unmanaged command.

## Inspect the exact PR state

Collect only the evidence needed for the maintenance problem:

1. Current PR metadata, base, head SHA, changed files, and relevant diff.
2. Thread-aware review comments and reviews. Prefer the current provider's review-comment/thread read surface when it exposes resolved, outdated, collapsed, path, line, author, and pagination state.
3. Provider-native GitHub Actions evidence for the exact current head when checks are relevant.
4. Repository instructions and local code around any disputed finding.

Do not treat old line numbers, bot prose, a top-level comment summary, or a check from another SHA as current evidence.

## Triage review feedback

For each relevant thread or requested change, classify the claim before editing:

- `real`: current code still exhibits the claimed problem.
- `already fixed`: the current head contains the needed correction.
- `stale`: the comment refers to code or context no longer present.
- `false positive`: current code and governing requirements disprove the claim.
- `needs decision`: evidence cannot resolve a product, architecture, or contradictory-review choice.

Ground the verdict in current code, callers, tests, contracts, and repository authority. Group related threads by behavior, but keep each fix traceable to the feedback it addresses.

## Triage CI failures

When GitHub Actions is failing, prefer the live KIS exact-head CI triage workflow when available. Otherwise use provider-native Actions reads that prove the run head matches the expected PR head.

Classify failures into the narrowest supported cause, such as implementation, tests, governance topology, base state, provider/tooling, runner environment, or unresolved. Do not change source code for an unrelated infrastructure or stale-head failure.

## Repair the PR

When edits are authorized:

1. Hand real implementation fixes to `code-work` with the exact finding and affected behavior.
2. Hand semantic Git conflicts to `merge-conflict-resolution`; do not pick ours/theirs mechanically.
3. Preserve unrelated user changes and the repository's current change/claim boundary.
4. After any edit, run the target repository's governed verification path. Prefer KIS `execute-current-change` or `verify-current-change` when advertised and applicable.
5. Re-resolve the resulting PR head before relying on prior review or CI evidence.

If the repair produces a new local commit that still needs publication or PR-head update, return that state to the invoking delivery workflow; do not invent a push path here.

## Review replies and thread state

Reply only when authorized and only through an approved live provider operation. For a fix, cite the changed behavior and fresh verification. For stale or false-positive feedback, state the concrete current evidence.

Resolve a review thread only when the live approved provider/KIS surface explicitly exposes that mutation and the task authorizes it. If thread resolution is not exposed, report the addressed thread and capability gap; never bypass it with raw GraphQL.

## Completion

Return:

- repository, PR, base, and final observed head SHA;
- feedback classifications and which items were changed, already fixed, stale, false positive, or unresolved;
- exact-head CI classification and current check state when relevant;
- files/behavior changed and verification evidence;
- replies or review mutations actually performed;
- remaining blockers, required decisions, or unavailable capabilities;
- whether the PR is ready to return to `github-delivery` for governed landing.

Do not call the PR ready merely because local tests pass. Readiness must be supported by the current head, applicable review state, exact-head checks, repository policy, and any governed Work Management gate.