# Technical Depth

## Core concerns
- schema and contract conformance
- positive negative and boundary partitions
- authentication and resource authorization
- idempotency retries and duplicate submission
- pagination ordering filtering and cursor stability
- concurrency conflicts and conditional requests
- error taxonomy headers content types and protocol rules
- backward compatibility and consumer-driven contracts

## Method
- derive cases from the explicit API contract and invariants
- partition inputs by valid invalid boundary and malformed classes
- test authn and authz independently including cross-tenant denial
- replay idempotent and non-idempotent operations intentionally
- exercise pagination under inserts deletes and stable sort assumptions
- test preconditions conflicts and concurrent writes where supported
- verify exact error schema not just status code
- run old-client or prior-contract checks for compatibility-sensitive changes

## Failure modes to challenge
- only happy-path status assertions
- authorization tests using one identity
- fixtures that bypass validation path
- hard-coded order assumptions with unstable results
- mocking transport or serialization in a contract test
- accepting any 4xx as correct negative behavior
- retry tests that accidentally duplicate state
- performance assertions mixed into correctness tests without controls

## Verification questions
- contract examples and machine schemas agree
- negative cases assert precise failure semantics
- cross-tenant and privilege boundaries are exercised
- replay behavior matches idempotency contract
- pagination invariants are demonstrated
- concurrency behavior has deterministic assertions
- compatibility-sensitive changes include old-client evidence
- tests are deterministic and isolate external instability

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
