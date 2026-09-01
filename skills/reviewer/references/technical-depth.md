# Technical Depth

## Core concerns
- requirements and intended behavior
- changed control and data flow
- edge cases failure paths and error handling
- security and privacy implications
- regression and compatibility risk
- test relevance and missing cases
- scope discipline and accidental changes
- actionable findings with evidence and severity

## Method
- read requirements and repository authority before the diff
- identify behavioral changes and affected boundaries
- trace risky paths rather than reviewing lines in isolation
- check invalid input failures concurrency and cleanup where relevant
- verify tests exercise changed behavior instead of implementation trivia
- separate blockers from suggestions and style preferences
- cite exact evidence for every finding
- re-review affected areas after fixes

## Failure modes to challenge
- finding quotas that manufacture low-value issues
- style preference presented as correctness
- speculation without code path evidence
- ignoring tests or treating their existence as proof
- reviewing only changed lines when callers change semantics
- duplicate findings for same root cause
- assuming generated code is correct because tool produced it
- approving with stale verification after edits

## Verification questions
- blocking findings are tied to concrete behavior or requirement
- severity reflects credible impact and reachability
- false positives are actively avoided
- tests are assessed for causal relevance
- security findings include trust boundary or exploit precondition
- regression risk includes callers and contracts
- fixed findings are rechecked against new diff
- completion distinguishes no-findings from unreviewed areas

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
