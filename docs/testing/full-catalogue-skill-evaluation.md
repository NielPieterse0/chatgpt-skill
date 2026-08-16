# Full Workspace Skill Catalogue Evaluation — Issue #55

## Authority

- Programme issue: GitHub `#55`.
- Canonical population: `C:\Projects\.agents\skills`.
- Evaluation semantics: [`skill-evaluation-standard.md`](skill-evaluation-standard.md).
- Machine-readable programme record: [`full-catalogue-skill-evaluation.json`](full-catalogue-skill-evaluation.json).
- Historical critical cohort evidence: [`top-five-skill-evaluation.md`](top-five-skill-evaluation.md).

This closeout records **coverage and governed deferral**, not successful behavioral effectiveness. No shared-catalogue skill content was changed.

## Current coverage

On 2026-08-16 the canonical workspace catalogue contained **38 active skills**. The tracked programme record binds all 38 to their exact current `SKILL.md` SHA-256 and records bounded structural package evidence for each.

| Metric | Result |
|---|---:|
| Active canonical skills | 38 |
| Current covered records | 38 |
| Current coverage | 100% |
| Admit | 0 |
| Revise | 0 |
| Defer | 38 |
| Suspend | 0 |
| Stale programme records | 0 |

All 38 dispositions are **`defer`**. A defer means the skill was assessed and the repository has an explicit reason why a credible effectiveness decision cannot yet be made. It is not an effectiveness pass and does not authorize repository runtime admission, target installation, activation, or mutation of the canonical workspace package.

## Structural and lifecycle evidence

All 38 active entries passed the bounded structural snapshot required by this programme: valid catalogue identity/frontmatter, exact `SKILL.md` hash, readable package files, and no symlinked package content observed by the generator.

Current lifecycle gaps are explicit:

- **11** skills have all three tracked evaluation definition files (`trigger-cases.json`, `output-evals.json`, `abuse-cases.json`).
- **27** skills have no complete tracked definition set in this repository.
- **36** canonical workspace skills have no approved repository adoption identity.
- `develop-code` and `develop-docs` have approved repository adoption records, but those recorded adopted identities differ from the current canonical workspace hashes.
- Four issue #54 cohort records still match the current canonical hash: `develop-code`, `develop-docs`, `time-series-research`, and `reproducibility-auditor`.
- `kis-mcp` changed hash after issue #54, so the historical #54 evidence is retained but marked stale relative to the current canonical candidate.

The full machine-readable record preserves the exact per-skill states and blocker list.

## Why the programme defers all current skills

Three evidence gates remain globally unavailable or incomplete on the current target surface:

1. no repository-controlled isolated candidate-vs-baseline execution runner is available for the whole catalogue;
2. reliable automatic/explicit activation observability is not available for the whole catalogue;
3. required human output review has not been completed for catalogue-wide behavioral decisions.

Per-skill blockers additionally record missing/incomplete tracked definitions, missing or stale repository adoption identity, and stale #54 evidence where applicable.

The repository therefore does not synthesize trigger precision, output improvement, abuse resistance, efficiency, or human-review passes from structural validity or KIS usage telemetry. Operational telemetry remains context only.

## Risk and sequencing

The programme did not skip the risk-first requirement. The highest-use critical cohort was evaluated first under issue #54 using the strongest non-truncated KIS usage evidence available at that point. The remaining active catalogue was then assessed after the shared evaluation harness and dashboard existed.

Once the full-catalogue pass reached the same global behavioral blocker for every remaining skill, further usage/risk ordering could not change the release disposition: no skill could legitimately advance to `admit` or `revise`. The programme therefore completed the remaining structural/defer pass in one bounded snapshot rather than fabricating finer-grained risk scores that had no decision effect.

Future behavioral execution should resume risk-first when the blocking execution/observability surface exists, using current high-risk/high-usage evidence rather than this defer snapshot as a substitute.

## Dashboard semantics

The dashboard now consumes two evidence layers:

1. a valid current generated per-skill scorecard under `.work/evals/<skill>/...` when available;
2. otherwise, the strict tracked programme `defer`/`suspend` record when its hash matches the current canonical skill and its evidence age is current.

Generated scorecards are stronger evidence and take precedence. A programme record with a mismatched canonical hash or expired evidence is shown as `stale` and is **excluded** from current coverage. Malformed programme records contribute no coverage.

The live closeout read against `C:\Projects\.agents\skills` reports:

- `total_catalogue_count = 38`;
- `active_count = 38`;
- `repo_evaluated_count = 38`;
- `unevaluated_count = 0`;
- `evaluation_coverage = 1.0`;
- `defer_count = 38`;
- `stale_evaluation_count = 0`.

## Re-evaluation ownership and triggers

Owner: **chatgpt-skill evaluation programme**.

The tracked programme evidence has a maximum age of **90 days**. Re-evaluation is triggered earlier when:

- any canonical skill `SKILL.md` hash changes;
- catalogue membership or active status changes;
- isolated candidate-vs-baseline execution becomes available;
- reliable activation observability becomes available;
- human review is completed;
- runtime adapter or target behavior materially changes;
- security, quality, or operational regression evidence appears.

The dashboard compares hashes on every live read, and `scripts/catalogue_evaluation.py validate` can additionally compare the tracked snapshot against the live canonical catalogue. `npm run verify` validates the tracked record contract and expiry even when the external workspace catalogue is unavailable to CI.

## Closeout decision

Issue #55's programme completion criteria are satisfied for **coverage governance**: every current active canonical workspace skill has a current reviewable hash-bound record with an explicit governed defer reason, 100% current coverage is visible in the dashboard, ownership and re-evaluation triggers are defined, and the snapshot is reproducible/validatable from repository plus live catalogue evidence.

The programme does **not** claim that any of the 38 skills has passed behavioral effectiveness. Those future evaluations must produce the normal per-skill evidence before any `admit` or `revise` decision.
