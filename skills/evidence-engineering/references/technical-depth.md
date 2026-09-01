# Technical Depth

## Core concerns
- requirement to observable acceptance mapping
- domain invariants and system behaviors
- fail-before and pass-after causality
- lowest appropriate test level
- contract boundary and integration evidence
- logs state snapshots metrics and traces
- focused versus broad regression verification
- freshness provenance and completion-proof chain

## Method
- rewrite each requirement as an observable falsifiable criterion
- identify the owning boundary and invariant
- select the lowest test level that can prove the behavior without mocking it away
- capture a credible failing-before state for regressions or new behavior where applicable
- capture passing-after evidence on the same assertion
- add boundary contract or integration checks only where risk crosses seams
- run focused checks first then broader repository gates
- report unsupported claims unavailable evidence and residual uncertainty

## Failure modes to challenge
- screenshots used for non-visual state claims
- tests that pass before the fix and prove nothing
- mock-heavy tests that bypass the changed boundary
- coverage percentage treated as correctness
- fresh code changes paired with stale verification
- only happy-path evidence for failure-sensitive behavior
- claiming broad safety from one focused test
- completion status inferred from confidence rather than evidence

## Verification questions
- each material requirement has an evidence owner and observable
- regression fixes demonstrate fail-before/pass-after when feasible
- test level is justified against the behavior boundary
- critical external contracts have boundary evidence
- focused tests target the exact change
- broader checks address plausible regression radius
- evidence timestamps or revisions match current code
- completion report separates verified unverified and not-applicable claims

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
