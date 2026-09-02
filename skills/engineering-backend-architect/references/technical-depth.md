# Backend Architecture Technical Depth

Load this reference when backend design crosses persistence, transactions, asynchronous workflows, service boundaries, reliability, migration, caching, or operational behavior.

## Architecture selection

Choose the simplest deployment and ownership model that satisfies verified constraints.

- A monolith or modular monolith often wins when the team is small, boundaries are still moving, or independent scaling/deployment is not required.
- Microservices are justified by stable domain boundaries, independent ownership/deployment, isolation, or scaling needs—not by fashion.
- Serverless can fit bursty event-driven workloads, but evaluate latency, state, observability, execution limits, and provider coupling.
- Event-driven designs trade temporal decoupling and throughput for harder consistency, ordering, debugging, replay, and failure recovery.
- CQRS or event sourcing should solve real read/write asymmetry, audit, temporal, or domain problems; they are not default CRUD patterns.

Record the operational complexity and migration path of the chosen pattern.

## Data and transaction design

Define data ownership before tables or services.

- Identify aggregate/transaction boundaries and invariants that must hold atomically.
- Separate strongly consistent state from eventually consistent projections or integrations.
- Model uniqueness, foreign-key/relationship, lifecycle, retention, deletion, privacy, and audit requirements explicitly.
- Design indexes from real access paths and cardinality; an index is a write/storage trade-off, not a free optimization.
- Keep query plans and distribution/skew visible when scale matters.
- Use optimistic/pessimistic concurrency deliberately and define conflict behavior.
- For cross-resource workflows, prefer explicit sagas/outbox/inbox/transactional messaging patterns over accidental distributed transactions where appropriate.

## Schema evolution and data migration

For critical data, prefer expand-and-contract:

1. add backward-compatible schema/contract support;
2. deploy readers/writers that can tolerate both forms;
3. backfill or migrate with bounded batches and resumability;
4. reconcile counts, invariants, checksums, or domain totals;
5. switch reads/writes deliberately, using dual-write only when its consistency risks are understood;
6. observe stability and rollback options;
7. remove old fields/paths only after all consumers and data are migrated.

Plan locks, long transactions, index-build behavior, replication lag, write amplification, and rollback before production-scale migrations.

## External calls, retries, and time budgets

Every remote call should have an explicit time budget derived from the caller's end-to-end objective.

- Set connect/request/deadline timeouts; an unbounded call is a resource leak.
- Retry only transient, retry-safe failures, with bounded attempts, backoff, jitter, and deadline awareness.
- Make retrying writes idempotent or deduplicated.
- Use circuit breakers only when they improve failure isolation; avoid synchronized recovery storms.
- Use bulkheads/concurrency limits to keep one dependency from exhausting shared resources.
- Define fallback/graceful degradation only when stale, partial, or reduced behavior is acceptable.

## Messaging and asynchronous workflows

Define semantics rather than saying “use a queue.”

- Delivery: at-most-once, at-least-once, or effectively-once through idempotent processing/deduplication.
- Ordering: global, partition/key scoped, or none; document what business invariants depend on it.
- Poison messages: bounded retries, dead-letter handling, visibility, replay, and ownership.
- Consumer concurrency: partitioning, duplicate delivery, lock/lease expiry, and backpressure.
- Transactional publication: outbox or equivalent when database commit and event publication must not diverge.
- Replay: event/schema versioning, side-effect suppression, and historical compatibility.

## Caching

A cache changes consistency and failure behavior.

- Define source of truth, key, scope, TTL, invalidation trigger, stale tolerance, and stampede protection.
- Distinguish read-through/write-through/write-behind/cache-aside trade-offs.
- Avoid caching authorization-sensitive data under keys that can cross users/tenants.
- Plan cold-cache load and cache outage behavior.
- Measure hit rate and origin-load reduction; do not add caching without a demonstrated bottleneck.

## API/service contracts

At backend boundaries specify:

- machine-readable request/response/event schemas;
- versioning and compatibility rules;
- stable errors and correlation IDs;
- authentication and action/resource authorization context;
- pagination/filtering/sorting where applicable;
- retry/idempotency, timeout, and rate-limit semantics;
- ownership of validation and normalization.

Use the API-platform specialist for public/partner platform lifecycle depth.

## Reliability and operability

Design observability at the same time as behavior.

- Structured logs with stable event/error identifiers and correlation/request/trace IDs.
- Metrics for latency distributions, throughput, errors, saturation, queue lag, pool usage, retries, and dependency health.
- Distributed traces across services, queues, databases, caches, and external dependencies when causality spans boundaries.
- SLIs/SLOs that reflect user-visible availability/latency/correctness rather than only CPU or host health.
- Alerts on actionable user impact and exhaustion trends, with runbook/recovery evidence where required.

Backups are not recovery until restore is tested. Define RPO/RTO from business requirements, verify restore procedures, and include key/configuration dependencies.

## Security architecture within backend scope

Apply least privilege to service/database identities; validate at trust boundaries; use current approved cryptographic libraries/protocols; protect secrets and sensitive logs; separate tenant data and authorization; limit payload/resource abuse. Defer full threat modeling and AppSec assessment to the corresponding security specialists.

## Performance reasoning

Do not import arbitrary upstream targets such as “sub-20 ms queries,” “200 ms APIs,” or “10x traffic.” Establish workload and SLO first. Analyze distributions (especially tail latency), query plans, connection pools, allocation/GC, queueing, serialization, network hops, lock contention, and dependency latency. Attribute the bottleneck before optimizing.

## Failure modes to challenge

- microservices before ownership or operational maturity exists;
- database shared implicitly across supposed service boundaries;
- dual writes without reconciliation or failure semantics;
- retries without idempotency, budget, or jitter;
- queue consumers assuming exactly-once delivery;
- cache invalidation or tenant scoping left implicit;
- migration with no backfill/resume/reconcile/rollback plan;
- health endpoint that reports process liveness while dependencies are unusable;
- dashboards that show infrastructure health but not user-impacting failures;
- performance claims based only on averages.

## Verification questions

- Where are invariants enforced and what is the transaction/concurrency boundary?
- What happens if each dependency times out, partially succeeds, duplicates, or recovers late?
- Can schema/data migration be paused, resumed, reconciled, and rolled back safely?
- What is the message delivery/ordering model and how are duplicates handled?
- Can cache outage or cold start overload the source of truth?
- Are SLOs backed by measurable SLIs and end-to-end time budgets?
- Is restore—not merely backup creation—verified?
- Are security/tenant boundaries preserved across async work, caches, and data stores?

## Specification-to-TDD composition

Trace requirement → observable system behavior → consistency/reliability invariant → owning service/data/queue/cache boundary → smallest independently deliverable slice → lowest appropriate test level → failing test → RED → GREEN → REFACTOR → migration/contract/integration/failure checks → independent review → focused verification → governing repository/KIS gate. This specialist does not authorize deployment, infrastructure mutation, or lifecycle actions.