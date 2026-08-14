# KIS-Governed GitHub Skill Pack Evaluation

## Status

Evaluation evidence for Change 019 / implementation Changes 021–024, captured 2026-08-14.

The evaluated runtime target is the canonical Projects workspace catalogue at `C:\Projects\.agents\skills`. These skills are not admitted into this repository's P0 `skills/` runtime.

## Candidate pack

| Skill | Active entrypoint SHA-256 | Package files | Role |
|---|---|---:|---|
| `github` | `cb558cd7dbe6723f4d709441ed62c7f8452cbf95b21114c398dda5930ce97b8e` | 1 | General GitHub triage/router |
| `github-pr-maintenance` | `da26f56c96dbee64b1a5c3ba0a59df11474c66e955d6d3f8b658299589fdbcd1` | 1 | Existing-PR feedback/CI/base/conflict maintenance |
| `github-delivery` | `2a0f0de89bee8bd7fcafdac3c8b547f38a6c3ffb202e5eeecc1f5bff9cb2e1ab` | 1 | Governed publication, PR lifecycle, landing, reconciliation, cleanup |

KIS `refresh_skills` produced snapshot `d84373bc753c6d7f` with 28 active canonical skills. Structural `evaluate_skill` succeeded for all three candidates on that exact snapshot.

## Baseline evidence

Before catalogue mutation, KIS structural evidence was captured at snapshot `083d073aa34c7dd5` for the prior GitHub-related workflow sources:

- `github`: `81dbdd90934fe86a79ddc4790fd211e5fca866302a74090ad153395f56f2bd42`
- `gh-address-comments`: `c1ebc337357402f7faabafe712e0c463981a65f736453efe52abd305bcb74769`
- `gh-review-comment-triage`: `effcaa0580cd882e68e0e8d947ef0de24951748ed31d5f5eb2e57ff9afbfb5d1`
- `gh-fix-ci`: `7621a3560d788fb221d25f9753233fe0c393c5cfe63167c88b11f027c277b1f8`
- `yeet`: `e93c6ea769ba673d30749a981cd8ad75b687f454e3c8e2e45e7cfcbd412df12c`
- `take-pr-to-completion`: `772bd454fb9f0cd4cd32b1a4aa39e3d32ea9625af4875d8d3c6af2eb68557836`
- `commit-workspace-changes`: `d5939c5a1964da66b73eba615ca12097d716e9f9f79903f10f54998d8a6953fc`

Those baseline records were available through the running KIS capability/skill composition but the corresponding superseded packages were not present in the canonical shared root by final refresh. The new canonical `github` package was therefore created rather than mutating an upstream/plugin-owned file.
## Trigger and abuse definitions

Repository-owned definitions now exist under:

- `tests/skills/github/`
- `tests/skills/github-pr-maintenance/`
- `tests/skills/github-delivery/`

For each skill, the suite contains:

- 6 positive trigger cases;
- 6 near-miss cases;
- 2 adjacent-workflow conflict cases;
- 2 prompt-injection cases;
- 3 representative output/workflow cases;
- 8 abuse-boundary cases.

A local structural check parsed every JSON file, verified the case counts, verified skill/frontmatter name identity, and verified all three descriptions are within the 1,024-character portable limit. Result: `STATIC_EVAL_DEFINITIONS_OK`.

The cases specifically test routing separation, stale-head evidence, Work Management/source authority, provider bypass attempts, unsupported review-thread resolution, merge-queue candidate freshness, false completion, and destructive cleanup boundaries.

## Static workflow review

### `github`

**Pass for design boundary.** General repository/issue/PR triage remains in the umbrella. Existing-PR repair and delivery outcomes are explicitly routed to the two specialists. Generic implementation/review stays with `code-work`, `code-review`, or `code-verification`. Raw `gh`/GraphQL bypasses and invented KIS registration are prohibited.

### `github-pr-maintenance`

**Pass for design boundary.** The skill resolves exact PR head identity, classifies feedback before editing, uses exact-head CI evidence, delegates code and semantic conflict work, and cannot land/publish. Review-thread resolution fails closed when no approved live operation exists.

### `github-delivery`

**Pass for design boundary.** The skill owns the full delivery outcome while delegating mechanics to live KIS workflows. It preserves exact-head evidence freshness, live Work Management authority, complexity/risk-trigger governance, merge-vs-queue policy, post-merge reconciliation, and recoverable cleanup gates.

These are instruction-contract reviews, not measured model-activation precision or isolated candidate-vs-baseline execution scores.
## Runtime compatibility findings

### Canonical Skills snapshot

**Pass.** After explicit atomic refresh, all three candidate skills are active and structurally evaluable in KIS snapshot `d84373bc753c6d7f`. A canonical-root content search found no references to `gh-address-comments`, `gh-review-comment-triage`, `gh-fix-ci`, `yeet`, `take-pr-to-completion`, or `commit-workspace-changes`.

No permanent deletion was performed during this change because the superseded packages were already absent from the canonical shared root when final retirement was reconciled.

### Capability-discovery split-brain

**Fail — KIS defect, not a skill-package defect.** `search_capabilities` still advertises removed skill contributions such as `skill.gh-address-comments`, `skill.gh-review-comment-triage`, `skill.gh-fix-ci`, `skill.yeet`, `skill.take-pr-to-completion`, and `skill.commit-workspace-changes` as ready even though the active Skills snapshot cannot load those packages.

This was registered in `NielPieterse0/kis-mcp` as issue #183, **Defect: Skills capability registry remains stale after catalogue refresh**, and linked beneath Change 024 / issue #36. Do not restore obsolete packages or add duplicate private metadata as a workaround.

The new specialists intentionally use portable `name`/`description` frontmatter only. They therefore remain uncategorized with no private KIS capability tags until the portable metadata/adapter decision owned by Change 020 is resolved.

## Evaluation limitations

- The current environment does not expose an isolated automatic skill-activation scoring harness, so trigger precision/recall is **unmeasured**. The trigger files are executable definitions for a future harness, not claimed measurements.
- The `plugin-eval` CLI previously used by the evaluation skill is not installed in this environment, so no plugin-eval benchmark or token-cost score is claimed.
- Representative output cases were reviewed against the skill instruction contracts; they were not run as repeated independent model executions against a no-skill baseline. Therefore no quantitative quality delta is claimed.

## Release assessment

The three-skill pack is structurally valid, materially smaller than the superseded workflow surface, aligned to current KIS registered GitHub workflows, and has explicit trigger/output/abuse regression definitions. It is suitable to remain active in the canonical Projects catalogue **with one recorded KIS runtime limitation**: stale skill-derived capability contributions can still misroute capability search until kis-mcp #183 is fixed or the runtime is proven to reconcile them after restart.

The repository P0 admission boundary remains unchanged.