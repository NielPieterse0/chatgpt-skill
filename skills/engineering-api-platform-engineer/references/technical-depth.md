# API Platform Engineering Technical Depth

Load this reference for public, partner, service, or platform API design/evolution where wire contracts, consumer compatibility, gateway semantics, or SDK/developer experience matter.

## Contract-first model

- Treat a published API as a consumer-held contract. Working client code is part of the compatibility surface even when the schema still validates.
- Start from resources, operations, lifecycle, invariants, consumer jobs, and failure semantics before endpoint naming.
- Keep a machine-readable contract such as OpenAPI, JSON Schema, AsyncAPI, protobuf, or GraphQL schema as close as practical to the reviewed source of truth.
- Lock cross-cutting conventions once: field naming, identifiers, timestamps, nullability, enum behavior, pagination, errors, idempotency, correlation, authentication, and authorization context.
- Distinguish contract syntax from semantics. A same-shaped field whose meaning, default, ordering, authorization, or consistency changes can still be breaking.

## Compatibility classification

Usually additive, subject to client behavior:

- new endpoint or operation;
- new optional request field or parameter;
- new optional response field;
- relaxed validation;
- new enum value only when consumers are documented and tested to tolerate unknown values.

Usually breaking:

- remove or rename a field or operation;
- change type, format, unit, meaning, default, nullability, or requiredness;
- tighten validation;
- remove an enum value;
- change error structure or status-code semantics;
- change ordering, pagination stability, authorization, idempotency, or consistency guarantees relied on by clients.

For protobuf/gRPC, also check wire compatibility, field-number reuse, reserved fields, and generated-client behavior. For GraphQL, prefer additive schema evolution and explicit field deprecation; versionless transport does not eliminate semantic breakage.

## Versioning and deprecation

Use version boundaries for genuine breaking change, not routine additive evolution. A deprecation plan should define:

1. announcement and changelog entry;
2. migration guide and replacement behavior;
3. machine-visible deprecation/sunset signals where the protocol supports them;
4. a consumer-appropriate runway rather than a hard-coded universal duration;
5. usage telemetry by consumer/version when available;
6. outreach or escalation for material remaining users;
7. measurable exit criteria before removal.

Do not claim a deprecation is safe merely because a date has passed. Remaining usage, contractual commitments, and migration blockers matter.

## Retry and idempotency semantics

For state-changing operations, define whether retries are safe before advising clients to retry.

- Specify idempotency-key scope, uniqueness, retention/replay window, and ownership/tenant boundary.
- Define the response for repeated identical requests and for key reuse with different payloads.
- Define concurrent duplicate handling and whether processing state is observable.
- Distinguish transport retry from application retry; avoid retry storms on overloaded dependencies.
- Pair `Retry-After` or equivalent guidance with retryable status/error classes where appropriate.

## Pagination and collection semantics

Choose pagination from consistency and access needs, not convention.

- Offset pagination is simple but can duplicate or skip on volatile datasets and becomes costly at deep offsets.
- Cursor/keyset pagination needs a stable total ordering, cursor opacity/versioning, tie-breakers, and explicit behavior when rows are inserted, removed, or mutated.
- Define filtering and sorting grammar, case/locale semantics, maximum page size, and interaction with authorization.
- State whether totals are exact, approximate, expensive, or unavailable.

## Error contract

Errors are a consumer debugging interface. Prefer:

- correct protocol status semantics;
- stable machine-readable error code;
- safe human-readable message;
- structured field/context details when useful;
- request/correlation identifier for support and tracing;
- no stack traces, secrets, internal paths, or unstable implementation text in the public contract.

Document retryability and conflict/precondition semantics instead of forcing clients to infer them from prose.

## Authentication, authorization, and tenancy

- Authentication establishes identity; it does not prove authorization to a resource or action.
- Specify credential/token type, scopes/audience, expiry/refresh expectations, and service-to-service identity where relevant.
- Define resource/action authorization and tenant isolation at the contract boundary.
- Do not expose client-manageable claims as authoritative privilege without server-side verification.
- Keep deep identity design with the responsible security specialist.

## Rate limits, quotas, and gateway behavior

- Separate sustained rate, burst allowance, quota, concurrency, payload, and cost limits.
- Make enforcement observable through documented response metadata where possible; do not assume one vendor-specific header family is universal.
- Return a stable rate-limit error and retry guidance.
- Define whether limits apply per credential, user, tenant, IP, operation, or another key.
- Treat gateway validation, request-size limits, abuse protection, and correlation as part of externally visible behavior when consumers depend on them.

## SDK and developer-experience surface

When SDKs are part of the platform contract:

- generate as much as practical from the same reviewed contract;
- test generated clients against compatibility changes;
- preserve idiomatic language behavior without inventing divergent semantics;
- version SDKs coherently with API compatibility policy;
- verify quickstarts and examples execute against the documented contract;
- keep reference docs, changelog, authentication setup, and migration guidance aligned.

Do not assume every internal API requires multi-language SDK generation or a developer portal; justify those costs from consumers.

## Observability and governance

Track signals that answer consumer-impact questions: request IDs, operation/version usage, latency/error distributions, rate-limit events, deprecation usage, and contract-diff results. Contract linting and compatibility diffing are mechanical gates where available, but they do not prove semantic compatibility on their own.

## Failure modes to challenge

- implementation-first API with a retrofitted spec;
- silent semantic break hidden behind schema compatibility;
- inconsistent names, timestamps, IDs, nullability, pagination, or errors;
- authentication treated as authorization;
- unsafe retry advice on non-idempotent writes;
- cursor without stable ordering or tie-breaker;
- deprecation with no migration path, usage evidence, or exit criteria;
- rate limiting that clients cannot observe or recover from;
- generated SDK/docs that drift from actual behavior;
- implementation details leaked into long-lived public contracts.

## Verification questions

- Can a contract diff classify wire changes, and has semantic compatibility also been reviewed?
- Are negative, boundary, conflict, retry, and authorization semantics explicit and testable?
- Can duplicate writes be safely recognized under concurrency?
- Can pagination avoid duplicates/skips under the stated data-consistency model?
- Do generated clients tolerate additive evolution such as unknown enums where claimed?
- Is deprecation progress measurable by affected consumer/version?
- Can support correlate a consumer-visible failure to server evidence without exposing sensitive details?

## Specification-to-TDD composition

Trace requirement → consumer-observable acceptance criterion → wire/semantic invariant → owning contract/gateway/client boundary → smallest compatible behavior slice → lowest test level that crosses that boundary → failing contract/behavior test → RED → GREEN → REFACTOR → compatibility and generated-client checks → independent review → focused verification → governing repository/KIS gate. This specialist supplies API/platform reasoning only; it does not grant lifecycle or mutation authority.