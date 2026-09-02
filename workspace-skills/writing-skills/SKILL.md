---
name: writing-skills
description: Use when creating or materially revising an Agent Skill and a test-first, pressure-scenario method is needed to prove the skill changes agent behavior rather than merely reading well.
license: MIT
---

# Writing Skills

Apply RED-GREEN-REFACTOR to reusable process guidance. Preserve the upstream behavioral-testing discipline while leaving package authority and lifecycle decisions with the canonical skill-governance skills.

## Authority and role

- `create-skill` owns skill scope, package structure, progressive disclosure, provenance, and authoring lifecycle.
- `evaluate-skill` owns activation, output, abuse, compatibility, efficiency, and release-evidence decisions.
- `improve-skill` owns evidence-backed revision of an accepted candidate.
- This skill supplies a test-first method for discovering and correcting behavioral instruction failures.
- Repository instructions and KIS remain higher authority for files, tools, Work state, and mutations.

## TDD mapping

| Software TDD | Skill development |
|---|---|
| Test case | Representative or pressure scenario |
| Production code | Skill instructions |
| RED | Baseline or previous version exhibits the target failure |
| GREEN | Minimal skill change fixes that observed failure |
| REFACTOR | Generalize wording and close real loopholes without regressing passing cases |

If there is no observed baseline failure or reusable outcome, do not add rules merely because they sound prudent.## Choose the test form that matches the failure

- **Discipline failure:** the agent knows the rule but skips it under pressure. Use realistic pressure scenarios, explicit invariant wording, and counters to rationalizations actually observed.
- **Wrong output shape:** specify the positive result contract and compare outputs. Do not pile prohibitions onto a shaping problem.
- **Omitted required element:** add a structural required slot and test whether it appears reliably.
- **Conditional behavior:** key the instruction to an observable condition rather than a broad unconditional rule with exceptions.
- **Technique or pattern:** test recognition, correct application, edge cases, and when not to apply it.
- **Reference skill:** test whether the needed information can be found and applied without loading irrelevant material.

## RED

1. Use `create-skill` to establish the reusable outcome, intended activation boundary, and package authority.
2. Define representative cases before editing the skill. Include realistic near-misses and pressure where the suspected failure is behavioral discipline.
3. Run the strongest available baseline: no skill or the previous accepted version.
4. Record what actually failed, including rationalizations or output defects. If behavioral execution is not observable, mark it `not_observable`; do not fabricate RED evidence.

## GREEN

Change the smallest responsible part of the skill: description for activation, core workflow for always-needed behavior, a focused reference for conditional depth, or a justified script only when deterministic automation is warranted. Re-run the same cases and require evidence that the target failure improved.## REFACTOR

Review new failures and variance. Tighten only generalizable ambiguity exposed by evidence. Do not tune against held-out validation cases, copy exact prompts into the description, or add a rule for every hypothetical misuse.

Keep descriptions focused on realistic trigger conditions rather than compressing the workflow into metadata. Keep `SKILL.md` lean and move only conditionally needed depth into focused references.

## Pressure-testing discipline

For rule-enforcing skills, combine pressures that realistically cause shortcuts: urgency, sunk cost, authority pressure, fatigue, or apparent simplicity. Record the actual rationale used to violate the rule, then add the smallest counter that closes that observed loophole.

Micro-tests can compare wording variants when the active evaluation runtime supports isolated repeated samples. They supplement rather than replace representative output and activation evaluation. Never invent run counts, token cost, or behavioral success when the runtime cannot expose them.

## Boundaries

Do not bundle the upstream graph renderer, helper scripts, remote assets, deployment steps, or publication workflow. Skill creation does not authorize installation or catalogue publication. Hand structural and behavioral evidence back to `evaluate-skill`, and use `improve-skill` for further evidence-backed iterations.

## Completion

The method is complete when a reproducible baseline exists or is explicitly unavailable, the change targets an observed reusable failure, applicable cases are rerun without held-out tuning, structural/package authority remains with `create-skill`, and the resulting lifecycle decision is recorded through `evaluate-skill`.