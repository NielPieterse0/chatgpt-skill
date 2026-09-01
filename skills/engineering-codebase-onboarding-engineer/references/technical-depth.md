# Technical Depth

## Core concerns
- repository topology and executable entry points
- build packaging and dependency systems
- test hierarchy fixtures and quality gates
- runtime processes jobs queues and schedulers
- data stores schemas migrations and ownership
- public contracts and integration boundaries
- cross-cutting configuration logging metrics and security
- hotspots generated code and legacy seams

## Method
- read governing repository instructions first
- identify how the system starts builds tests and ships
- map modules by responsibility and dependency direction
- trace one representative critical path end to end
- locate state ownership schemas and migration mechanisms
- identify contracts integration points and compatibility obligations
- record invariants and non-obvious gotchas
- produce a change-oriented map rather than a directory tour

## Failure modes to challenge
- equating directory structure with architecture
- missing generated code or build-time behavior
- ignoring tests as executable specification
- failing to distinguish source from generated artifacts
- overlooking data migrations and compatibility boundaries
- assuming one runtime path covers workers or jobs
- inventing ownership from filenames
- producing exhaustive inventory with no prioritization

## Verification questions
- map identifies start/build/test commands without executing unauthorized actions
- critical path includes state and external effects
- module responsibilities and dependency direction are explicit
- test levels and fixtures are located
- data ownership and migrations are identified
- uncertain or environment-specific behavior is labeled
- likely change seams and blast radius are stated
- next-step reading is prioritized

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
