# Technical Depth

## Core concerns
- service and domain boundaries
- transaction and consistency models
- database schema indexes and query paths
- idempotency deduplication and exactly-once illusions
- queues streams outbox inbox and sagas
- caching invalidation and stampede control
- timeouts retries backpressure circuit breaking and load shedding
- observability SLOs capacity and recovery

## Method
- state invariants before storage or framework choices
- place transaction boundaries around invariants not convenience
- model duplicate delayed reordered and lost messages
- make retryable operations idempotent and define dedupe scope
- design indexes from concrete query shapes and cardinality
- use caches only with ownership freshness and invalidation rules
- budget timeouts and retries across the call chain
- define metrics logs traces and recovery evidence for critical flows

## Failure modes to challenge
- N+1 or unbounded query patterns
- retrying non-idempotent writes
- cache-as-source-of-truth ambiguity
- shared mutable state without concurrency model
- queue consumers with poison-message infinite retry
- transactions spanning unreliable networks
- timeouts longer than caller budgets
- schema design disconnected from access patterns

## Verification questions
- invariants map to transaction or compensation mechanisms
- duplicate and replay behavior is defined
- critical queries have index rationale
- async paths define ordering and poison handling
- retry budgets are bounded and jittered where applicable
- cache failure cannot silently corrupt source state
- operability signals detect saturation and correctness failures
- recovery and rollback paths are explicit

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
