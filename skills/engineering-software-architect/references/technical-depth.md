# Technical Depth

## Core concerns
- bounded contexts modules and cohesion
- dependency direction and stable abstractions
- interfaces contracts and compatibility
- data ownership consistency and transaction boundaries
- sync async and event-driven interaction
- scalability latency availability and cost
- failure containment retries idempotency and recovery
- evolution seams migration strategy and ADR-quality rationale

## Method
- extract quality attributes and hard constraints from requirements
- identify domain responsibilities and data owners
- choose boundaries that maximize cohesion and minimize coupling
- define contracts and dependency direction before implementation detail
- model failure modes consistency and recovery at boundaries
- test alternatives against scale operability security and change cost
- plan incremental migration with reversible seams
- record decisions trade-offs rejected options and measurable consequences

## Failure modes to challenge
- architecture by technology preference rather than requirements
- shared database used as accidental integration bus
- cyclic dependencies and bidirectional ownership
- distributed transactions introduced without failure model
- microservices chosen before modular boundaries are proven
- abstract layers with no substitutable responsibility
- ignoring migration compatibility and rollout
- diagrams that cannot be traced to code contracts

## Verification questions
- every boundary has a responsibility and owner
- dependency direction is acyclic or justified
- contracts include versioning and failure semantics
- data consistency model matches business invariants
- resilience mechanisms avoid retry storms and duplicate effects
- quality attributes have observable acceptance evidence
- migration path preserves compatibility and rollback
- decision record separates facts assumptions and trade-offs

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
