# Skill Adoption Implementation Backlog

## Authority

This document owns the dependency order, priority, evidence, and stop criteria for implementing the accepted skill-adoption architecture.

It does not redefine package, security, evaluation, or adapter requirements. Follow the linked authoritative documents for each task.

## Current Baseline

Verified repository baseline before Change 011:

- P0 authority, discovery, validation, manifest, capability, kill-switch, research, package, evaluation, and adapter-boundary controls are present;
- KIS Work Management is the required tracked-work control plane, with issue-backed repository identity and GitHub Project projection;
- the shared Projects workspace catalogue used by KIS Skills is `C:\Projects\.agents\skills`;
- `C:\Users\piete\.codex\skills` is an upstream candidate/source surface, not the canonical Projects workspace catalogue;
- `develop-code` and `develop-docs` are admitted canonical repository Tier 2 project-content workflow skills under `skills/`;
- runtime remains globally disabled, so no repository-admitted skill is runtime-enabled;
- the historical dirty checkout on `NielPieterse0/adopt-modularity-assessment` is preserved evidence and must not be reset, cleaned, or merged wholesale.

Repository reconciliation for Changes 001–010 is complete. Change 011 reopens bounded reconciliation because the operator requested a local-main cleanup, workspace catalogue changes, and a full catalogue compliance audit.

Stable prior dispositions remain evidence:

- `modularity-assessment`: the prior repository runtime/canonical release decision is **DEFER** until isolated target behavioral execution and activation observability are available. Change 013 / #24 separately authorizes deliberate **shared workspace catalogue adoption**; it does not waive the repository runtime release gates. See [`docs/testing/modularity-assessment-release-decision.md`](../testing/modularity-assessment-release-decision.md).
- GitHub governance Change 007: **BLOCKED-EXTERNAL / CLOSED AS PROVIDER LIMITATION**. Repository policy remains unchanged; live enforcement must be retried when a bounded compatible provider operation is available. See [`docs/operations/github-governance-status.md`](../operations/github-governance-status.md).
- `develop-code` and `develop-docs` historical drafts are **SUPERSEDED / REDUNDANT** because their portable payloads match the admitted repository skills.
- `tdd-change-discipline` remains **NOT ADMITTED FOR THIS REPOSITORY** because its mandatory gate/governance contract conflicts with the actual KIS/npm workflow. Change 016 / #27 now tracks the operator-requested shared-catalogue status change and future redesign. See [`docs/testing/workflow-draft-disposition.md`](../testing/workflow-draft-disposition.md).

## Current Active Backlog

Use the issue-backed Work Management records as the live execution state. Parent Change 011 / #22 coordinates the sweep; child work is independently verifiable and must preserve unrelated state.

1. **Change 012 / #23 — reconcile local `main`.** Preserve the dirty historical branch, use a clean registered issue worktree, refresh governed remote state, and reconcile local `main` to accepted remote `main` after cleanup changes land.
2. **Change 013 / #24 — adopt `modularity-assessment` into the shared workspace catalogue.** Resolve the Codex-created candidate from preserved evidence, verify its portable package and safety boundaries, and confirm KIS discovery. Repository runtime admission remains separately gated.
3. **Change 014 / #25 — withdraw `code-as-docs-governance` from shared canonical discovery.** Preserve reviewable evidence and retain future re-admission requirements as backlog work.
4. **Change 015 / #26 — withdraw `use-doc-solution` from shared canonical discovery.** Preserve/reconcile the historical candidate evidence and require a fresh adoption decision before future re-admission.
5. **Change 016 / #27 — change the shared-catalogue status of `tdd-change-discipline`.** Align active discovery with the existing incompatibility decision and retain redesign/re-evaluation as backlog work.
6. **Change 017 / #28 — audit every active shared canonical skill.** Run after the requested catalogue changes. Classify every package against the applicable portable package, security, trigger/overlap, progressive-disclosure, script, and portability requirements; create bounded follow-up records for every material unresolved failure.

Dependency rules:

- Change 012 must preserve the historical branch before any local cleanup action.
- Changes 013–016 may be evaluated independently when they do not overlap owned paths, but each catalogue mutation requires source evidence and a KIS refresh/re-read.
- Change 017 must use the post-mutation catalogue as its final audit baseline; an initial pre-mutation inventory may be captured for comparison.
- No child may silently enable repository runtime skills or weaken the P0 security standard.

## Historical P1 Prototype Plan

The sequence below records the original pre-admission prototype plan. It is retained as historical planning evidence and is not the live work queue. Where it conflicts with the Current Active Backlog or admitted artifacts, the live repository and issue-backed Work Management records govern.

Execute the historical sequence only as background rationale; do not create its named prototype merely because it appears below.

### P1.1 Select and specify the low-risk prototype

**Owner:** repository owner

**Recommended candidate:** a Tier 1 `skill-candidate-assessor` that reads repository and candidate evidence, applies the repository adoption standards, and produces a structured adopt/adapt/defer/reject assessment without executing candidate content.

**Required evidence:**

- real project tasks showing repeated assessment work;
- explicit customer outcome and baseline behavior;
- capability tier, read scope, inputs, outputs, exclusions, and rollback;
- proof that the task is coherent and not already handled reliably without a skill.

**Stop criteria:** one bounded candidate is approved for evaluation. Stop and reject the prototype if its expected value is merely duplicating `AGENTS.md` or general model capability.

### P1.2 Create evaluation definitions before the skill

**Owner:** evaluation standard

Create only the files consumed by the prototype evaluation:

```text
tests/skills/skill-candidate-assessor/
├── trigger-cases.json
├── output-evals.json
├── abuse-cases.json
└── fixtures/
```

**Required evidence:**

- 6 positive, 6 near-miss negative, 2 conflict, and 2 injection trigger cases;
- 3 representative output tasks with critical assertions;
- baseline run instructions;
- abuse cases for malicious candidate files, traversal, secrets, external instructions, and prohibited capability requests;
- human-review criteria.

**Stop criteria:** cases are realistic, objective, bounded, and reviewable before any candidate description is optimized against them.

### P1.3 Implement the canonical Tier 1 skill

**Owner:** package standard and security standard

Create the smallest admitted skill:

```text
skills/skill-candidate-assessor/
├── SKILL.md
├── adoption-manifest.json
└── references/              # only when eval evidence proves they are needed
```

Do not add scripts or assets to the first prototype unless repeated execution traces demonstrate a deterministic need.

**Required evidence:**

- portable frontmatter and lean workflow;
- explicit reference load conditions;
- immutable source and license basis;
- Tier 1 repository-read scope only;
- content hash, approval, and rollback;
- repository validation passes while runtime remains disabled.

**Stop criteria:** canonical skill is structurally and security valid. Do not package it if any capability or source decision is unresolved.

### P1.4 Implement the minimum ChatGPT adapter mapping

**Owner:** adapter architecture

Introduce `adapters/chatgpt/` only for the files and logic required by the admitted prototype. The adapter must consume the canonical skill and admission result.

**Required evidence:**

- target capability map;
- generated OpenAI metadata when current target documentation requires it;
- explicit unsupported capability handling;
- deterministic package inclusion report;
- no target-specific facts copied into canonical provenance or security records.

**Stop criteria:** adapter output is reproducible and fails closed on unsupported required behavior.

### P1.5 Add target packaging and validation

**Owner:** package standard

Implement only the validator or packager required to produce the prototype package under `.work/packages/chatgpt/`.

**Required evidence:**

- canonical hash and adapter identity recorded;
- admitted file allowlist;
- exclusion of manifest, evals, generated evidence, hooks, MCP, installers, credentials, and prohibited artifacts;
- structural, link, metadata, and package-integrity checks;
- no writes outside `.work/packages/chatgpt/`.

**Stop criteria:** repeated packaging from the same inputs produces the same content and report.

### P1.6 Run the complete prototype evaluation

**Owner:** evaluation standard

Run trigger, output, efficiency, abuse, compatibility, human-review, disablement, and rollback checks.

**Required evidence:**

- isolated with-skill and baseline runs;
- assertion evidence and human feedback;
- available time, token, tool-call, retry, and output-size signals;
- target behavior and observability limitations;
- abuse results with zero critical failures;
- accepted adoption decision and residual risk.

**Stop criteria:** admit, revise, defer, or reject. Do not continue iterating when the baseline is already sufficient or the required boundary cannot be enforced.

### P1.7 Decide runtime enablement

**Owner:** repository owner and security standard

Enable only when the admitted prototype, target package, evaluation record, Git-aware validation, rollback, and owner review all pass.

**Required evidence:**

- updated `config/runtime-control.json` reason, actor, and UTC timestamp;
- repository validation and catalog output;
- successful GitHub verification workflow;
- documented emergency disable test.

**Stop criteria:** runtime is either deliberately enabled for the single admitted skill or remains disabled with the reason recorded. No other skill may be added opportunistically.

## P2 — Implement After the First Proof

Prioritize only work justified by prototype evidence:

1. automate trigger-run capture and benchmark aggregation where ChatGPT exposes reliable observability;
2. add machine-readable eval schemas only when the harness consumes them;
3. add deterministic script-runner controls if a proven skill requires scripts;
4. add adapter contract tests and reusable packaging fixtures;
5. add upstream change monitoring for adopted sources without automatic adoption;
6. evaluate a second skill only after the first lifecycle is stable;
7. add a Codex adapter against the same canonical skill and shared evals;
8. add cross-adapter parity tests for portable behavior;
9. consider Tier 2 `.work/<skill-name>/` writes only after enforcement and approval evidence is accepted.

## Deferred or Excluded

The following remain excluded until separate architecture, controls, tests, and owner approval exist:

- recursive or registry-wide automatic repository runtime discovery;
- broad automatic catalogue import without bounded review;
- network access or runtime package resolution;
- remote MCP;
- inherited credentials or secrets;
- lifecycle hooks or background loops;
- Git commit, push, pull-request creation, or external diff transmission by admitted runtime skills;
- deployment, deletion, or external mutation by admitted runtime skills;
- direct writes outside the repository or explicitly authorized shared-catalogue operations;
- automatic update from mutable upstream branches;
- target-specific forks of canonical repository skills.

## Task Intake Rule

Every future skill task must identify:

- the customer outcome;
- whether the task affects repository runtime state, shared workspace catalogue state, or both;
- the authoritative owner documents affected;
- source evidence and immutable revision or trusted-local identity;
- canonical versus adapter scope;
- capability tier and enforcement point where repository runtime is involved;
- baseline and evaluation evidence appropriate to the requested boundary;
- package and runtime impact;
- rollback and stop criteria.

Reject or re-scope tasks that cannot provide these fields without inventing unsupported assumptions.

## Backlog Completion

Change 011 is complete only when Changes 012–017 have accepted dispositions, the requested shared-catalogue changes are verified through KIS, the final compliance audit has no untracked material findings, repository authority is internally consistent, and local `main` is clean and synchronized without loss of the preserved historical branch state.

The historical P1 definition remains historical evidence and does not override the current issue-backed queue.