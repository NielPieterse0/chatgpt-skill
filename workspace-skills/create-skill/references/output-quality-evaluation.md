# Output Quality Evaluation

## Purpose

Use this reference to determine whether a skill produces reliable, materially better outputs than an accepted baseline.

A successful demonstration is not sufficient evidence. Evaluation must use repeatable tasks, observable assertions, explicit baselines, isolated runs, human review, and recorded costs.

## Load this reference when

Load this file when:

* defining output evaluations for a new skill;
* comparing a candidate skill with no skill or a previous version;
* converting observed failures into objective assertions;
* grading generated files or responses;
* analyzing benchmark results and execution traces;
* revising a skill after failed or inconsistent evaluations;
* deciding whether repeated helper logic should become a bundled script.

Do not load this file when only the skill description or activation boundary is being changed.

## Evaluation model

Run each representative task in two configurations:

```text
Candidate:
The current skill version.

Baseline:
No skill, or the previously accepted skill version.
```

Both configurations must receive the same:

* user prompt;
* input files;
* runtime and adapter;
* output constraints;
* permissions and tool availability;
* run-isolation method.

A candidate adds value only when it improves a material outcome over the baseline without introducing unacceptable regressions, cost, or risk.

## Test-case design

### Start small

The source guidance recommends beginning with 2–3 representative cases rather than building a large suite before observing initial outputs.

Under this repository's evaluation standard, begin with at least three output cases, including one boundary or malformed-input case.

Each case should contain:

* a realistic user prompt;
* a human-readable expected outcome;
* required input files or fixtures;
* objective assertions;
* critical assertions whose failure blocks acceptance;
* human-review criteria.

Use realistic prompts containing context such as filenames, paths, field names, constraints, and informal wording. Avoid generic prompts such as `Process this file`.

## Normalized test-case format

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": "output-001",
      "prompt": "Realistic task request",
      "expected_outcome": "Human-readable description of a successful result",
      "files": [
        "tests/skills/example-skill/fixtures/input.csv"
      ],
      "assertions": [
        {
          "id": "assertion-001",
          "text": "The output file is valid JSON",
          "critical": true,
          "method": "script"
        },
        {
          "id": "assertion-002",
          "text": "The report contains at least three actionable recommendations",
          "critical": false,
          "method": "model"
        }
      ],
      "human_review": [
        "The result addresses the user's actual decision",
        "The output is usable without substantial manual correction"
      ]
    }
  ]
}
```

Allowed assertion methods:

```text
script
model
human
```

Use `script` whenever the property can be checked deterministically.

## Placement and packaging

### Portable source convention

The source guide places hand-authored evaluations in:

```text
<skill>/evals/evals.json
```

### Repository adaptation

The ChatGPT Skill Adoption repository deliberately keeps evaluations outside runtime skill packages.

Store accepted definitions under:

```text
tests/skills/<skill-name>/
├── trigger-cases.json
├── output-evals.json
├── abuse-cases.json
└── fixtures/
```

Store generated evidence under:

```text
.work/evals/<skill-name>/iteration-<n>/
```

Do not copy eval definitions, fixtures, grading results, timing data, transcripts, or benchmark evidence into the generated runtime package.

The repository's package and evaluation standards override the portable source placement convention.

## Run isolation

Every run must start with a clean context containing only the information available to that configuration.

For each case, record:

* candidate skill path or identity;
* baseline identity;
* prompt;
* input files;
* output directory;
* runtime and adapter;
* skill content hash or immutable snapshot;
* isolation method.

When comparing with a previous skill version, snapshot the previous version before editing and use that immutable snapshot as the baseline.

## Evidence workspace

A practical generated layout is:

```text
.work/evals/<skill-name>/iteration-1/
├── trigger-results.json
├── eval-<case-id>/
│   ├── with-skill/
│   │   ├── outputs/
│   │   ├── timing.json
│   │   └── grading.json
│   └── baseline/
│       ├── outputs/
│       ├── timing.json
│       └── grading.json
├── feedback.json
├── compatibility.json
└── benchmark.json
```

Generated evidence is disposable and must not become the authoritative test definition.

## Capturing efficiency data

Record observable metrics such as:

```json
{
  "duration_ms": 23332,
  "input_tokens": 3200,
  "output_tokens": 850,
  "total_tokens": 4050,
  "tool_calls": 4,
  "retries": 1,
  "script_executions": 1,
  "manual_intervention": false
}
```

When a metric is unavailable, record it explicitly:

```json
{
  "total_tokens": "not_observable",
  "target": "runtime-name",
  "verification_date": "YYYY-MM-DD"
}
```

Do not estimate or invent unavailable metrics.

Efficiency is a decision input, not an isolated pass condition. Higher cost may be justified by material quality or risk reduction.

## Writing assertions

Assertions must describe observable properties of the result.

Strong assertions:

* `The output file parses as valid JSON.`
* `The chart contains exactly three data series.`
* `All required headings are present.`
* `No produced path is outside the approved output directory.`
* `The report includes at least three recommendations.`

Weak assertions:

* `The output is good.`
* `The response is professional.`
* `The result uses exactly this sentence.`
* `The output resembles the example.`

Assertions should be:

* specific;
* observable;
* evidence-based;
* resistant to harmless wording variation;
* meaningful to the user's outcome;
* strict enough to distinguish candidate value from baseline competence.

Add detailed assertions after inspecting an initial run when necessary. Early output often reveals what should be measured.

## Grading procedure

For each assertion:

1. Inspect the actual output.
2. Apply the declared grading method.
3. Record `PASS` or `FAIL`.
4. Provide concrete evidence.
5. Do not infer missing evidence.
6. Review whether the assertion itself is useful and verifiable.

Example:

```json
{
  "assertion_results": [
    {
      "id": "assertion-001",
      "text": "The output file is valid JSON",
      "critical": true,
      "passed": true,
      "method": "script",
      "evidence": "validator exited 0 for outputs/report.json"
    },
    {
      "id": "assertion-002",
      "text": "The report contains three recommendations",
      "critical": false,
      "passed": false,
      "method": "model",
      "evidence": "Only two numbered recommendations were present"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.5,
    "critical_failures": 0
  }
}
```

Require direct evidence for every pass. A heading or label without substantive content does not satisfy an assertion about that content.

## Mechanical and judgment-based grading

Use deterministic scripts for:

* file existence;
* parse validity;
* schema conformance;
* row or item counts;
* image dimensions;
* expected hashes;
* permitted paths;
* required filenames;
* bounded output sizes.

Use model judgment only when the quality cannot be checked mechanically, such as:

* organization;
* usability;
* explanation quality;
* relevance;
* visual hierarchy;
* decision usefulness.

When using a model judge, provide the outputs, assertions, and rubric. Require quoted or precisely referenced evidence.

For holistic comparisons, use blind review without identifying which output came from the candidate or baseline.

## Human review

Automated assertions only evaluate properties anticipated by the test designer. Human review should examine the actual outputs and identify:

* technically correct results that miss the user's real objective;
* awkward or unusable output structure;
* hidden assumptions;
* unexpected omissions;
* poor prioritization;
* visual or editorial defects;
* unnecessary work or complexity.

Record actionable feedback:

```json
{
  "output-001": "The recommendations are correct but are not prioritized by impact.",
  "output-002": ""
}
```

An empty value means no corrective feedback was identified.

Avoid feedback such as `looks bad` or `needs improvement`.

## Aggregating results

Aggregate candidate and baseline results separately:

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": 0.83,
      "duration_ms": 45000,
      "total_tokens": 3800
    },
    "baseline": {
      "pass_rate": 0.33,
      "duration_ms": 32000,
      "total_tokens": 2100
    },
    "delta": {
      "pass_rate": 0.5,
      "duration_ms": 13000,
      "total_tokens": 1700
    }
  }
}
```

Standard deviation is meaningful only after multiple runs per case. During early iterations, prioritize raw pass counts, critical failures, and candidate-versus-baseline deltas.

## Pattern analysis

After grading, inspect patterns hidden by the aggregate score:

| Pattern                                           | Interpretation                                         | Action                                           |
| ------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------ |
| Assertion passes in both configurations           | It may not measure skill value                         | Remove, replace, or demote it                    |
| Assertion fails in both configurations            | Case, assertion, or required capability may be invalid | Diagnose before revising the skill               |
| Candidate passes and baseline fails               | The skill is likely adding value                       | Identify the instruction or resource responsible |
| Results vary across repeated runs                 | Eval may be flaky or instructions ambiguous            | Tighten the case or instruction                  |
| One case consumes disproportionate time or tokens | Workflow may contain waste or a bottleneck             | Inspect its execution trace                      |
| Human feedback remains non-empty                  | Output is not yet reliably usable                      | Revise the responsible artifact                  |
| Added rules do not improve results                | Skill may be over-constrained                          | Remove or simplify instructions                  |

Do not allow easy assertions to inflate the apparent value of the skill.

## Iteration procedure

Use three evidence sources:

1. failed assertions;
2. human feedback;
3. execution traces.

Then:

1. identify the smallest responsible artifact;
2. generalize from the failure rather than patching one prompt;
3. revise the description, workflow, reference, script, adapter, or test;
4. keep instructions lean;
5. explain important reasoning where it improves compliance;
6. bundle repeated deterministic work only when it materially improves reliability;
7. create a new immutable iteration directory;
8. rerun the complete applicable evaluation set;
9. compare candidate, baseline, and previous iterations.

Do not overwrite previous iteration evidence.

## Script-extraction signal

Consider adding a tested helper under `scripts/` when execution traces show that multiple cases repeatedly recreate the same:

* parser;
* validator;
* chart builder;
* normalizer;
* schema checker;
* comparison routine.

Do not add a script merely because one could be written. The repeated work must be fragile, deterministic, or mechanically verifiable enough to justify maintenance and security cost.

## Acceptance conditions

A candidate output evaluation passes only when:

* every critical assertion passes;
* no baseline-critical behavior regresses;
* the candidate materially improves at least one outcome that the baseline does not already satisfy reliably;
* deterministic checks pass;
* human review confirms the result is usable;
* efficiency cost is justified by the measured benefit;
* generated evidence matches the evaluated skill version;
* limitations and unavailable metrics are explicit.

## Stop conditions

Stop iterating when:

* the candidate satisfies the acceptance conditions;
* human feedback is consistently empty;
* further changes produce no meaningful improvement;
* the baseline already performs sufficiently well;
* the necessary behavior cannot be enforced safely;
* the required runtime capability or observability is unavailable.

A skill should be rejected or deferred when its marginal value does not justify its context, execution, security, or maintenance cost.

## Source and authority notes

This reference summarizes the supplied Agent Skills guidance on output-quality evaluation.

Portable source guidance supplies the test-case model, candidate-versus-baseline comparison, isolated workspaces, timing capture, assertions, evidence-based grading, blind comparison, benchmarks, human feedback, pattern analysis, and iterative refinement.

Repository-specific test placement, critical assertions, abuse and compatibility evidence, packaging exclusions, acceptance gates, and release decisions remain governed by the repository's authoritative standards.
