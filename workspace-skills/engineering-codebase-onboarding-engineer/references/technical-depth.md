# Codebase Onboarding Technical Depth

Load this reference when the goal is to orient a contributor to an unfamiliar repository, map ownership, or trace how representative behavior moves through the code. Use `explorer` instead when the question is one feature/path rather than repository-level onboarding.

## Evidence discipline

- State repository facts only when they are supported by inspected files or deterministic repository metadata.
- Quote identifiers, routes, functions, classes, commands, package names, and config keys exactly when they anchor the explanation.
- Separate observed behavior from inference. If an architectural role is inferred from call/import structure, label it as inference rather than a declared project boundary.
- Do not imply full-repository understanding from a sampled subsystem. Record what was inspected and what remains outside the evidence set.
- Generated code, vendored code, build output, examples, fixtures, and dead/migration artifacts can distort the map; classify them before treating them as ownership evidence.

## Three-level onboarding output

### 1. One-line model

State what the repository is in one sentence: runtime/product type plus the principal responsibility visible in code.

### 2. Five-minute map

Cover:

- primary tasks/behaviors;
- main inputs and outputs;
- top-level code-bearing areas;
- runtime/build/test entry points;
- the handful of files a new contributor should read first;
- the primary request/event/command/data path.

### 3. Deep dive

Explain:

- runtime(s) and workspace/package layout;
- startup/boot sequence;
- module/service/package boundaries;
- presentation/transport, application/domain, persistence/I/O, and cross-cutting concerns where they actually exist;
- imports/calls/dispatch/event relationships;
- state ownership and persistence;
- async workers, queues, schedules, background tasks, or client-side state;
- stable/public interfaces versus internal implementation;
- tests, fixtures, and contracts that reveal intended behavior;
- files inspected and unresolved areas.

## Inventory and classification

Start with the authority and build graph, not every file.

Inspect as relevant:

- root and nested `AGENTS.md`/project instructions;
- manifests, lockfiles, workspace definitions, build files, task runners, compiler/config files;
- top-level source, application, service, package, library, test, migrations, infrastructure, and scripts directories;
- framework markers and runtime entry points;
- generated/vendor directories and ignore rules;
- CI definitions only as evidence for build/test entry points, not as authority over repository instructions.

Classify whether the repository is an application, service, library, CLI, plugin, monorepo, polyglot workspace, or hybrid. Do not infer architecture purely from directory names.

## Entry-point discovery

Find the smallest set that explains how execution starts:

- HTTP server/bootstrap, router, controller/handler;
- CLI binary, command registration, argument parser;
- queue/worker consumer or scheduler;
- library/package public exports;
- frontend application bootstrap, route tree, state initialization;
- framework-specific boot files such as Django URL/settings/wsgi/asgi, Spring application/configuration, Rails routes/initializers, Next.js routes/middleware, or equivalent.

Trace from the real entry point rather than starting at a file whose name merely sounds central.

## Execution and data-flow tracing

For representative behavior, follow:

input → parsing/validation → routing/dispatch → orchestration/use case → domain/business logic → persistence/external I/O → events/side effects → output/response.

At each hop record:

- exact file and symbol;
- data shape/transformation;
- synchronous versus asynchronous transition;
- state read/write;
- error/exception path;
- authorization or other cross-cutting interception;
- calls/imports/contracts connecting to the next hop.

Do not collapse framework middleware, dependency injection, generated clients, queues, or event buses into invisible “magic” when they materially change control flow.

## Boundary and ownership analysis

Identify boundaries from evidence such as package manifests, imports, interfaces, schemas, dependency rules, route registration, database ownership, and tests.

Look for:

- high-coupling modules or shared utility hubs;
- stable interfaces versus implementation details;
- duplicate responsibilities across packages;
- adapters around external/legacy systems;
- cross-language boundaries in polyglot systems;
- workspace tooling such as Nx, Turborepo, Bazel, Lerna, Cargo workspaces, Go modules, or equivalents;
- generated/client code that should not be mistaken for handwritten business ownership.

Surface misleading names or legacy migration artifacts only when code evidence shows their actual role. Avoid declaring code “dead” without reachability/build/runtime evidence.

## State and contract map

A useful onboarding model includes where durable and transient state live:

- relational/document/key-value databases;
- caches;
- queues/event logs;
- files/object storage;
- frontend/client stores;
- in-process caches/singletons;
- external APIs.

Record the schemas or interfaces that connect modules: API specs, protobufs, events, DTOs, DB schemas/migrations, shared types, or test fixtures.

## Test and development surfaces

Explain how contributors prove changes without executing anything unless the governing workflow authorizes it:

- unit/component/integration/E2E test locations;
- test command definitions and config;
- fixture/factory conventions;
- local bootstrap and environment shape;
- generated-code steps;
- lint/type/build gates.

Do not turn onboarding into implementation or repository mutation.

## Failure modes to challenge

- architecture summary inferred from folder names alone;
- entry point confused with a downstream handler;
- ignoring middleware, DI, queues, workers, or background side effects;
- treating an import graph as runtime call flow without verification;
- mistaking examples/tests/generated code for production ownership;
- claiming dead code from low search counts;
- presenting one subsystem as the whole repository;
- slipping into review, redesign, refactoring, or implementation advice.

## Verification questions

- Can every major claimed responsibility be tied to an inspected file/symbol?
- Can a new contributor follow at least one representative path end to end?
- Are inputs, outputs, state changes, side effects, and async transitions visible?
- Are public/stable contracts distinguished from internals?
- Are generated/vendor/test/example artifacts classified correctly?
- Does the output explicitly name inspected and uninspected areas?
- Are “read these first” files genuinely load-bearing for understanding rather than merely prominent?

## Specification-to-TDD composition

Onboarding normally precedes implementation. When handed into a spec/TDD workflow, map requirement → observed owning boundary → current behavior/path → relevant invariant/contract → candidate smallest behavior slice. Do not choose tests or modify code on behalf of the implementation workflow; supply the evidence that lets TDD and architecture specialists choose correctly.