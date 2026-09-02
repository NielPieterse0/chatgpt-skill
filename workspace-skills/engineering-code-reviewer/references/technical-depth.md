# Deep Engineering Code Review Technical Depth

Load this reference for architecture-aware review of a bounded change when ordinary `reviewer` depth is insufficient. This specialist looks beyond obvious diff defects into invariants, concurrency, contracts, data evolution, operational behavior, and cross-module regressions.

## Review model

Review the change against four evidence sets:

1. requested/accepted behavior and governing repository rules;
2. pre-change contracts and invariants;
3. changed code plus the code paths it affects;
4. tests/verification that can falsify the implementation.

Do not turn review into a rewrite contest. A finding is valuable only when it identifies a concrete failure mode, violated contract, material maintainability hazard, or missing proof.

## Finding threshold

For each candidate finding record:

- severity/impact;
- confidence based on inspected evidence;
- exact changed location and affected path;
- triggering condition/precondition;
- resulting behavior or risk;
- why existing checks are insufficient;
- smallest credible remediation or proof needed.

Prefer fewer high-confidence findings to speculative volume. The upstream confidence-scale idea is retained as a filtering discipline, but no hard numeric threshold is repository authority unless the review workflow defines one.

## Correctness and invariants

Check:

- state transitions and invariants before/after each mutation;
- missing branches, off-by-one/boundary behavior, null/optional states, parsing/normalization;
- exception/error propagation and partial-success semantics;
- assumptions made by callers/callees;
- transactional behavior and rollback on failure;
- time, locale, precision, ordering, and identity semantics;
- whether a fix addresses root cause or only a downstream symptom.

Trace non-local effects when changed code alters shared utilities, public interfaces, persistence, event schemas, caches, or dependency injection.

## Concurrency and asynchronous behavior

Look for:

- read-modify-write races;
- lost updates and duplicate processing;
- TOCTOU assumptions;
- lock ordering/deadlock risk;
- missing cancellation/deadline propagation;
- retry without idempotency;
- asynchronous tasks whose failure is dropped;
- queue redelivery/order assumptions;
- shared mutable state across threads/workers/tests;
- cleanup/resource release on cancellation or exception.

Do not flag concurrency hypotheticals without a plausible interleaving or runtime model.

## Data and persistence review

Check:

- schema compatibility and migration sequence;
- expand/contract requirements;
- backfill resumability and reconciliation;
- transaction boundaries and isolation assumptions;
- query cardinality, N+1 behavior, missing indexes only when an actual access path supports the concern;
- tenant/authorization filtering in data access;
- soft-delete/retention semantics;
- cache invalidation and stale-state behavior;
- serialization/version compatibility.

A database change is not complete because the migration file parses; examine old/new application compatibility and rollback constraints.

## Contract review

For APIs, events, CLI interfaces, config, files, and library exports, inspect:

- added/removed/renamed fields or options;
- type, default, nullability, ordering, units, error/status semantics;
- validation tightening or new required values;
- authorization behavior;
- version/deprecation implications;
- generated clients or downstream parsers;
- retry/idempotency and compatibility of event consumers.

Semantic breaks can exist with unchanged syntax.

## Security review

Within ordinary engineering review, check concrete changed attack surfaces:

- authentication versus authorization;
- untrusted input to SQL/commands/templates/files/URLs/deserializers;
- path traversal and filesystem scope;
- secret exposure in code/logs/client bundles;
- dangerous defaults or fail-open behavior;
- privilege/tenant boundary changes;
- sensitive error output;
- new dependency/supply-chain exposure.

Route deep exploitation analysis to AppSec/security specialists; do not manufacture offensive proof beyond authorized defensive validation.

## Performance and resource review

Flag only plausible material effects:

- algorithmic complexity on realistic sizes;
- repeated queries/network calls in loops;
- unbounded collections, queues, concurrency, or retries;
- large serialization/copies;
- blocking work on latency-critical/event-loop paths;
- missing pagination/backpressure;
- cache stampede or connection-pool exhaustion;
- hot-path logging/metrics cardinality.

Avoid performance style comments without workload evidence.

## Operability and failure behavior

For production-relevant changes ask:

- Can failures be diagnosed from stable logs/metrics/traces without leaking sensitive data?
- Are request/job/trace IDs preserved across boundaries?
- Are retries/timeouts/circuit behavior observable?
- Does health/readiness reflect required dependencies appropriately?
- Can rollout and rollback coexist with old/new schemas/contracts?
- Are feature flags/config states bounded and safe by default?

## Test-quality review

Assess whether tests prove behavior rather than implementation details.

- Requirement/bug should fail before the change when practical.
- Choose the lowest test level that crosses the changed boundary.
- Critical integration contracts need real boundary checks where mocks could hide failure.
- Include meaningful negative/boundary/concurrency cases.
- Avoid sleeps, shared mutable fixtures, order dependence, and retry-masked flakes.
- Assertions should identify the violated behavior and avoid tautologically reproducing implementation logic.
- Verify tests would fail under a plausible regression, not merely execute lines.

## Architecture and maintainability

Review whether the change:

- preserves dependency direction;
- places behavior in the owning module/context;
- introduces cross-layer leakage or duplicated business rules;
- expands public surface unnecessarily;
- creates abstraction before stable repeated need;
- mixes unrelated responsibilities;
- increases coupling or migration cost without recorded trade-off.

Do not flag an architectural preference when current project architecture intentionally chooses another valid pattern.

## Review process

1. Read authority and intended outcome.
2. Bound the diff/commit/PR source.
3. Map changed files to affected execution/data paths.
4. Inspect surrounding contracts/invariants only as needed.
5. Generate candidate findings across correctness, security, data, concurrency, contracts, performance, operability, tests, and architecture.
6. Falsify each candidate: look for guards, caller constraints, tests, framework guarantees, or unchanged behavior that disprove it.
7. Report only material surviving findings, ordered by severity and confidence.
8. State residual/unreviewed areas and unavailable verification.

## Failure modes to challenge

- style/nit volume masking real defects;
- pre-existing issue attributed to the current change;
- framework-guaranteed behavior flagged as missing;
- hypothetical race with no shared state/interleaving;
- “needs more tests” without naming the missing behavior;
- suggestion presented as blocker;
- deep architecture redesign proposed for a local correct patch;
- security claim without source-to-sink or privilege impact;
- approving because tests pass without checking whether tests are meaningful.

## Output contract

For each finding provide severity, concise title, location, evidence/trigger, impact, and smallest remediation/proof. Group blockers before non-blocking findings. If no material findings survive falsification, say so and state the scope reviewed and any limitations.

## Specification-to-TDD composition

Use requirement → acceptance criterion → invariant/contract → changed owning boundary → candidate failure → test/evidence capable of reproducing it. Review occurs after implementation evidence exists and must not redefine lifecycle authority or claim completion; hand surviving findings back to the governing implementation workflow.