# API Testing Technical Depth

Load this reference when an API, service boundary, webhook, RPC, or third-party integration needs behavioral verification. Use the API-platform specialist for contract design/evolution and the performance specialist for statistically serious load/capacity work.

## Test from the contract and risk

Establish:

- API/protocol/version under test;
- machine-readable contract and relevant documentation;
- authentication/authorization model;
- state/persistence side effects;
- retry/idempotency/concurrency semantics;
- compatibility obligations;
- error and rate-limit behavior;
- critical consumer workflows and known production risks.

Do not use universal coverage, latency, throughput, or traffic-multiplier targets. Derive thresholds from the governing requirement/SLO and actual workload.

## Test-level selection

Prefer the lowest level that proves the behavior while retaining at least one real boundary check for risks mocks could hide.

- Unit tests for pure parsing, validation, mapping, or client helpers.
- Component/service tests for handler/use-case behavior with controlled dependencies.
- Contract tests for producer/consumer schema and semantic compatibility.
- Integration tests for real serialization, auth middleware, persistence, queue, gateway, or client behavior.
- E2E/system tests for critical multi-boundary journeys.
- Performance/load tests when latency, throughput, concurrency, saturation, or recovery is itself the requirement.

## Functional contract matrix

For each operation test relevant cases across:

- valid minimum and representative requests;
- optional/omitted/default fields;
- boundary values and maximum accepted sizes;
- malformed syntax/types/formats;
- unknown/extra fields according to contract policy;
- missing/not-found/conflict/precondition cases;
- state transitions and repeated operations;
- response schema, headers, status/error code, and side effects;
- serialization of timestamps, identifiers, numeric precision, nulls, and enums.

An HTTP status alone is not enough when the API promises a structured error contract.

## Authentication and authorization

Test identity separately from access policy.

Authentication cases may include:

- missing/invalid/expired credentials;
- wrong audience/scope/issuer where applicable;
- malformed credentials;
- revoked/session-invalid state where the system supports it.

Authorization cases should include:

- actor can access own/allowed resource;
- actor cannot access another user/tenant resource;
- lower privilege cannot call privileged operation;
- list/search/export endpoints filter unauthorized objects;
- create/update cannot inject privileged ownership/role fields;
- service-to-service scopes/permissions are action-specific.

Do not use real secrets in test artifacts; use governed fixtures/credentials only when execution is authorized.

## Input and abuse boundaries

Exercise safe defensive cases for:

- validation and canonicalization;
- injection-sensitive parameters;
- path/query/header/body ambiguity;
- oversized payloads and deeply nested/complex inputs;
- URL/file/template/deserialization inputs where exposed;
- GraphQL query depth/complexity or batching if relevant;
- WebSocket upgrade/origin/auth/message validation if relevant.

The test plan should prove rejection/containment, not teach offensive exploitation. Do not target external systems without explicit authorization.

## Idempotency, retries, and duplicates

For retryable writes verify:

- first request creates the expected result;
- exact replay with same key returns/references the same logical result according to contract;
- same key with a different payload produces the documented conflict/error;
- concurrent duplicate requests do not create duplicate state;
- replay after the documented retention window behaves as specified;
- tenant/user scope of the idempotency key is enforced;
- failure during processing does not leave an ambiguous duplicate-prone state.

For non-idempotent operations, verify the API does not imply unsafe retries.

## Pagination, filtering, and ordering

Test:

- empty, single-page, and multi-page sets;
- maximum/minimum page size;
- stable ordering and tie-breakers;
- cursor validity/expiry/versioning where applicable;
- inserts/deletes/updates between pages under the documented consistency model;
- no duplicate/omitted records within the promised semantics;
- filter/sort combinations and invalid expressions;
- authorization filtering across pages;
- totals if the contract promises them.

## Error and failure semantics

Exercise expected dependency and state failures where practical:

- validation errors;
- not found/conflict/precondition;
- dependency unavailable/timeout;
- internal failure without sensitive leakage;
- rate limiting/resource exhaustion;
- partial/async processing;
- retryable versus terminal errors.

Verify stable machine-readable codes, correlation/request IDs when promised, safe detail, and documented retry guidance.

## Rate limits and quotas

Test from the actual policy:

- limit key/scope (credential, tenant, IP, operation, etc.);
- burst versus sustained behavior;
- quota versus rate/concurrency limits;
- documented response metadata;
- correct rate-limit error and retry guidance;
- reset/recovery behavior;
- whether one tenant/consumer can exhaust another's allowance.

Avoid hard-coded source thresholds unless they are the real system requirement.

## Contract compatibility

For version changes compare old/new producer and representative consumer behavior.

Check:

- removed/renamed/type/default/nullability changes;
- new required request fields;
- enum evolution and unknown-value tolerance;
- validation tightening;
- error/status semantic changes;
- event/protobuf field-number/wire compatibility where applicable;
- generated clients against the new contract;
- deprecation/sunset behavior.

A schema-diff tool helps but does not replace semantic compatibility tests.

## Third-party integrations

For external APIs prefer controlled mocks/virtualization for deterministic failure cases plus bounded contract/integration evidence against the real provider only when authorized.

Verify:

- request signing/auth and field mapping;
- timeout/retry/idempotency;
- rate-limit handling;
- provider error translation;
- pagination/webhook behavior;
- fallback/degradation;
- schema drift and version pinning;
- duplicate/out-of-order webhook/event delivery;
- signature/replay validation for inbound callbacks.

## Documentation and examples

Executable examples/quickstarts can be contract tests. Verify documented requests, auth setup, SDK examples, error examples, and response shapes against the same supported version. Do not assume documentation accuracy because it generated successfully.

## Performance within API testing

Use lightweight latency/concurrency checks only when they support a defined requirement. For serious baselining, load/stress/endurance/capacity, distribution analysis, or bottleneck attribution, use `testing-performance-benchmarker`.

Measure percentiles/distributions rather than relying on an average. Preserve correctness/error-rate checks while applying load; a fast wrong response is not a performance pass.

## Test data and isolation

- Use synthetic or approved non-sensitive fixtures.
- Create/own test state deterministically where practical.
- Keep parallel tests isolated by user/tenant/identifier.
- Clean up or use disposable environments according to governing test policy.
- Control clocks/IDs/randomness when they affect deterministic assertions.
- Avoid test ordering dependencies and shared mutable “seed users.”

## Reporting

Report by requirement/risk rather than vanity counts:

- contract/functional results;
- authentication/authorization results;
- negative/error/retry/idempotency results;
- compatibility/integration findings;
- performance evidence when applicable;
- exact failed assertions and evidence;
- untested/unobservable areas and environment limitations.

A “release-ready” recommendation belongs only to the governing lifecycle, not this Tier 0 skill.

## Failure modes to challenge

- endpoint count used as meaningful coverage percentage;
- only happy-path/status-code tests;
- authentication tested but resource authorization omitted;
- destructive injection payloads against non-owned targets;
- idempotency tested only sequentially, not under duplicate/concurrent conditions;
- offset/cursor pagination tested only on static data;
- mocks hiding serialization/auth/gateway behavior;
- provider integration assumed from mocked tests alone;
- arbitrary `200 ms`, `10x load`, or `95% coverage` source targets treated as universal;
- performance pass without checking correctness/errors;
- production monitoring/setup treated as authority from a test skill.

## Verification questions

- Does every material contract promise have at least one falsifying test?
- Are authorization tests actor/resource/action specific?
- Are retries, duplicates, conflicts, and concurrency represented?
- Can pagination remain correct under the stated consistency model?
- Are old consumers/clients protected where compatibility is promised?
- Are real boundary tests present where mocks could conceal failure?
- Are performance thresholds requirement-derived rather than inherited from a generic source?

## Specification-to-TDD composition

Trace API requirement → consumer-observable criterion → wire/authorization/idempotency invariant → operation/boundary → smallest behavior slice → lowest API test level → failing test → RED → GREEN → REFACTOR → contract/integration/negative/compatibility checks → independent review → focused evidence → governing repository/KIS gate. This specialist designs API verification; it does not authorize external testing, deployment, or lifecycle decisions.