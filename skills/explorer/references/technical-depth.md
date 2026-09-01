# Technical Depth

## Core concerns
- entry points and dispatch
- call graph and control flow
- data transformations and state transitions
- configuration feature flags and environment inputs
- persistence queues events and external boundaries
- layering ownership and dependency direction
- side effects concurrency and error paths
- file-and-symbol evidence with uncertainty

## Method
- start from observable behavior and likely entry points
- trace callers and callees until stable boundaries emerge
- follow data from input through transformations to side effects
- map configuration and runtime variants that alter the path
- compare similar features to expose established patterns
- record architecture layers and dependency seams
- stop at evidence gaps rather than guessing
- return a compact path map with key files and risks

## Failure modes to challenge
- keyword-only search mistaken for execution tracing
- listing files without explaining relationships
- assuming names imply runtime behavior
- ignoring alternate paths feature flags or async work
- missing persistence or external side effects
- over-reading the repository without a decision question
- turning exploration into unauthorized edits
- presenting inference as observed fact

## Verification questions
- each material path claim cites concrete code evidence
- entry-to-effect trace covers happy and failure paths
- data ownership and mutation points are explicit
- unknown runtime-dependent behavior is labeled
- similar-feature comparison is scoped and relevant
- architecture boundaries match actual dependencies
- no mutation is performed
- output identifies next files/tests needed

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
