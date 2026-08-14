# Shared Skill Authority Lifecycle

## Authority

This document owns the lifecycle composition for shared skill creation, evaluation,
improvement, admission, maintenance, suspension, and rollback. It does not duplicate
the detailed rules owned by the package, evaluation, security, or runtime-adapter
standards.

Apply the existing owners in this order for their domains:

- package shape and progressive disclosure: `skill-package-standard.md`;
- behavioral and release evidence: `../testing/skill-evaluation-standard.md`;
- provenance, capability tiers, admission, disablement, and rollback:
  `../security/skill-adoption-security-standard.md`;
- target-specific packaging and runtime behavior:
  `../architecture/skill-runtime-adapters.md`.

The shared Projects workspace catalogue is a delivery surface, not repository policy.
Repository-owned standards remain authoritative when a shared skill is revised for
this project.

## Lifecycle states

1. **Create** — establish one reusable outcome, package boundary, activation contract,
   baseline, and evaluation definitions using `create-skill`.
2. **Evaluate** — assess structural/admission integrity, activation, output value,
   efficiency, abuse resistance, compatibility, human review, and rollback using
   `evaluate-skill` and repository evaluation authority.
3. **Improve** — apply the smallest evidence-backed correction using `improve-skill`,
   preserving baseline and held-out evaluation integrity.
4. **Verify / decide** — use evidence to admit, revise, defer, reject, or suspend.
   No single successful run is release evidence.
5. **Deliver** — mutate or package the approved catalogue artifact through the
   governed workspace/runtime path; catalogue presence does not imply repository
   runtime enablement.
6. **Maintain** — rerun affected regression cases after material skill, reference,
   script, adapter, policy, or target-runtime changes.
7. **Suspend / rollback** — disable first on integrity, security, compatibility, or
   quality uncertainty; preserve evidence and require re-evaluation before return.

## Required handoffs

Create → evaluate must carry the skill identity, baseline, intended outcome,
activation boundaries, eval definitions, capability/runtime assumptions, and known
limitations.

Evaluate → improve must carry failed or weak assertions, held-out set identity,
human feedback, abuse/compatibility evidence, unavailable metrics, residual risks,
and the current lifecycle decision.

Improve → evaluate must carry changed artifacts, before/after identities or hashes,
rationale tied to findings, unchanged held-out identity, and the checks that require
re-execution.

Evaluate → admit/deliver must carry all applicable passing critical gates,
provenance/license/integrity evidence, approval, target compatibility, and verified
rollback. Missing observability is a limitation, never an inferred pass.
## Cross-skill invariants

The shared `create-skill`, `evaluate-skill`, and `improve-skill` entrypoints must:

- defer to governing repository/workspace authority;
- keep package creation, activation evaluation, and output evaluation distinct;
- keep evaluation definitions and generated evidence outside the runtime package;
- preserve a baseline and held-out activation cases during optimization;
- treat abuse, compatibility, provenance, observability, and rollback as explicit
  gates or explicit limitations;
- avoid mandatory dependence on optional third-party evaluators;
- avoid treating metadata, catalogue presence, or a successful refresh as tool or
  runtime authorization;
- use progressive disclosure and bounded, non-interactive scripts when scripts are
  justified;
- stop rather than invent evidence or bypass unavailable governance controls.

`config/skill-lifecycle-contract.json` is the machine-readable projection of these
entrypoint invariants. `scripts/skill_lifecycle.py` validates a supplied catalogue
root against that projection without making the shared catalogue a CI dependency.

## End-to-end proof

For a release or material lifecycle change:

1. run repository-wide verification with the runtime kill switch unchanged;
2. run the lifecycle contract validator against the intended shared catalogue root;
3. use KIS `evaluate_skill` for the three lifecycle entrypoints and refresh the
   catalogue after an approved mutation;
4. exercise one realistic create → evaluate → improve → re-evaluate flow;
5. record unavailable target activation/runtime observability rather than claiming
   it passed;
6. verify disablement/rollback remains available before closing the lifecycle work.

## Completion

The lifecycle is coherent only when all material findings are resolved or owned by
bounded follow-ups, the three shared entrypoints satisfy the machine-readable
contract, repository validation passes, the catalogue refresh is evidenced, and no
runtime enablement is inferred from catalogue maintenance.
