# Skill Effectiveness Evaluation Implementation Plan

## Objective

Implement the missing deterministic evaluation harness for issue 029 / #49 without changing the repository's existing evaluation policy or runtime admission authority.

## Design

1. Add `scripts/skill_effectiveness.py` as an offline evidence validator and scorecard generator.
2. Load tracked `trigger-cases.json`, `output-evals.json`, and `abuse-cases.json` for one canonical skill.
3. Validate one generated evaluation record against those definitions using strict field and ID checks.
4. Calculate trigger boundary results using the category-specific rules already defined by the evaluation standard.
5. Compare candidate and baseline assertion reliability; expose critical failures, material improvements, and baseline regressions.
6. Preserve observed efficiency values and explicit `not_observable` reasons without inventing zeros.
7. Keep verification, abuse, compatibility, human-review, and rollback gates independent.
8. Optionally ingest a KIS `SkillTelemetryReport` as non-causal operational context.
9. Emit a versioned per-skill JSON scorecard with a recommended disposition of `admit`, `revise`, or `defer`.
10. Return production-regression entries as fixture candidates without editing tracked eval definitions.

## Boundaries

- No model execution or provider SDK dependency.
- No mutation of skills, shared catalogue, Project state, or runtime configuration.
- No generated evidence committed beneath `skills/`.
- No single composite quality score.
- No final admission, rejection, or suspension decision made by the script.

## Tests first

Add unit tests covering:

- a fully passing observed record recommends `admit`;
- unavailable trigger or compatibility evidence recommends `defer` without inventing pass/fail data;
- a failed critical assertion or abuse case recommends `revise`;
- baseline-critical regression is surfaced even when aggregate candidate pass rate is high;
- metric `0` remains an observed zero while missing metrics require `not_observable` reasons;
- KIS telemetry is filtered to the requested skill/version, preserves truncation, and cannot change the behavioral recommendation;
- unknown fields, missing definition IDs, and mismatched skill/version identities fail closed;
- production regressions appear only as fixture candidates.

## Verification

Run targeted evaluator tests first, then `npm run verify`, `git diff --check`, and final change review. Generated end-to-end sample evidence stays under `.work/` and must not be committed.
