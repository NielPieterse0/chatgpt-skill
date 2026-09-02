# Evidence Engineering Technical Depth

Load this reference when a claim about correctness, completion, regression, quality, or acceptance must be translated into reproducible evidence. This specialist designs proof; it does not grant execution or lifecycle authority.

## Evidence starts from the claim

For each material claim write:

- the exact observable statement;
- the acceptance criterion or governing requirement;
- the strongest practical evidence source;
- what would falsify the claim;
- the scope represented by the evidence;
- any unavailable verification.

Avoid collecting artifacts first and deciding later what they supposedly prove.

## Evidence hierarchy by claim type

Prefer the lowest-cost evidence that directly proves the behavior, while matching the actual claim.

- **Pure logic/invariant:** focused deterministic unit/property test.
- **Module/component integration:** component/integration test across the changed boundary.
- **Wire/schema compatibility:** contract/schema test plus representative producer/consumer behavior.
- **Persistence/migration:** migration/reconciliation checks, row/domain invariants, before/after state.
- **Concurrency/idempotency:** controlled repeated/concurrent scenario with observable state.
- **User workflow:** E2E/system test when lower layers cannot prove integration.
- **Visual/layout:** screenshot/image comparison or human visual review, but not as proof of hidden state or behavior.
- **Operational behavior:** logs/metrics/traces/health/recovery evidence under the relevant scenario.
- **Security claim:** deterministic defensive test plus specialist review appropriate to the attack surface.

A screenshot cannot prove a database invariant. A unit test cannot prove runtime wiring. Match evidence to the claim boundary.

## Fail-before / pass-after discipline

For a defect fix, strongest evidence usually shows:

1. the relevant test/check fails against the baseline or known-bad state for the expected reason;
2. the same check passes after the smallest responsible change;
3. surrounding regression checks still pass;
4. the changed behavior is not merely masked by altered assertions/fixtures.

When a fail-before state cannot be executed safely or reproducibly, record why and use the strongest alternate evidence without pretending RED was observed.

## Acceptance decomposition

Translate specification language into testable form:

requirement → observable acceptance criterion → invariant/system behavior → owning boundary → scenario/input → expected output/state/side effect → evidence source.

Split ambiguous compound requirements until each criterion can be independently falsified.

## Evidence strength and scope

Label what evidence actually represents:

- static inspection;
- focused local test;
- component/integration test;
- full repository test suite;
- target-runtime check;
- staging/system check;
- production observation;
- human review.

Do not upgrade a local test to “production-ready” evidence. Broader scope is not automatically stronger if it is less direct.

## Mechanical evidence

Prefer deterministic tooling for facts such as:

- file existence/path constraints;
- JSON/YAML/schema validity;
- counts, dimensions, hashes;
- generated artifact identity;
- test exit status;
- exact diff/commit identity;
- contract compatibility checks;
- security-policy/validator outcomes.

Record the command/tool, inputs, exit/result, relevant output, and artifact identity when reproducibility matters.

## Behavioral evidence

For model-, UI-, or environment-dependent behavior:

- use realistic representative prompts/scenarios;
- keep candidate/baseline inputs equivalent;
- repeat when nondeterminism materially affects confidence;
- preserve raw or referenced outputs where policy permits;
- require specific grading evidence;
- use human review for qualities not reducible to deterministic assertions.

Never synthesize missing runs or metrics.

## Logs, metrics, and traces

Operational telemetry is evidence only for what it directly observes.

- Logs: event detail and context; beware sampling, redaction, missing branches, and high-cardinality data.
- Metrics: trends/distributions; beware aggregation hiding individual failures.
- Traces: causality and latency across boundaries; beware unsampled paths.
- Health/readiness: only the dependencies included in the probe.

Correlate multiple sources when a high-impact claim cannot be established by one signal.

## Negative evidence and absence claims

“Not found” is difficult to prove. When claiming absence:

- define the search universe and exclusions;
- use more than one relevant mechanism when practical (e.g., structural search plus validator);
- state limitations such as generated/runtime content not inspected;
- avoid converting no observed evidence into proof of impossibility.

## Evidence integrity

Bind evidence to the artifact it evaluates:

- candidate commit/content hash;
- test-definition revision;
- configuration/runtime identity;
- source inputs/fixtures;
- date where external/runtime state can change.

Any post-evidence edit to a covered artifact can stale the result. Re-run affected checks rather than carrying forward a pass by assumption.

## Human review

Human review is distinct evidence. Preserve reviewer identity/date and actionable feedback when the governing standard requires it. Agent grading can prepare or supplement review but cannot fabricate or substitute a named-human gate.

## Failure triage

A failed check must distinguish:

- product/implementation failure;
- test defect;
- environment/infrastructure failure;
- flaky/nondeterministic behavior;
- unsupported/unobservable requirement.

Do not “fix” evidence by weakening an assertion until it passes. If the assertion is wrong, change it with rationale and record the definition change separately.

## Failure modes to challenge

- artifact collection with no mapped claim;
- screenshot treated as proof of hidden behavior;
- tests passing only because assertions were weakened;
- broad suite pass used to infer an untested requirement;
- stale evidence after implementation changes;
- logs with no correlation to the tested request/commit;
- baseline/candidate runs using different prompts/fixtures/config;
- unobserved metric reported as zero;
- human-review field populated by an agent;
- predetermined “pass” or quota-driven issue hunting.

## Evidence report structure

For each claim record:

- requirement/claim;
- evidence type and scope;
- exact artifact/run identity;
- expected result;
- observed result;
- pass/fail/unverified;
- evidence reference;
- limitations/residual risk.

Finish with the set of claims proven, disproven, and not credibly observable.

## Specification-to-TDD composition

Trace requirement → observable criterion → invariant → owning boundary → smallest behavior slice → lowest appropriate test → fail-before evidence → RED → implementation GREEN → REFACTOR → focused/broader checks → independent review → fresh completion evidence. Evidence engineering owns the proof mapping and freshness, not the implementation or lifecycle gate.