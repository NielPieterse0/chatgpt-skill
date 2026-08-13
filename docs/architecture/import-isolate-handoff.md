# Import-Isolate Handoff Boundary

## Authority

This document defines the responsibility boundary between this repository and the separate `import-isolate` repository for candidate material acquired from external web sources, including GitHub.

This document defines only the interface into this repository. All external acquisition, isolation, inspection, cleanup, security review, semantic review, and neutralization are owned by `import-isolate` and are out of scope here. Skill admission, runtime evaluation, enablement, and rollback remain governed by [`docs/security/skill-adoption-security-standard.md`](../security/skill-adoption-security-standard.md).

## Responsibility Split

`import-isolate` owns the complete external-source intake lifecycle through a finalized checked, verified, semantically reviewed, and neutralized handoff.

This repository starts only after that finalized handoff is received. It owns skill selection, repository-specific adaptation, canonical admission, evaluation, packaging, activation decisions, maintenance, disablement, and rollback.

This repository must not reproduce, implement, or govern `import-isolate` internals. When new or updated web-sourced material is needed, request a new finalized handoff from `import-isolate`.

Local repository-owned sources and explicitly trusted local workspace material remain outside this external-source handoff boundary unless the repository owner directs otherwise.

## Handoff Contract

Accept only a finalized handoff intended for downstream use. An intermediate `import-isolate` state that still requires semantic or security review is not a valid input to this repository.

The handoff must provide enough machine-readable provenance and integrity identity to bind the received artifact to its source and to the exact handed-over content. This repository records `source.provenance_type`, and for `import-isolate` handoffs it records `source.handoff.case_id`, `source.handoff.artifact`, and `source.handoff.artifact_sha256`. The handed-over artifact digest is independent of `source.adopted_content_sha256`, which fingerprints the repository-owned adopted skill after adaptation. The internal evidence and process used to establish the upstream result remain authoritative in `import-isolate` and are not duplicated here.

If the handoff is incomplete, inconsistent, or not finalized, stop and request a corrected handoff from `import-isolate`.

## Trust Semantics

A finalized handoff is accepted as checked, verified, semantically reviewed, and neutralized source input. It is still not repository-owned runtime content until this repository completes its own skill-specific adaptation, admission, evaluation, and approval.

Receipt of a handoff does not authorize installation or activation. Those decisions remain subject to this repository's admission and runtime controls.

## Legacy Material

Material already present under `references/` before this responsibility split is grandfathered only as inert, non-authoritative source evidence. Its presence does not assert that `import-isolate` processed, verified, semantically reviewed, or neutralized it.

Legacy material may remain for historical comparison, provenance, or reconstruction while repository security rules keep it non-executable and outside runtime discovery. If new adoption or release work materially relies on a legacy external source and a finalized `import-isolate` handoff cannot be demonstrated, request a new upstream handoff before using that source as current evidence.

Deletion, archival reduction, or structural cleanup of legacy material is separate repository work and must not be mixed into this boundary change.
