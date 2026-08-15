# Top-Five Skill Evaluation - Issue #54

## Authority

- Execution scope: GitHub issue `#54`.
- Research basis: [`docs/research/skill-adoption-research-synthesis.md`](../research/skill-adoption-research-synthesis.md).
- Evaluation semantics: [`skill-evaluation-standard.md`](skill-evaluation-standard.md).
- Fail-closed evaluator: `scripts/skill_effectiveness.py`.

Issue `#54` is the bounded execution specification for this evidence-only change; no new behavior, lifecycle rule, shared schema, or runtime contract is introduced.

## Scope

Lane A evaluates the five most-used active canonical workspace skills. This change records evaluation evidence only. It does not modify canonical skill content, adoption manifests, lifecycle/evaluation standards, dashboard schemas, `AGENTS.md`, backlog/board authority, or other implementation lanes.

Repository baseline: `eaba5d994d8c0cc7432333d19a2c8f08e9587bad`. Canonical workspace: `C:\Projects\.agents\skills`. KIS catalogue snapshot: `c4ada48dff958cd9`.

## Cohort selection

The strongest available KIS `skill_telemetry_report` contained `20000` events with `truncated: false`. Ranking uses aggregate `loaded_count` as the primary actual-usage signal, then resource reads, completions, and evaluations. Catalogue `discovered_count` is retained in evidence but is not treated as use.

| Rank | Skill | Loads | Resource reads | Static package | Recommendation |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | `develop-code` | 24 | 20 | pass | defer |
| 2 | `kis-mcp` | 21 | 25 | pass | defer |
| 3 | `develop-docs` | 10 | 7 | pass | defer |
| 4 | `time-series-research` | 9 | 0 | pass | defer |
| 5 | `reproducibility-auditor` | 8 | 0 | pass | defer |

`reproducibility-auditor` and `statistical-analyst` tied at eight loads and were also equal on all actual-usage secondary fields. The documented final tie-break is canonical `skill_id` ascending, so `reproducibility-auditor` is rank 5. Discovery counts did not break the tie.

## Evaluation result

All five recommendations are **`defer`**. KIS can read and statically evaluate every selected package, and the basic Agent Skills structure checks passed. Behavioral effectiveness cannot be credibly scored on the current execution surface because no isolated skill-vs-baseline runner with activation observability is exposed, and human review has not occurred.

The repository harness also fails closed before behavioral scoring for the current canonical candidates:

- `develop-code`: harness exit `2` - `evaluation record runtime content hash mismatch`
- `kis-mcp`: harness exit `2` - `cannot resolve evaluation definition tests\skills\kis-mcp\trigger-cases.json at eaba5d994d8c0cc7432333d19a2c8f08e9587bad: fatal: path 'tests/skills/kis-mcp/trigger-cases.json' does not exist in 'eaba5d994d8c0cc7432333d19a2c8f08e9587bad'`
- `develop-docs`: harness exit `2` - `evaluation record runtime content hash mismatch`
- `time-series-research`: harness exit `2` - `cannot resolve evaluation definition tests\skills\time-series-research\trigger-cases.json at eaba5d994d8c0cc7432333d19a2c8f08e9587bad: fatal: path 'tests/skills/time-series-research/trigger-cases.json' does not exist in 'eaba5d994d8c0cc7432333d19a2c8f08e9587bad'`
- `reproducibility-auditor`: harness exit `2` - `cannot resolve evaluation definition tests\skills\reproducibility-auditor\trigger-cases.json at eaba5d994d8c0cc7432333d19a2c8f08e9587bad: fatal: path 'tests/skills/reproducibility-auditor/trigger-cases.json' does not exist in 'eaba5d994d8c0cc7432333d19a2c8f08e9587bad'`

The two repo-adopted skills have semantic runtime drift from the canonical workspace candidates:

- `develop-code`: canonical runtime SHA-256 `10ab0e8457b53d1940d27cb70ac3a96d0088636e7c5437a17fc769c68d4a5288`; current repo runtime differs.
- `develop-docs`: canonical runtime SHA-256 `17791b4232a3bb002ebfb5fc993636691a85a9c6574d7c210f9fc1912cc23a0c`; current repo runtime differs.

`kis-mcp`, `time-series-research`, and `reproducibility-auditor` are active in the canonical workspace but have neither a repo adoption identity nor immutable tracked evaluation definitions in this repository. Creating or synchronizing those lifecycle artifacts is intentionally outside issue #54's evidence-only lane.

## Dimension status

For every cohort member:

- trigger boundaries: `not_observable` on the current isolated-run surface;
- candidate-vs-baseline output quality: `not_observable`;
- abuse/security execution: `not_observable` (static package checks only);
- runtime compatibility: `pass` for catalogue activation/readability and KIS static evaluation;
- efficiency: `partial` from operational telemetry only; no isolated-run token/tool/time comparison;
- human review: `pending`;
- critical behavioral regression assessment: `not_assessable`, not a pass.

Operational telemetry is treated as exposure/context evidence only and does not change an effectiveness disposition.

## Evidence

Generated evidence is under ignored runtime paths:

- `.work/evals/top-five-selection.json`
- `.work/evals/<skill>/iteration-1/evaluation-record.json`
- `.work/evals/<skill>/iteration-1/harness-attempt-record.json`
- `.work/evals/<skill>/iteration-1/harness-attempt.txt`

The tracked machine-readable summary is [`top-five-skill-evaluation.json`](top-five-skill-evaluation.json).

## Follow-on evaluation order

1. In separate governed lifecycle changes, bind/synchronize the current canonical `develop-code` and `develop-docs` candidates to valid repo evaluation identities.
2. Establish repo evaluation identities and immutable tracked definitions for `kis-mcp`, `time-series-research`, and `reproducibility-auditor` before behavioral reruns.
3. When an isolated candidate-vs-baseline runner and human review are available, rerun the same top-five cohort before making any `admit` or `revise` decision.

No aggregate score is used to hide missing critical evidence. No behavioral regression is claimed absent merely because none could be observed.
