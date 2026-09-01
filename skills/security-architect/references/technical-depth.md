# Technical Depth

## Core concerns
- assets actors trust boundaries and data flows
- STRIDE-style threat enumeration and misuse cases
- authentication sessions federation and identity proofing
- authorization models least privilege and tenant isolation
- secret key and certificate lifecycle
- data classification encryption and retention
- network service and supply-chain boundaries
- security logging detection recovery and control validation

## Method
- model the system and data flows before listing controls
- identify assets adversaries entry points and privilege transitions
- enumerate threats per boundary and high-value flow
- map preventive detective and recovery controls to threats
- prefer centralized policy only where failure and latency semantics are clear
- design key secret rotation and compromise response
- validate controls with abuse cases and observable evidence
- record residual risk assumptions and ownership

## Failure modes to challenge
- checklist security without system model
- confusing authentication with authorization
- trusting internal networks or service identity implicitly
- encrypting data while exposing keys or plaintext logs
- authorization enforced only in UI or gateway
- security controls with fail-open dependency behavior
- unbounded privilege in service accounts
- mitigations that cannot be tested or monitored

## Verification questions
- threats trace to concrete assets and boundaries
- high-impact abuse paths have layered controls
- authorization is enforced at resource boundary
- secret lifecycle includes rotation revocation and audit
- data protection matches classification and retention
- control failure modes are explicit
- security telemetry supports detection and investigation
- residual risks have owners and verification plans

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
