# Technical Depth

## Core concerns
- hallucinated libraries methods flags and configuration
- authorization and tenant-boundary omissions
- input validation injection and unsafe parsing
- error swallowing fallback and fabricated success
- dependency provenance versions and insecure defaults
- secret logging telemetry and data leakage
- concurrency resource cleanup and cancellation
- test adequacy for generated assumptions

## Method
- verify unfamiliar APIs against installed code or authoritative docs
- trace every security-sensitive operation to authorization enforcement
- inspect parsing serialization templating and command construction
- look for broad exception handling silent fallback and fake success states
- check dependency additions and configuration for provenance and necessity
- identify copied patterns that bypass repository conventions
- require tests that fail when the suspected omission exists
- separate AI-origin suspicion from evidence-backed defect findings

## Failure modes to challenge
- treating AI authorship itself as a defect
- assuming plausible API names exist
- reviewing comments instead of executed behavior
- missing indirect authorization through shared helpers
- accepting catch-all fallback that hides failed writes
- adding dependencies to solve trivial logic
- tests generated with same mistaken assumption as code
- security claims without reachability or trust-boundary evidence

## Verification questions
- all unfamiliar external calls are verified or flagged
- security-sensitive paths have explicit authz evidence
- user-controlled data has sink-aware validation
- failure handling cannot silently claim success
- new dependencies are justified and pinned by repository policy
- secrets and sensitive data do not enter unsafe logs
- tests challenge rather than repeat generated assumptions
- findings distinguish confirmed defect uncertainty and follow-up verification

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
