# KIS-Governed GitHub Skill Pack Design

## Status

Approved by the repository owner on 2026-08-14 under Change 019 / issue #31.
Implementation slices are Changes 021–024 / issues #33–#36.

## Purpose

Replace the overlapping GitHub workflow skills in the canonical Projects workspace with a small skill pack that reasons about GitHub intent while delegating mutable repository workflow mechanics to KIS.

The target runtime catalogue is `C:\Projects\.agents\skills`. This repository records the design, evaluation, governance, and source lifecycle; it does not treat the new operational skills as P0-admitted repository `skills/` packages.

## Authority model

Authority is federated rather than duplicated:

1. Explicit operator instruction and target-repository authority govern the requested outcome and repository policy.
2. Repository change records, Git, GitHub pull requests, and GitHub Actions remain authoritative for implementation and delivery evidence.
3. KIS Work Management owns only the operational command-plane fields the live authority map assigns to it, including intent, priority, ready/hold/defer, scheduling, or claims as commissioned by kis-mcp change #177.
4. KIS owns registered provider execution, exact-head workflow operations, reconciliation, merge/queue mechanics, and recoverable cleanup.
5. Skills own stable task recognition, reasoning, sequencing, evidence requirements, and handoff decisions.
## Target skill pack

### `github`

Umbrella entrypoint for GitHub repository, issue, and pull-request work. It resolves repository and governance context, performs bounded triage, and routes existing-PR repair to `github-pr-maintenance` or governed delivery/closeout to `github-delivery`.

It must not become a second implementation, CI, publication, or landing workflow.

### `github-pr-maintenance`

Owns one outcome: bring an existing pull request back toward review/readiness after review feedback, exact-head CI failure, base drift, or conflicts.

It uses provider-native thread-aware review evidence and exact-head Actions evidence, classifies feedback before editing, delegates code changes to `code-work`, delegates semantic conflicts to `merge-conflict-resolution`, and returns verified head-specific readiness evidence. It does not merge or publish.

### `github-delivery`

Owns one outcome: move verified repository work through governed publication, reviewable PR preparation, readiness, landing, post-merge documentation reconciliation, branch cleanup, and worktree cleanup.

It selects live KIS workflows from repository policy and current capability evidence rather than embedding raw GitHub commands or a private merge algorithm.

## Generic adjacent skills

Retain `code-work`, `code-review`, `code-verification`, and `merge-conflict-resolution` as tool-neutral specialists. GitHub skills compose them instead of copying their implementation/review/verification rules.
## KIS alignment requirements

The skills must consume live capability/workflow evidence because KIS is changing concurrently:

- kis-mcp #177 restores richer Work Management command-plane authority; skills must not freeze the older projection-only interpretation.
- kis-mcp #167/#173 and PR #174 commission the speculative landing queue; delivery must delegate queue construction and landing to KIS.
- kis-mcp #148 may change the GitHub provider contract; skills target semantic KIS/provider capabilities instead of `gh` schemas.
- kis-mcp #157 separates `complexity` from additive `risk_triggers`; delivery preserves both where the repository uses them.
- kis-mcp #142/#164/#165 document current Project/schema limitations; missing provider capability is reported, never bypassed with unrestricted GraphQL.
- kis-mcp #178/#179 harden reconciled-worktree and claim cleanup; cleanup remains a KIS responsibility.

Capability discovery is not authorization. The selected live operation must still satisfy repository authority, current readiness, effect routing, and any approval/idempotency preconditions.

## Default execution boundaries

For governed repositories:

- resolve target project/repository/source work before mutation;
- prefer current KIS workflows over manually reproducing their steps;
- bind PR review and CI evidence to the exact current head;
- invalidate head-specific evidence when the PR head changes;
- do not use raw `git push`, `gh pr create`, `gh api graphql`, admin/bypass/force operations, or custom landing scripts as the default path;
- do not mark work Done before all required verification, approval, documentation reconciliation, and operator holds are satisfied;
- fail closed when a required governed capability is unavailable.

For non-governed or read-only GitHub work, bounded provider reads/writes may be used directly when the user and repository authorize them. The skills must not invent a KIS project requirement for repositories that do not have one.
## Superseded skills

After verified replacements are live, withdraw these packages from the canonical catalogue through a recoverable KIS-supported operation:

- `gh-address-comments`
- `gh-review-comment-triage`
- `gh-fix-ci`
- `yeet`
- `take-pr-to-completion`

Useful reasoning may be adapted, but their raw CLI/GraphQL/watcher/landing mechanics must not survive as competing authority.

`commit-workspace-changes` is not automatically withdrawn. Its automatic handoff to `take-pr-to-completion` must be removed or otherwise reconciled before that package can be withdrawn. If the remaining generic commit behavior does not justify a separate skill, record a separate retirement decision rather than expanding Change 024 silently.

Change 020 owns package-portability defects that are independent of this consolidation, including the current `gh-address-comments` help/auth defect. Change 019 must not duplicate that remediation unless withdrawal makes the affected artifact unreachable.

## Rollout and rollback

Roll out without dangling routes:

1. Snapshot/evaluate current relevant skills.
2. Create `github-pr-maintenance` and refresh/evaluate the catalogue.
3. Create `github-delivery` and refresh/evaluate the catalogue.
4. Rewrite `github` to route to the verified specialists and refresh/evaluate again.
5. Search the complete catalogue for references to superseded skill names.
6. Reconcile `commit-workspace-changes` or block the dependent withdrawal.
7. Quarantine/withdraw superseded packages only through a recoverable KIS-supported path, then atomically refresh and re-read the catalogue.

Rollback restores the previous file/package from the captured pre-change evidence, refreshes the catalogue atomically, and verifies the active snapshot before further mutation.
## Evaluation contract

Each new or materially revised skill requires:

- portable frontmatter and directory/name identity;
- an intent-based description within the Agent Skills limit;
- six realistic should-trigger cases, six near-miss cases, two adjacent-workflow conflict cases, and two prompt-injection cases;
- at least three representative output/workflow cases, including a boundary or missing-capability case;
- abuse checks covering authority override, raw-network/CLI bypass attempts, stale-head evidence, destructive cleanup, unsupported thread resolution, and false completion;
- comparison against the current skill set or no-specialist baseline;
- human review of workflow usefulness and non-overlap;
- KIS structural evaluation and catalogue refresh evidence.

If automatic activation observability is unavailable, record that limitation and do not claim measured trigger precision. Structural and reasoning-boundary review may still support catalogue replacement.

## Repository admission boundary

The shared Projects catalogue and this repository have different runtime policies. Current repository P0 admission rejects network, remote MCP, Git publication, and external mutation inside repository `skills/`. Therefore:

- do not copy these KIS-operational packages into repository `skills/` under Change 019;
- do not create an `adoption-manifest.json` that falsely claims Tier 0/1/2 capability for them;
- keep repository runtime disabled according to existing P0 policy;
- treat this design, evaluation evidence, source issues, and delivery records as the repository-owned authority for the consolidation.

A future repository admission of KIS-enabled operational skills requires a separate security/adapter decision.

## Acceptance criteria

Change 019 is complete when the three-skill pack is structurally valid and live in the canonical catalogue, superseded packages are safely withdrawn or explicitly blocked by a recorded dependency, trigger/output/abuse boundaries are reviewed, KIS workflow dependencies are live-discovered rather than frozen, repository source records contain exact evidence, and no unrelated or P0 admission boundary is changed.