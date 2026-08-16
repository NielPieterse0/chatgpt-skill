# Full Catalogue Evaluation Closeout Plan

## Authority and scope

GitHub issue #55 is the source specification. The canonical population is the active Projects workspace catalogue at `C:\Projects\.agents\skills`.

This change closes the programme without inventing behavioral effectiveness. Issue #55 explicitly permits a current reviewable evaluation record **or an explicit governed defer/suspend reason** for every active skill. The current target still lacks the isolated candidate-vs-baseline execution and activation observability required for credible behavioral scoring, so the programme can reach 100% current coverage through per-skill structural evidence plus explicit `defer` decisions.

Generated run evidence remains under `.work/evals/`. The durable programme decision is a tracked machine-readable summary under `docs/testing/`, following the precedent established by issue #54.

## Current defect to correct

The dashboard currently reads only recognized generated scorecards under `.work/evals`, so the tracked #54 top-five defer summary is invisible and reports 0% coverage. It also includes stale evaluations in the coverage numerator, which conflicts with #55's requirement for current coverage.

## Implementation slices

1. Add tests proving tracked current-hash programme defer records contribute to coverage, stale programme records do not, malformed tracked records fail closed, and stale evaluations are excluded from the current-coverage numerator.
2. Add a strict tracked programme-evidence contract for `docs/testing/full-catalogue-skill-evaluation.json` and make repository evidence prefer a valid current generated scorecard, then a valid current tracked programme decision, while preserving stale warnings.
3. Add a deterministic generator/validator that snapshots every active canonical skill, records its content hash and bounded structural package evidence, classifies repository adoption/evaluation-definition availability, and emits an explicit defer reason without fabricating trigger/output/abuse/human-review results.
4. Generate the issue #55 snapshot for the current 38-skill catalogue. Preserve issue #54 as historical richer evidence for its original cohort; do not rewrite or delete it.
5. Add a concise tracked closeout report documenting coverage, global behavioral limitations, ownership, re-evaluation triggers, and the fact that `defer` is not an effectiveness pass.
6. Verify the dashboard against the live canonical catalogue shows 38/38 current covered records and 100% coverage, all as governed defers unless stronger current generated evidence exists.
7. Run focused tests, record validation against the live catalogue, `git diff --check`, full `npm run verify`, exact-head provider CI, merge, and post-merge reconciliation.

## Gates

- No shared-catalogue mutation.
- No skill is marked `admit` or `revise` without the full behavioral/human evidence required by the evaluation standard.
- A programme record counts only when its recorded runtime hash exactly matches the current canonical `SKILL.md` hash.
- A malformed or internally inconsistent programme summary contributes no coverage.
- Stale records remain visible but are excluded from current coverage.
- Any canonical skill hash change, catalogue membership/status change, new isolated runner/activation observability, completed human review, adapter/runtime change, significant regression, or evidence-age expiry triggers re-evaluation.
- Programme ownership remains with this repository's evaluation lifecycle; telemetry is context only and cannot change disposition.
