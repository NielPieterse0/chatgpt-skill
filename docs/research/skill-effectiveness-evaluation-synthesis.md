# Skill Effectiveness Evaluation Synthesis

## Scope

This targeted review supports issue 029 / GitHub issue #49: turn the repository's existing skill-evaluation standard into deterministic, reviewable effectiveness evidence without making a model runner part of repository authority.

## Evidence reviewed

- Agent Skills evaluation guidance in `references/evaluating-skills.md`.
- Agent Skills trigger-description guidance in `references/optimising-skill-description.md`.
- Agent Skills creator guidance in `references/skills-best-practice.md`.
- Anthropic's vendored `skill-creator` implementation, especially trigger runs, benchmark aggregation, and evidence schemas.
- Repository authority in `docs/testing/skill-evaluation-standard.md` and `docs/standards/skill-authority-lifecycle.md`.
- KIS skill-telemetry contract from the linked `kis-mcp` change for issue #234.

## Source-supported findings

1. Output evaluation should compare the same task with the candidate skill and a baseline, using objective assertions plus human review.
2. Trigger evaluation needs realistic positive and near-miss cases, repeated runs, and a held-out validation set when descriptions are optimized.
3. Mechanical checks should be deterministic; model grading is appropriate only where mechanical verification is insufficient and must cite evidence.
4. Duration, tokens, tool calls, retries, and similar costs are useful only when actually observable; absent measurements must not be fabricated.
5. Benchmark aggregation is useful, but a single aggregate score can hide critical failures, variance, or baseline regressions.
6. Generated run evidence belongs outside the runtime skill package and should remain reproducible across iterations.

## Repository decisions

- Add one offline evaluator that validates tracked definitions plus generated result records and emits a per-skill scorecard.
- Do not embed a Claude, ChatGPT, Codex, or other model runner. Adapters or external execution workflows produce isolated-run evidence; the evaluator consumes it.
- Derive trigger pass/fail from the repository's category rules, not from a universal keyword threshold.
- Compare assertion reliability by configuration and identify material improvements and baseline-critical regressions explicitly.
- Represent each efficiency metric as observed or `not_observable`; zero is never used as a proxy for missing data.
- Treat verification, abuse, compatibility, human review, and rollback as separate gates.
- Import KIS telemetry only as a separate operational context: discovered, loaded, applied, completed, failed, resource-read, and cost-sample counts never alter the behavioral disposition.
- Emit `admit`, `revise`, or `defer` as a recommendation. Human authority retains `reject`, `suspend`, or final admission decisions.
- Surface production regressions as fixture candidates rather than silently adding or mutating evaluation definitions.

## Failure modes to prevent

- A high average pass rate masking one failed critical assertion.
- A candidate appearing better because baseline prompts, files, or assertions differed.
- Trigger optimization using held-out failures as training input.
- Missing token/tool metrics being represented as zero-cost execution.
- Operational load counts being mistaken for successful application or improved outcomes.
- Truncated telemetry being treated as complete history.
- A generated benchmark being copied into the runtime skill package.

## Implementation consequence

The harness should consume repository-owned definitions under `tests/skills/<skill>/` and generated evidence under `.work/evals/<skill>/iteration-<n>/`. Its output is a multi-dimensional scorecard and recommendation, not an opaque numeric score. This keeps the existing evaluation standard authoritative while making its gates executable.

## 2026-08-14 live cross-check

A final live cross-check against current public sources found no design reversal:

- Agent Skills still frames output evaluation around realistic tasks, candidate-versus-baseline runs, evidence-backed assertions, timing/cost capture, aggregation, and human review.
- Anthropic's current `skill-creator` still uses no-skill or previous-version baselines, isolated repeated runs, benchmark aggregation, and timing/token evidence.
- Anthropic's current trigger optimization still uses repeated activation trials and a held-out train/validation split rather than optimizing directly against every query.
- Anthropic's benchmark schema preserves per-configuration runs, deltas, variance, and notes rather than collapsing the result to one opaque quality number.

These sources reinforce the repository decision to keep execution adapters separate from deterministic evidence validation, preserve missing observations explicitly, and report multiple decision dimensions.
