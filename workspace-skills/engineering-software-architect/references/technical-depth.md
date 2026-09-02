# Software Architecture Technical Depth

Load this reference when a decision spans modules, domains, dependency direction, quality attributes, integration boundaries, or evolutionary structure. Use backend/API/security specialists for domain-specific depth after the system-level seams are clear.

## Architecture starts from constraints

Establish:

- business/domain outcome and important language;
- current architecture and ownership boundaries;
- change rate and likely evolution;
- team size/ownership/deployment constraints;
- quality attributes such as reliability, latency, security, operability, maintainability, data consistency, portability, and cost;
- known failure modes and migration constraints.

Do not introduce an architectural pattern unless it solves a verified coupling, complexity, ownership, consistency, or evolution problem.

## Domain modeling depth

Use domain-driven techniques when domain language, rules, invariants, and organizational boundaries are materially complex.

- **Bounded context:** boundary within which a model and language are internally consistent.
- **Aggregate:** transactional consistency boundary responsible for protecting invariants.
- **Entity / value object:** distinguish identity/lifecycle from immutable descriptive concepts.
- **Domain service:** domain behavior that does not naturally belong to one entity/value object.
- **Domain event:** meaningful business fact that may drive other behavior.
- **Repository:** collection-like access to aggregates without leaking persistence mechanics into domain policy.
- **Anti-corruption layer:** translates when integrating distinct or legacy models.

Do not force rich DDD onto simple CRUD/reporting/data-entry domains whose rules do not justify it.

## Pattern selection

### Layered

Useful when separating presentation, application, domain, and infrastructure is sufficient. Reject layers that become pass-through ceremony with no rules or dependency discipline.

### Hexagonal / ports and adapters

Use when core use cases must remain independent of UI, database, messaging, vendor APIs, or test doubles. Define ports around business-required interactions and adapters around mechanisms. Avoid adapter proliferation for trivial CRUD.

### Onion / clean dependency rules

Use when inward dependency direction is a central maintainability requirement. Domain policy must not import framework, transport, ORM, database, or deployment mechanisms.

### Modular monolith

Strong default when boundaries matter but independent service deployment does not. Enforce module ownership and dependency rules so “modular” is not only a directory layout.

### Microservices

Require evidence for independent deployment/ownership/scaling/failure isolation. Account for network failure, distributed tracing, duplicated data, consistency, contract versioning, deployment coordination, and operational burden.

### Event-driven

Good for asynchronous decoupling, fan-out, workflows, and audit/event needs. Explicitly model ordering, delivery, idempotency, schema evolution, poison events, replay, and eventual consistency.

### CQRS

Consider when read and write models genuinely diverge or complex queries should not distort the write/domain model. Avoid it for ordinary CRUD where one model is sufficient.

## Dependency and boundary rules

A typical inward dependency model is:

- domain policy depends on domain concepts only;
- application/use-case layer coordinates transactions, authorization decisions, domain objects, and ports;
- adapters translate protocols/frameworks/external models into application/domain terms;
- infrastructure implements persistence, messaging, filesystem, network, and vendor mechanisms.

Controllers reaching directly into repositories, domain code importing framework/ORM types, or unrelated bounded contexts sharing private tables are architectural smells unless explicitly accepted.

Cross-context communication should use explicit APIs, events, shared kernel contracts, published language, or anti-corruption layers—not incidental internal imports.

## Data ownership and consistency

For each important state set, identify:

- owning module/context;
- write authority;
- transaction/invariant boundary;
- replication/projection/read ownership;
- consistency expectations;
- integration contract and failure behavior.

Avoid “shared database” as an undeclared coupling mechanism between supposedly independent services. If data is duplicated, define source of truth, synchronization, staleness, and reconciliation.

## Quality-attribute reasoning

Evaluate architecture through scenarios, not adjectives.

- **Scalability:** workload, bottleneck, statefulness, partitioning, and scale dimension.
- **Reliability:** dependency failures, retry/idempotency, isolation, degradation, recovery.
- **Maintainability:** ownership, coupling, change locality, dependency direction, comprehensibility.
- **Security:** trust boundaries, privilege, data classification, attack surface.
- **Observability:** ability to reconstruct cross-boundary behavior and diagnose failures.
- **Performance:** latency budget, network hops, serialization, datastore access, queueing, caching.
- **Deployability:** blast radius, compatibility, rollout order, rollback, schema/data migration.

State what improves and what gets worse for each consequential option.

## Evolution and reversibility

Prefer decisions that can evolve without rewrites:

- seams around volatile integrations;
- modular boundaries before service extraction;
- additive contracts before hard version forks;
- expand-contract migration for data/contracts;
- strangler/parallel-run techniques for incremental replacement;
- feature flags only when lifecycle/cleanup is governed elsewhere;
- ADRs for decisions whose rationale must survive team turnover.

## ADR structure

For durable decisions record:

- title/status;
- context/problem and constraints;
- considered options;
- decision;
- consequences/trade-offs;
- migration/rollback/evolution notes;
- assumptions requiring later validation.

The ADR captures why, not merely a diagram of what.

## Diagram selection

Use the lightest representation that clarifies a decision: context/container/component views, dependency diagrams, data-flow/trust-boundary diagrams, or sequence diagrams. A diagram is evidence communication, not architecture by itself.

## Failure modes to challenge

- “best practice” with no mapped constraint;
- premature microservices/event sourcing/CQRS;
- technology-first design before domain/problem understanding;
- abstractions that hide rather than reduce coupling;
- dependency inversion described but not enforceable in imports/build rules;
- bounded contexts that still share private implementation/data;
- diagrams with no failure, data ownership, or deployment semantics;
- architecture that cannot migrate incrementally;
- quality attributes stated without measurable scenarios.

## Verification questions

- Which domain/business invariant defines each boundary?
- What dependencies point inward and which mechanisms remain outside policy?
- What fails independently, and what is the blast radius?
- Who owns each data set and contract?
- What is the rollout/migration/rollback sequence?
- Which option is simplest under current team and operational constraints?
- What assumption, if false, would reverse the decision?

## Specification-to-TDD composition

Trace requirement → quality/domain acceptance criterion → invariant → bounded context/module/interface → smallest architecture-relevant behavior slice → lowest test level that protects the boundary → failing test → RED → GREEN → REFACTOR → architecture/contract checks → independent review → focused verification → governing repository/KIS gate. Architecture should shape seams and invariants, not replace executable behavioral proof.