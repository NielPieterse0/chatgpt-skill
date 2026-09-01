# Technical Depth

## Core concerns
- domain invariants and state transitions
- control flow error propagation and cleanup
- concurrency races ordering and atomicity
- API schema and compatibility semantics
- database transactions migrations and query behavior
- architecture boundaries coupling and dependency direction
- security privacy and secret handling
- tests observability rollback and operational failure modes

## Method
- derive expected invariants from requirements and existing behavior
- trace changed data and state across boundaries
- check atomicity race windows and duplicate/retry behavior
- inspect public and persisted contract compatibility
- evaluate query shape migration safety and rollback
- challenge new coupling and abstractions against ownership
- look for silent failure observability and recovery gaps
- rank findings by correctness risk and evidence confidence

## Failure modes to challenge
- local readability review on a cross-system change
- missing race or retry analysis for async code
- schema migration reviewed without old/new data coexistence
- API compile compatibility mistaken for semantic compatibility
- new abstraction accepted without ownership benefit
- error swallowing or fallback hiding correctness failures
- tests passing because mocks bypass changed integration
- performance or security risk asserted without plausible path

## Verification questions
- material invariants remain true on success failure and retry
- concurrency assumptions are explicit and tested where critical
- public and persisted contracts have compatibility evidence
- data migrations include rollout rollback and mixed-version reasoning
- architecture changes preserve dependency direction
- security findings identify concrete boundary and impact
- tests cover the exact changed behavior and boundary risks
- findings are concise evidence-linked and independently actionable

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
