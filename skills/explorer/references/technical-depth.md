# Feature Exploration Technical Depth

Load this reference when one feature, request path, event flow, command, or behavior must be understood before design or modification. Use the codebase-onboarding specialist when the goal is a repository-wide contributor mental model.

## Exploration target

Define a specific behavior or question. Good targets include:

- “How does request X reach persistence?”
- “Where is permission Y enforced?”
- “What writes state Z?”
- “How does event A trigger side effect B?”
- “Which files are essential to understand feature C?”

Do not start with a vague request to “understand everything.”

## Feature discovery

Find observable entry points first:

- HTTP/API route or RPC method;
- UI route/component/action;
- CLI command;
- event/message consumer;
- scheduled/background job;
- library/public method;
- config/feature flag that selects behavior.

Search for exact symbols, route strings, event names, schema fields, and tests. Confirm registration/wiring; a matching filename is not proof of runtime reachability.

## Execution-path tracing

Follow control flow end-to-end:

entry → validation/middleware → routing/dispatch → orchestration → business/domain logic → persistence/external integration → event/side effect → output.

At each step record:

- file and symbol, with line references when stable/available;
- input and output data shapes;
- transformations/defaults/normalization;
- synchronous versus async transition;
- state read/write;
- external/internal dependency;
- error/exception path;
- side effects;
- authorization, caching, logging, metrics, and other cross-cutting behavior.

When indirection exists through interfaces, DI, registry maps, reflection, decorators, generated code, event buses, or framework conventions, trace the binding mechanism rather than jumping from interface to assumed implementation.

## Data-flow tracing

Track important values separately from call flow:

- source and trust level;
- validation/sanitization;
- type/schema transformations;
- identity/tenant context;
- persistence/cache keys;
- serialization/deserialization;
- propagation to external systems;
- returned or emitted representation.

This often exposes behavior that the control-flow summary misses, especially authorization, caching, and mutation.

## Architecture mapping

For the target feature only, identify:

- presentation/transport layer;
- application/use-case orchestration;
- domain/business logic;
- persistence and external adapters;
- contracts/interfaces between them;
- cross-cutting middleware/interceptors;
- test seams.

Note patterns such as layered, ports/adapters, event-driven, repository, CQRS, or framework conventions only when visible in code. Do not infer intent from pattern-shaped names alone.

## State and side effects

List every material state transition:

- database create/update/delete;
- cache read/write/invalidate;
- file/object storage;
- event/message publication;
- outbound HTTP/RPC;
- background job enqueue;
- in-memory/session/client-state mutation;
- logging/audit/security event with behavioral significance.

For async effects, record who consumes them and whether the traced path ends before completion.

## Error and edge paths

Trace at least the likely non-happy paths relevant to the question:

- validation rejection;
- not-found/conflict;
- authorization denial;
- dependency timeout/failure;
- retry or duplicate delivery;
- partial state change;
- fallback/cache behavior;
- cancellation.

Do not claim full behavior from the happy path alone.

## Dependency map

Distinguish:

- internal modules/packages;
- shared libraries/utilities;
- generated clients/code;
- external services/APIs;
- database/cache/queue infrastructure;
- framework/runtime dependencies.

Record which dependencies are essential to understanding the feature and which are incidental implementation details.

## Tests as evidence

Tests can reveal intended contracts, edge cases, fixtures, and seams, but passing tests are not proof that production wiring matches them. Compare tests with actual registration/configuration when the distinction matters.

Useful evidence:

- unit tests for business invariants;
- integration/contract tests for boundaries;
- E2E tests for user journeys;
- fixtures/builders showing expected data shape;
- regression tests naming historical failures.

## Observations versus review

The upstream explorer includes observations about strengths/issues/opportunities. Keep those strictly evidence-based and secondary to descriptive tracing. If the user asks for defect judgment, architectural redesign, or implementation recommendations, route to reviewer/architecture/development specialists rather than allowing exploration to become unbounded review.

## Essential-files output

End with the smallest set of files needed to reconstruct the feature mentally. For each, explain its role. Include files that own wiring/contracts even when they contain little business logic.

## Failure modes to challenge

- grep match mistaken for live execution path;
- interface traced without finding runtime binding;
- happy path documented while error/async side effects are omitted;
- call flow described but data/identity transformations ignored;
- framework middleware or decorators treated as invisible;
- tests treated as production behavior without checking wiring;
- technical debt opinion stated without evidence;
- changing code while still in exploration mode;
- reading too broadly after the target path is already understood.

## Output contract

Provide:

1. target behavior and evidence boundary;
2. entry points;
3. step-by-step execution flow;
4. data transformations;
5. components/responsibilities;
6. state changes and side effects;
7. contracts/dependencies;
8. error/edge paths;
9. architecture observations;
10. essential files;
11. inspected/uninspected areas and unresolved questions.

## Verification questions

- Is every step tied to an inspected symbol or explicit framework binding?
- Can the input be followed to every material output/state effect?
- Are async boundaries and consumers identified?
- Are authorization and tenant context preserved across the path?
- Are errors and retries visible where relevant?
- Can another engineer navigate directly to the essential files and reproduce the explanation?

## Specification-to-TDD handoff

Explorer supplies current-state evidence: requirement/question → observed behavior/path → owning boundary → existing invariants/contracts → likely test seams. It does not select the implementation, mutate code, or claim the new behavior verified.