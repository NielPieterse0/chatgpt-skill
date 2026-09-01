# Technical Depth

## Core concerns
- behavioral ownership and change seam
- public and internal compatibility
- blast-radius analysis
- dependency and caller impact
- data and migration compatibility
- feature flags and incremental rollout
- targeted tests around changed behavior
- refactor separation and rollback simplicity

## Method
- state the exact required behavior and exclusions
- locate the narrowest owner of that behavior
- trace callers contracts and side effects before editing
- prefer a local seam over cross-cutting redesign when both satisfy the requirement
- avoid opportunistic cleanup in the same change
- add the smallest test that fails for the missing behavior
- verify adjacent callers and contracts
- broaden only when evidence proves the local seam cannot be correct

## Failure modes to challenge
- tiny diff optimized for line count while violating ownership
- duplicating logic to avoid touching the correct abstraction
- mixing refactor and behavior change without necessity
- changing public contract for internal convenience
- ignoring migration or serialized-data compatibility
- fixing symptom at caller instead of invariant owner
- removing validation to make tests pass
- under-testing because the patch looks small

## Verification questions
- scope maps exactly to requirement and necessary dependencies
- existing public semantics are unchanged unless explicitly required
- new test would fail on old behavior
- adjacent callers remain valid
- no unrelated cleanup is included
- data format migration impact is assessed
- rollback is localized and understandable
- diff review can explain every changed line

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
