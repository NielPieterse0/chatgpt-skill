# Agent Skills Compliance Audit

**Audit date:** 2026-08-16
**Authority:** GitHub issue #58
**Machine-readable matrix:** [`agent-skills-compliance-matrix.json`](agent-skills-compliance-matrix.json)

## Executive verdict

The current repository-owned canonical skill packages satisfy all traced normative Agent Skills package requirements in the checked-in audit baseline: **8/8 normative requirements compliant (100%)**, with **0 normative failures, partials, or unevidenced claims**.

This is a package/repository-control verdict, not a claim that every target host behavior is observable or conformant. Client-side activation, permission allowlisting, context-compaction retention, and activation deduplication remain adapter/host concerns where current runtime evidence is incomplete.

Across all six audited source artefacts, the matrix traces **74 requirements or recommendations**. No row is marked compliant without repository evidence, and source fingerprints make the audit fail closed when its baseline changes.

## Quantified results

| Classification | Compliant | Partial | Non-compliant | Unevidenced | Intentional divergence | Not applicable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Normative | 8 | 0 | 0 | 0 | 0 | 0 | 8 |
| Recommended | 29 | 8 | 0 | 1 | 2 | 14 | 54 |
| Contextual | 3 | 1 | 0 | 4 | 3 | 1 | 12 |
| **Total** | **40** | **9** | **0** | **5** | **5** | **15** | **74** |

Current package checks cover both repository-owned adopted skills: **2 skills**, **0 unresolved local resource references**, and **0 `SKILL.md` files over 500 lines**.

## Source baseline

The audit uses the repository's checked-in snapshots as issue #58 requires:

- Agent Skills specification;
- client/support integration guidance;
- skill-description optimization guidance;
- output/effectiveness evaluation guidance;
- script usage guidance;
- skill-creator best practices.

The matrix records the SHA-256 of every audited source. A source change invalidates the stored audit until the matrix is deliberately reviewed and refreshed. These snapshots are research inputs; repository-owned standards remain the implementation authority after adoption.

## Strong controls

- Package identity, required frontmatter, naming, description length, optional portable metadata, body presence, provenance, and repository admission are deterministic and fail closed.
- Canonical skills use bounded progressive disclosure with relative supporting resources and remain below the recommended 500-line `SKILL.md` ceiling.
- Evaluation definitions separate trigger, output, abuse, compatibility, human review, rollback, and operational evidence; observed behavioral claims require explicit candidate/baseline evidence.
- Generated evaluation evidence remains outside runtime skill packages under `.work/evals`.
- Repository security is intentionally stricter than portable metadata: authorization, network access, dependency installation, and high-risk capabilities are not delegated to skill frontmatter.
- The workspace dashboard now reports compliant/partial/non-compliant/unevidenced counts, source-drift state, and audit age.

## Intentional divergences

The divergence register contains five explicit repository decisions. They are restrictions or scoped architecture choices, not misreported source requirements:

1. Reject experimental `allowed-tools` metadata at admission because portable metadata is not repository authorization.
2. Keep portable-core discovery to direct repository-owned skills; multi-scope host discovery belongs to runtime adapters.
3. Fail closed on malformed adopted `SKILL.md` instead of applying lenient client-compatibility repair.
4. Require a 16-case trigger minimum with explicit conflict and prompt-injection cohorts rather than copying the guide's approximate 20-query target.
5. Prohibit runtime dependency resolution and network installation at the current security baseline even though the script guide describes tools that can resolve dependencies dynamically.

## Evidence gaps and remediation priority

**Priority 1 — make description optimization mechanically auditable.** The repository standard calls for a fixed train/validation split, but trigger-case schema does not encode cohort membership. Add explicit split metadata when the activation runner is available so optimization uses training failures while held-out validation remains uncontaminated.

**Priority 1 — obtain target-host activation evidence.** The portable core cannot currently prove explicit user activation, resource permission allowlisting, context-compaction retention, or duplicate-activation behavior. Keep these claims unevidenced until a target adapter exposes reproducible traces; do not infer them from structural package validity.

**Priority 2 — strengthen evaluation mechanics.** Consider typed assertion methods for deterministic graders, automated detection of assertions that always pass/fail across candidate and baseline, a fresh unseen post-optimization trigger cohort, and transcript capture where the runner exposes execution traces.

**Priority 2 — upstream validator compatibility.** The repository validator covers the traced normative package constraints plus stricter local policy. A pinned `skills-ref` compatibility check would provide independent format confirmation, but it should only become a gate when it can run reproducibly without weakening the repository's dependency-installation policy.

Script-specific recommendations are currently not applicable because neither repository-owned adopted skill contains a `scripts/` directory. Admission of the first script-bearing skill is a mandatory re-audit trigger.

## Continuous compliance

`python scripts/skill_compliance.py validate --repo .` validates the matrix, source fingerprints, evidence paths, normative gate, divergence registration, current package references, and `SKILL.md` line ceilings. `npm run verify` invokes this gate directly and the unit suite tests its failure behavior.

The audit must be rerun at least every **90 days**, and immediately when an audited source hash changes, the specification/source register is refreshed, package/discovery rules change, evaluation contracts change, a script-bearing canonical skill is proposed, or a runtime adapter changes activation/resource/permission/context behavior.

Immutable catalogue-update baselines are byte-addressed evidence. `.gitattributes` disables text conversion beneath `references/catalogue-update-baselines/**`, making recorded SHA-256 manifests reproducible across Windows and Linux checkouts rather than dependent on host EOL settings.

## Completion evidence

Closeout requires the matrix validator, targeted compliance/dashboard/snapshot tests, repository-wide `npm run verify`, and `git diff --check` to pass on the exact delivered revision. Any failure invalidates this verdict until corrected or explicitly reclassified in the matrix.
