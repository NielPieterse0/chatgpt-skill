# Agent Skills Compliance Audit Plan

## Authority and scope

Issue #58 is the source specification. This change audits the repository against the checked-in Agent Skills specification, client-support guidance, description-optimization guidance, evaluation guidance, script guidance, and creator best practices.

The audit is evidence, not a new policy authority. Existing repository owners remain authoritative for package, security, evaluation, lifecycle, and adapter rules.

## Outcome

Produce a machine-readable requirement-to-evidence matrix and concise audit report that separate normative format compliance from advisory best-practice conformance, register intentional repository restrictions, expose gaps, and make source/compliance drift detectable in normal verification.

## Implementation slices

1. Define the tracked compliance matrix with source fingerprints, stable requirement IDs, classifications, statuses, evidence, gaps, and justifications.
2. Add a deterministic compliance validator that rejects stale source fingerprints, unsupported compliant claims, missing evidence paths, malformed matrices, and normative failures.
3. Add package/resource checks that cover adopted skill line limits and referenced-resource resolution without duplicating `skill_security.py` authority.
4. Surface repository-wide compliance counts, source-freshness state, and audit age in the read-only workspace dashboard.
5. Fix the discovered cross-platform snapshot-byte regression by declaring immutable snapshot baselines as binary/no-conversion Git content, preserving their recorded Git blob hashes on Windows checkout.
6. Add focused tests first, verify each fails for the intended missing behavior, then implement the minimum code/control required to pass.
7. Publish the quantified audit report, run targeted checks and full repository verification, review the final diff, and close #58 only on exact-head passing evidence.

## Acceptance evidence

- Every matrix row has a stable ID, source/section, classification, repository control, evidence, status, gap, and remediation/justification.
- `compliant` rows cannot exist without resolvable repository evidence.
- Normative non-compliance or unevidenced normative requirements fail the compliance gate.
- Changes to any audited source snapshot invalidate its recorded fingerprint until re-audited.
- Dashboard output reports compliance counts and audit age without converting invalid/missing audit state to zero.
- Current adopted skills pass structural/resource checks; recommendations remain distinguishable from normative requirements.
- Windows checkout preserves immutable refresh-baseline bytes so recorded SHA-256 evidence is reproducible locally and in CI.
- `git diff --check`, focused tests, compliance validation, and `npm run verify` pass on the final exact state.

## Exclusions

This change does not alter the shared workspace catalogue, broaden runtime permissions, implement missing product-level activation observability, or claim behavioral evaluation evidence that the current target cannot observe.
