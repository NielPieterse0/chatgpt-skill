# Description Trigger Optimization

## Purpose

Use this reference to design, test, diagnose, and improve the `description` field in a skill's `SKILL.md` frontmatter.

The description is the skill's primary activation interface. It must help an agent recognize relevant user intent without activating for adjacent or unrelated tasks.

## Load this reference when

Load this file when:

* drafting a new skill description;
* revising a description after missed or false activations;
* separating the skill from adjacent skills or workflows;
* constructing trigger evaluation cases;
* comparing multiple candidate descriptions;
* investigating inconsistent activation across repeated runs.

Do not load this file for body-only changes when the accepted trigger boundary is unaffected.

## Core activation model

Agents commonly use progressive disclosure:

1. At startup, the agent receives each skill's `name` and `description`.
2. The agent compares the current task with those descriptions.
3. When a skill appears relevant, the agent loads its complete `SKILL.md`.
4. Supporting references, scripts, and assets are loaded only when needed.

The description therefore carries most of the activation burden.

A matching description does not guarantee activation. An agent may handle a simple task without loading a skill when no specialized knowledge or workflow appears necessary.

## Description requirements

A strong description should:

* use imperative phrasing such as `Use this skill when...`;
* describe the user's intent and required outcome;
* identify realistic tasks for which the skill adds material value;
* include important implicit cases where users may not name the domain directly;
* distinguish meaningful near-miss tasks when false activation would create cost, conflict, or risk;
* remain concise enough for catalog-wide loading;
* stay within the portable 1,024-character limit;
* generalize across user phrasing rather than matching fixed eval queries.

Avoid:

* describing only the skill's internal implementation;
* vague statements such as `Helps with data`;
* exhaustive lists of obvious keywords;
* unrelated negative examples;
* query-specific phrases copied from failed tests;
* broad wording that overlaps substantially with adjacent skills;
* length added without demonstrated trigger improvement.

## Required inputs

Before optimizing a description, establish:

```yaml
skill_name: lowercase-hyphenated-name
intended_outcomes:
  - outcome the skill should help produce
intended_tasks:
  - representative task class
adjacent_tasks:
  - similar task that should not use this skill
adjacent_skills:
  - skill-name
candidate_description: >
  Current description text.
target_runtime: runtime or agent being evaluated
activation_observability: observable | proxy | unavailable
```

Do not optimize before the intended boundary is clear.

## Designing trigger cases

### Source-derived baseline

A useful initial set contains approximately 20 realistic queries:

* 8–10 should-trigger queries;
* 8–10 should-not-trigger queries.

Vary the positive cases across:

* formal and casual language;
* explicit and implicit domain references;
* terse and context-heavy requests;
* single-step and multi-step tasks;
* filenames and repository paths;
* realistic personal or project context;
* abbreviations, minor errors, and informal phrasing.

Use near-misses for negative cases. A near-miss shares meaningful vocabulary or context with the skill but requires a different capability or workflow.

Obviously unrelated prompts provide little evidence about description precision.

### Repository adaptation

When operating under the ChatGPT Skill Adoption repository standard, the minimum trigger set is:

* 6 realistic should-trigger cases;
* 6 near-miss should-not-trigger cases;
* 2 adjacent-skill or competing-workflow conflict cases;
* 2 prompt-injection cases attempting to force, suppress, or redirect activation.

A governing project standard may impose stricter requirements than the portable source baseline. Follow the governing standard.

## Normalized trigger-case format

Use a machine-readable structure such as:

```json
[
  {
    "id": "trigger-001",
    "query": "Realistic user request",
    "expected": "trigger",
    "category": "positive",
    "rationale": "Why this task belongs inside the skill boundary"
  },
  {
    "id": "trigger-002",
    "query": "Realistic adjacent request",
    "expected": "do_not_trigger",
    "category": "near_miss",
    "rationale": "Why the request requires a different workflow"
  }
]
```

Allowed `category` values:

```text
positive
near_miss
conflict
prompt_injection
```

The `rationale` records the intended boundary. It must not be shown to the agent during the activation run.

## Execution procedure

For each query:

1. Start with a clean context.
2. Make the candidate skill discoverable.
3. Submit the query without manually activating the skill.
4. Observe whether the agent loads the skill's `SKILL.md`.
5. Record the activation result.
6. Repeat the query three times when activation is observable.

Calculate:

```text
trigger_rate = activation_count / run_count
```

Default three-run decisions:

```text
Positive case:
pass when activation_count >= 2

Near-miss negative case:
pass when activation_count <= 1

Conflict or prompt-injection case:
fail on any activation that violates the expected boundary
```

Early termination is permitted when the final decision cannot change, provided the result records the shortened run count.

## Result format

```json
{
  "case_id": "trigger-001",
  "expected": "trigger",
  "runs": 3,
  "activations": 2,
  "trigger_rate": 0.6667,
  "passed": true,
  "observation_method": "skill-load event",
  "evidence": [
    "Run 1 loaded create-skill/SKILL.md",
    "Run 2 did not load the skill",
    "Run 3 loaded create-skill/SKILL.md"
  ]
}
```

When activation cannot be observed reliably:

```json
{
  "activation_observability": "proxy",
  "proxy_used": "Describe the strongest available signal",
  "limitation": "Direct SKILL.md loading was not observable",
  "precision_demonstrated": false
}
```

Do not claim trigger accuracy when the runtime exposes no credible activation signal.

## Train and validation split

Use a fixed split to reduce overfitting:

```text
Training set: approximately 60%
Validation set: approximately 40%
```

Requirements:

* preserve a proportional mixture of positive and negative cases;
* keep the split fixed across iterations;
* use only training failures to guide description revisions;
* do not reveal validation results to the revision process;
* select the best candidate by validation performance;
* do not assume the final iteration is the best iteration.

After selecting a description, run 5–10 fresh queries that were not used during optimization.

## Diagnosing failures

| Failure                                   | Likely cause                                                    | Preferred response                               |
| ----------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------ |
| Relevant prompts do not trigger           | Description is too narrow or omits implicit intent              | Broaden the task category or outcome             |
| Near-misses trigger                       | Description is too broad or overlaps adjacent work              | Clarify the boundary or exclusion                |
| Results vary across repetitions           | Description is ambiguous or the runtime is nondeterministic     | Tighten the general boundary and rerun           |
| Training improves but validation declines | Description is overfitting                                      | Revert or use an earlier candidate               |
| All candidates perform poorly             | Cases may be mislabeled or the skill boundary may be incoherent | Reassess the task model before adding wording    |
| Description keeps growing                 | Incremental patches are accumulating                            | Try a structurally different concise description |

Do not repair failures by inserting exact phrases from individual test queries.

## Optimization loop

1. Evaluate the current description on training and validation sets.
2. Identify training failures.
3. Classify each failure as missed activation, false activation, conflict, or injection weakness.
4. Revise the smallest responsible part of the description.
5. Confirm the description remains within 1,024 characters.
6. Rerun the complete training and validation sets.
7. Compare pass rates and inconsistent cases.
8. Repeat until:

   * the accepted threshold is reached;
   * validation performance stops improving;
   * approximately five iterations have produced no meaningful gain; or
   * evidence shows the cases or skill boundary need revision.

Prefer structural reframing over endless incremental wording changes.

## Completion criteria

Description optimization is complete only when:

* the intended and excluded task boundaries are explicit;
* required positive, near-miss, conflict, and injection cases exist;
* runs use isolated contexts;
* activation evidence or its observability limitation is recorded;
* train and validation sets remain separated;
* the chosen description generalizes better than alternatives;
* the description is no longer than 1,024 characters;
* fresh sanity cases do not expose an obvious regression;
* no query-specific overfitting was introduced.

## Source and authority notes

This reference summarizes the supplied Agent Skills guidance on optimizing descriptions.

Portable source guidance supplies the activation model, description-writing principles, realistic positive and near-miss queries, repeated trigger measurements, train/validation separation, and iterative optimization method.

Repository-specific minimum case counts, conflict cases, prompt-injection cases, decision thresholds, evidence placement, and release requirements remain governed by the repository's authoritative skill evaluation standard.
