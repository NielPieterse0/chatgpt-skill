# Skill Evaluation Standard

## Authority

This document owns the repository evaluation and release-evidence requirements for skill descriptions, outputs, efficiency, compatibility, abuse resistance, and human review.

Structural admission and capability controls are governed by [`docs/security/skill-adoption-security-standard.md`](../security/skill-adoption-security-standard.md). Package contents are governed by [`docs/standards/skill-package-standard.md`](../standards/skill-package-standard.md). Runtime-specific behavior is governed by [`docs/architecture/skill-runtime-adapters.md`](../architecture/skill-runtime-adapters.md).

## Evaluation Principle

A skill is adopted only when evidence shows that it activates for the right tasks, avoids harmful or wasteful near-misses, produces materially better outcomes than the accepted baseline, stays within justified cost and capability boundaries, and remains safe under representative abuse cases.

A successful run is not sufficient evidence. Use repeatable cases, observable assertions, explicit baselines, and human review.

## Evaluation Layers

### 1. Structural and admission checks

Run the repository validator before behavioral evaluation. Any failure blocks further release activity.

Required evidence:

- valid portable frontmatter and directory identity;
- valid adoption manifest and content hash;
- accepted provenance and license;
- allowed capability tier and scopes;
- no prohibited files, instructions, dependencies, or executable patterns;
- verified rollback and disabled runtime state during evaluation.

### 2. Trigger evaluation

Trigger evaluation tests whether the skill description causes activation only when the skill is relevant.

The initial set must contain at least:

- 6 realistic should-trigger cases;
- 6 near-miss should-not-trigger cases;
- 2 conflict cases involving an adjacent skill or competing workflow;
- 2 prompt-injection cases attempting to force, suppress, or redirect activation.

Cases must vary phrasing, explicitness, detail, complexity, paths, filenames, and realistic project context. Near-misses must share meaningful vocabulary with the skill rather than being obviously unrelated.

When the target exposes activation observability, run each case three times in an isolated context. The default decision rule is:

- a positive case passes when the skill activates in at least two of three runs;
- a negative case passes when the skill activates in no more than one of three runs;
- conflict and prompt-injection cases fail on any activation that violates the expected boundary.

If the target does not expose reliable activation observability, record the limitation and use the strongest available proxy. Do not claim trigger precision was demonstrated when activation cannot be observed.

Keep a fixed train/validation split when optimizing descriptions:

- approximately 60% train cases used to guide revisions;
- approximately 40% held-out validation cases used only to select the best generalizing description.

Do not tune descriptions to validation failures or copy exact query phrases into the description.

### 3. Output-quality evaluation

Run each representative task with:

- the candidate skill;
- no skill, or the previously accepted version when updating an existing skill.

Start with three representative tasks, including at least one boundary or malformed-input case. Use the same prompt, files, target, and output constraints for both configurations.

Each case must define:

- a realistic prompt;
- expected outcome;
- required input files or fixtures;
- objective assertions;
- critical assertions whose failure blocks adoption;
- human-review criteria.

Assertions must be observable and evidence-based. Use deterministic scripts for mechanical checks such as file existence, schema validity, row counts, dimensions, hashes, or path constraints. Use model grading only for qualities that cannot be verified mechanically, and require quoted or referenced evidence for every pass.

A candidate passes output evaluation only when:

- every critical assertion passes;
- no baseline-critical behavior regresses;
- the candidate improves at least one material outcome that the baseline does not already satisfy reliably;
- human review confirms the result is usable and aligned with the user outcome;
- the recorded benefit justifies the added context, execution, and maintenance cost.

### 4. Efficiency evaluation

Capture the following when the target exposes them:

- duration;
- input and output tokens;
- tool calls;
- retries;
- script executions;
- generated output size;
- manual intervention required.

Efficiency is a decision input, not an isolated score. A higher-cost skill can pass when the quality or risk reduction is material. A skill fails when it adds negligible value while increasing context, time, tool use, or maintenance burden.

Do not invent unavailable metrics. Record `not_observable` with the target and date.

### 5. Abuse evaluation

Every candidate must test the risks relevant to its capability tier and inputs. The initial minimum set includes:

- path traversal and out-of-scope paths;
- symlink or reparse-point attempts;
- malicious filenames and repository content containing conflicting instructions;
- prompt injection in files, tool output, generated content, and reference material;
- secret-bearing or identity-bearing input and attempted egress;
- denied network or runtime-installation attempts;
- retry, idempotency, timeout, cancellation, and output-size behavior;
- active-output injection in HTML, CSV, Markdown, links, templates, or archives when applicable;
- attempts to trigger Git publication, deployment, deletion, credential use, or external mutation.

All deterministic security assertions must pass. Any critical control failure blocks adoption and requires containment, root-cause analysis, and a new evaluation iteration.

### 6. Runtime compatibility evaluation

Evaluate the canonical skill through the selected adapter, not by assuming portable package compatibility implies target behavior.

Required evidence:

- target identity and version or verification date;
- package contents and adapter mapping;
- supported and unsupported capabilities;
- explicit and automatic activation behavior when observable;
- resource-loading behavior;
- target metadata validation;
- tool and repository-scope behavior;
- disablement and rollback behavior;
- known workspace or plan constraints.

A future Codex adapter must rerun shared cases against the same canonical skill and add target-specific cases without creating a second canonical acceptance record.

## Evidence Layout

Authoritative test definitions belong outside the runtime package:

```text
tests/skills/<skill-name>/
├── trigger-cases.json
├── output-evals.json
├── abuse-cases.json
└── fixtures/

tests/adapters/<target>/
└── <skill-name>-cases.json
```

Generated evidence belongs under `.work/`:

```text
.work/evals/<skill-name>/iteration-<n>/
├── trigger-results.json
├── with-skill/
├── baseline/
├── grading.json
├── timing.json
├── feedback.json
├── compatibility.json
└── benchmark.json
```

Do not add machine-readable schemas until a repository tool consumes them. When introduced, schemas must reject unknown fields and distinguish test definitions from generated results.

## Required Evaluation Record

Each accepted iteration must record:

- canonical skill content hash;
- adapter and target verification date;
- eval definition revision;
- baseline identity;
- run isolation method;
- assertion results with evidence;
- human feedback;
- efficiency signals and unavailable metrics;
- abuse results;
- unresolved limitations and residual risk;
- adoption decision, reviewer, and date.

## Iteration Loop

1. Run the current candidate and baseline in isolated contexts.
2. Grade deterministic assertions mechanically where possible.
3. Grade remaining assertions with evidence.
4. Review actual outputs and execution traces.
5. Identify generalizable failures, wasted work, ambiguous instructions, and weak assertions.
6. Revise the smallest responsible artifact: description, workflow, reference, script, adapter, or test.
7. Create a new iteration directory and rerun the complete applicable set.
8. Stop when the candidate passes, improvement plateaus, the baseline is already sufficient, or the required behavior cannot be enforced safely.

## Release Decisions

### Admit

Use only when all applicable structural, trigger, output, abuse, compatibility, human-review, approval, and rollback gates pass.

### Revise

Use when the outcome remains plausible but evidence exposes a bounded, correctable gap.

### Defer

Use when target observability, enforcement, dependencies, or product behavior prevent a credible decision.

### Reject

Use when the baseline is already sufficient, marginal value is too low, provenance or license is inadequate, critical risk cannot be enforced, or the skill depends on prohibited capabilities.

### Suspend

Use when an accepted skill later fails integrity, compatibility, security, or quality checks. Disable runtime first, preserve evidence, and require full re-evaluation before reinstatement.

## Completion Criteria

Evaluation is complete only when:

- the tested skill hash matches the adoption record;
- test definitions and generated evidence are separated;
- the baseline and isolation method are explicit;
- critical assertions and abuse cases pass;
- human review is recorded;
- target limitations and unavailable metrics are explicit;
- the decision and residual risk are reviewable and reproducible;
- rollback and disablement have been verified.
