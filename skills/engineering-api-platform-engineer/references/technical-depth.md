# Technical Depth

## Core concerns
- resource and operation modeling
- OpenAPI JSON Schema protobuf or equivalent contracts
- backward and forward compatibility
- versioning deprecation and migration
- authentication authorization and tenant boundaries
- idempotency concurrency preconditions and retries
- pagination filtering sorting errors and rate limits
- SDK generation observability and governance

## Method
- start from consumer jobs and invariants rather than endpoint shapes
- define canonical request response and error schemas
- separate authentication identity from resource authorization
- specify idempotency keys conflict behavior and replay window
- choose pagination stable ordering and cursor semantics
- classify breaking changes at wire and semantic levels
- define rate-limit headers quotas and retry guidance
- verify contract examples against implementation and client behavior

## Failure modes to challenge
- HTTP status codes used as the only error contract
- breaking field semantics hidden behind same schema
- offset pagination on volatile high-volume sets without trade-off
- authorization inferred from authentication
- non-idempotent retry guidance
- inconsistent naming nullability timestamps or enums
- server implementation leaking into public contract
- deprecation without telemetry or migration path

## Verification questions
- contract is machine-checkable where practical
- negative and boundary semantics are documented
- authz is resource and action specific
- retry and idempotency behavior is deterministic
- pagination cannot duplicate or skip under stated consistency model
- breaking-change analysis covers generated clients
- observability can identify consumer/version impact
- deprecation has measurable exit criteria

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
