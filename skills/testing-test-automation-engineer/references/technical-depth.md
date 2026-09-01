# Technical Depth

## Core concerns
- test-level selection by behavior boundary
- unit component integration contract and E2E roles
- hermetic fixtures clocks randomness and identity
- test data builders factories and cleanup
- dependency virtualization versus real boundary tests
- parallelism isolation and order independence
- flake diagnosis retries quarantine and ownership
- coverage by risk mutation and escaped defects

## Method
- start from behavior and failure mode not preferred framework
- place assertions at the lowest level that still crosses the changed boundary
- use real contracts at integration seams that mocks could mask
- control clocks randomness IDs locales and environment
- design fixtures for explicit setup and deterministic teardown
- make tests independent under parallel and shuffled execution
- diagnose flakes to a cause instead of normalizing retries
- use E2E sparingly for critical cross-system journeys

## Failure modes to challenge
- E2E used for logic better proven below UI
- mock expectations coupled to implementation details
- sleep-based synchronization
- retry-on-failure hiding races
- shared mutable fixtures across tests
- tests depending on execution order
- assertions too broad to diagnose failure
- coverage target driving low-value tests

## Verification questions
- each requirement maps to a justified test level
- critical boundaries have at least one real integration/contract check
- tests pass under parallel or documented isolation constraints
- time and randomness are controlled
- fixtures clean up reliably
- flakes have root-cause treatment and ownership
- failure output identifies the violated behavior
- test cost is proportional to risk and feedback value

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
