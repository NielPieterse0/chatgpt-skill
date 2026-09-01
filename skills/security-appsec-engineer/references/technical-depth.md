# Technical Depth

## Core concerns
- input sources trust boundaries and dangerous sinks
- SQL NoSQL OS template and expression injection
- authentication authorization IDOR and tenant isolation
- SSRF URL validation redirects and metadata services
- XSS CSRF CORS content security and browser boundaries
- deserialization file upload archive and path traversal
- secrets cryptography tokens cookies and session lifecycle
- dependency supply chain configuration and security logging

## Method
- map untrusted inputs to privileged sinks before enumerating vulnerabilities
- verify authorization at the resource operation boundary
- use allowlists canonicalization and structured APIs instead of blacklist filtering
- model SSRF through redirects DNS changes and alternate address forms where relevant
- separate output encoding by HTML JS URL CSS and template context
- validate archive file and path operations after canonicalization
- check secret/token generation storage rotation and logging
- propose a regression test for each material remediation

## Failure modes to challenge
- generic OWASP checklist with no code path
- authentication mistaken for object-level authorization
- regex sanitization used instead of parameterization
- URL prefix checks vulnerable to parsing ambiguity
- escaping once then reusing data in another output context
- path checks before normalization
- crypto algorithm choice reviewed without key lifecycle
- dependency CVE mention without reachable affected behavior

## Verification questions
- findings trace source to sink or privilege boundary
- authorization bypass includes concrete object/action path
- injection remediation uses safe structured interface
- SSRF controls account for parser and redirect behavior
- browser issues identify exact rendering/request context
- file/path controls use canonical scope enforcement
- secret and session controls include lifecycle and revocation
- remediation has focused verification and residual-risk statement

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
