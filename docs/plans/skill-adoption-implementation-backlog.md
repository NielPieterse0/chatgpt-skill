# Skill Adoption Implementation Backlog

## Authority

This document owns the dependency order, priority, evidence, and stop criteria for implementing the accepted skill-adoption architecture.

It does not redefine package, security, evaluation, or adapter requirements. Follow the linked authoritative documents for each task.

## Current Baseline

Verified reconciliation baseline for Change 027 / issue #41:

- GitHub `main` is `66912c994f94a7da67e6b92e01279f5ed03778ed` and KIS registered default-branch tracking matches that exact revision;
- GitHub Actions `Verify` run `31776682295` completed successfully for that exact `main` revision on 14 August 2026;
- GitHub has no open pull requests and the only remote branch is `main` at the reconciliation baseline;
- Changes 001–026 are closed; none of their source records belongs in the live execution queue;
- P0 authority, discovery, validation, manifest, capability, kill-switch, research, package, evaluation, and adapter-boundary controls are present;
- KIS Work Management remains the required tracked-work control plane, with issue-backed repository identity and GitHub Project projection;
- the shared Projects workspace catalogue used by KIS Skills is `C:\Projects\.agents\skills`, while `C:\Users\piete\.codex\skills` remains an upstream candidate/source surface;
- `develop-code` and `develop-docs` are admitted repository Tier 2 project-content workflow skills, while the shared catalogue also contains the separately governed KIS-aligned workflow packages restored by Change 026;
- `config/runtime-control.json` remains fail-closed with `skills_enabled: false`, so catalogue presence does not imply repository runtime enablement;
- the historical dirty checkout on `NielPieterse0/adopt-modularity-assessment` remains preserved evidence and must not be reset, cleaned, or normalized into accepted current state.

The completed Changes 011–026 cover the canonical workspace/local-main cleanup, compliance audit, catalogue withdrawals and adoption decisions, branch/worktree reconciliation, portability/package remediation, the KIS-governed `github` / `github-pr-maintenance` / `github-delivery` pack, retirement of superseded GitHub workflow skills, and restoration of KIS-aligned `develop-code`, `develop-docs`, and `mcp-development` shared-catalogue packages.

Stable prior dispositions remain evidence:

- `modularity-assessment`: the repository runtime/canonical release decision remains **DEFER** until isolated target behavioral execution and activation observability are available. Change 013 / #24 separately authorizes shared workspace catalogue adoption and does not waive repository runtime release gates. See [`docs/testing/modularity-assessment-release-decision.md`](../testing/modularity-assessment-release-decision.md).
- GitHub governance Change 007 remains **BLOCKED-EXTERNAL / CLOSED AS PROVIDER LIMITATION** for live main-branch enforcement. Repository policy remains unchanged. See [`docs/operations/github-governance-status.md`](../operations/github-governance-status.md).
- `tdd-change-discipline` remains **NOT ADMITTED FOR THIS REPOSITORY** because its mandatory gate/governance contract conflicts with the actual KIS/npm workflow. Its shared-catalogue withdrawal/redesign disposition was completed under Change 016 / #27. See [`docs/testing/workflow-draft-disposition.md`](../testing/workflow-draft-disposition.md).

## Current Active Milestone

Use issue-backed Work Management records as the live execution state. The prior cleanup, audit, portability, GitHub consolidation, and restoration queue through Change 026 is complete.

1. **Change 027 / #41 — reconcile authoritative repository status and establish the next milestone.** This documentation closeout records the exact current baseline and removes completed Changes 001–026 from active planning without disturbing historical evidence.
2. **Change 028 / #42 — harden and optimize the shared skill-authority lifecycle.** This is the next implementation milestone and parent hardening program. Discover and classify findings first, then create bounded implementation slices only for materially independent changes.

Change 028 dependency order:

- establish one coherent lifecycle from create → evaluate → improve → verify/admit/maintain before optimizing individual surfaces in isolation;
- assess trigger/description quality, output quality, efficiency, security, compatibility, abuse resistance, provenance, rollback, package structure, progressive disclosure, scripts, references, and KIS/runtime handoffs against that lifecycle;
- resolve contradictory or duplicated authority in the owning artifact rather than adding another competing workflow layer;
- create separate source work items for independent implementation changes and owner-specific external defects;
- route any KIS runtime/provider defect to `kis-mcp` rather than implementing a local bypass;
- complete repository-wide validation, KIS catalogue refresh/re-read, and a realistic end-to-end lifecycle proof only after bounded findings are resolved or explicitly tracked;
- no milestone item may silently enable repository runtime skills or weaken the P0 security standard.

## Historical P1 Prototype Plan

The sequence below records the original pre-admission prototype plan. It is retained as historical planning evidence and is not the live work queue. Where it conflicts with the Current Active Milestone or admitted artifacts, the live repository and issue-backed Work Management records govern.

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

The cleanup, audit, portability, GitHub consolidation, and restoration backlog through Change 026 is closed with accepted dispositions and verification recorded in its issue-backed history. Change 027 closes when this reconciliation is merged, the exact merged `main` revision is verified, and its source/Project lifecycle is reconciled through KIS Work Management.

After Change 027, Change 028 / #42 is the sole active milestone. It is complete only when all material lifecycle findings are resolved or tracked in bounded owner-specific source records, the create → evaluate → improve → verify/admit/maintain flow is internally consistent, final repository validation and KIS catalogue refresh/re-read succeed, and the realistic end-to-end lifecycle proof required by #42 passes. The historical P1 definition remains historical evidence and does not override this issue-backed queue.