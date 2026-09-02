# High-Signal Review Technical Depth

Load this reference for an ordinary independent review of a bounded diff, commit, branch, or PR. Use `engineering-code-reviewer` when the requested review needs deep cross-module architecture, migration, concurrency, or operability analysis.

## Scope first

State exactly what is being reviewed and against which requirement/project rules. Defaulting to “all repository problems” creates false positives and noise. Distinguish:

- changed behavior;
- relevant unchanged context needed to understand it;
- pre-existing issues outside the change;
- unavailable evidence.

## High-signal responsibilities

Review for material issues in:

- functional correctness and logic;
- edge/boundary/null/error behavior;
- security and authorization;
- regressions and compatibility;
- performance when a changed path plausibly affects it;
- test coverage of important behavior;
- explicit project conventions that affect correctness/maintainability.

Style preferences belong to formatters/linters unless a governing project rule makes them material.

## Confidence filtering

The Anthropic source uses a 0–100 confidence scale and reports only high-confidence findings. Preserve the principle:

- discard candidates disproved by caller constraints, framework guarantees, tests, or unchanged behavior;
- do not report a pre-existing issue as introduced by the change;
- report speculation only when clearly marked and material enough to warrant verification;
- prioritize precision over finding count.

No fixed numeric threshold is repository authority unless the active review contract chooses one.

## Finding construction

A useful finding answers:

1. Where is the changed code?
2. What concrete input/state/interleaving triggers the problem?
3. What observable wrong result, security impact, or regression follows?
4. Why do current checks not prevent it?
5. What is the smallest credible fix or verification?

If one of these cannot be established, investigate more or omit the finding.

## Correctness checks

Look for:

- wrong condition/branch/order;
- off-by-one/range/boundary errors;
- missing null/optional/error cases;
- invalid state transitions;
- swallowed exceptions or silent partial failure;
- missing cleanup/resource handling;
- mismatched assumptions between caller/callee;
- incorrect time/date/locale/precision handling;
- race/duplicate handling when clearly present in changed code.

## Security checks

Within the changed surface, inspect authentication/authorization, untrusted input, injection sinks, filesystem/path use, secret leakage, unsafe deserialization, outbound URL/SSRF risk, client-side privilege assumptions, and error exposure. Route deep security assessment to the specialist rather than inflating an ordinary review.

## Regression and contract checks

Ask whether the change alters:

- public API/event/schema/CLI/config behavior;
- persisted data shape;
- default values or validation;
- ordering/pagination;
- authorization/tenant semantics;
- backwards compatibility expected by existing callers;
- build/runtime platform assumptions.

A regression can exist even when the new requested case passes.

## Performance checks

Flag only evidence-backed concerns such as:

- N+1/repeated external calls in a changed loop;
- obviously worse algorithmic complexity on relevant sizes;
- unbounded data reads/output;
- blocking work added to a latency/event-loop path;
- duplicate expensive computation;
- missing pagination/backpressure where the changed behavior makes it necessary.

Do not demand optimization without a plausible workload consequence.

## Test review

Tests should prove the behavior that justified the change.

- Verify the critical path/bug case is asserted, not just executed.
- Look for meaningful negative/boundary cases.
- Prefer behavior assertions over implementation-coupled mock choreography.
- Check whether the test would fail if the defect/regression were reintroduced.
- Identify important untested behavior specifically; “needs more tests” is not a finding.
- Treat retries/sleeps/shared fixtures as suspect only when they create real nondeterminism.

## Project-guideline compliance

Read and apply the active repository instructions and explicit conventions. Do not import Claude-specific `CLAUDE.md` assumptions into a different repository. A convention finding should cite the applicable project rule or show a concrete failure caused by the divergence.

## Review process

1. Read authority, requested behavior, and review source.
2. Inspect the diff before exploring broad context.
3. Trace changed behavior far enough to understand caller/callee and tests.
4. Generate candidate findings.
5. Attempt to falsify each candidate.
6. Rank surviving findings by impact and confidence.
7. Report all material findings in one pass where practical.
8. State what was not reviewed or could not be verified.

## Severity

Use simple impact classes that fit the governing workflow, for example:

- **Critical/blocking:** likely data loss, exploitable security issue, broken essential behavior, severe contract regression.
- **Important/blocking or high priority:** real user/system defect, meaningful regression, missing critical error/authorization handling.
- **Suggestion/non-blocking:** maintainability or resilience improvement with concrete value but no demonstrated blocker.

Avoid “nit” output unless the user explicitly requests stylistic review and tooling does not own it.

## Failure modes to challenge

- quota-driven comment generation;
- review of unrelated repository problems;
- style preference presented as correctness;
- vulnerability claim without a plausible source/sink or privilege impact;
- hypothetical performance complaint without workload consequence;
- test-count criticism without naming an uncovered behavior;
- duplicate comments for one root cause;
- drip-feeding obvious findings across multiple passes;
- “looks good” based only on tests passing.

## Output contract

Start with the review scope. For each material finding provide severity, concise title, exact location, triggering evidence, impact, and concrete remediation direction. If no material findings remain after falsification, state that and list any review limitations rather than inventing suggestions.

## Verification handoff

Reviewer findings are hypotheses supported by code evidence until reproduced or otherwise verified. Hand blockers to the governing implementation workflow and use the appropriate verification specialist for completion evidence. Review itself does not authorize edits, merge, or lifecycle transitions.