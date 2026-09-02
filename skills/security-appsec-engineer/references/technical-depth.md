# Application Security Engineering Technical Depth

Load this reference for code-level and SDLC security review: exploitable application weaknesses, secure coding, dependency risk, security regression tests, and development-pipeline controls. Use `security-architect` for architecture-level threat models and trust-boundary design; use the AI-generated-code auditor for generated-code-specific failure patterns.

## Risk-first AppSec model

Start with the changed or exposed attack surface, not a generic checklist. Identify:

- actors and identities;
- untrusted inputs and trust boundaries;
- sensitive operations/data;
- authorization decisions;
- persistence/file/command/template/network/serialization sinks;
- third-party libraries and external integrations;
- failure and recovery paths.

A finding needs a credible source-to-sink or privilege path. Automated scanner output is a lead, not proof.

## Secure code review priorities

Focus first on security-critical paths:

- authentication/session/token validation;
- resource/action authorization and tenant isolation;
- input validation and canonicalization;
- SQL/NoSQL/command/template injection;
- XSS/output encoding and browser trust boundaries;
- SSRF and URL fetching;
- filesystem/path traversal and upload handling;
- unsafe deserialization and dynamic execution;
- cryptography/randomness/key use;
- sensitive data exposure in responses/logs/cache/client code;
- business-logic abuse, race/TOCTOU, workflow bypass, and privilege escalation;
- dependency and build integrity.

Distinguish exploitable defects from defense-in-depth hardening.

## Authentication

Check the full validation contract for tokens/sessions as applicable:

- signature/issuer/audience/expiry/not-before;
- accepted algorithms and key selection;
- token/session rotation and revocation semantics;
- cookie security attributes and CSRF interaction;
- password/reset/MFA flows where relevant;
- generic external auth errors that do not leak account state unnecessarily;
- server-side enforcement rather than UI-only checks.

Do not invent exact token lifetimes or algorithms as universal policy. Follow governing product/security requirements and current approved libraries.

## Authorization

Authorization failures are frequently missed by scanners.

- Verify the actor is allowed to perform the action on the exact target resource.
- Test horizontal and vertical privilege boundaries.
- Treat object IDs supplied by users as identifiers, not authorization.
- Check collection/list endpoints for tenant/resource filtering as carefully as item endpoints.
- Validate create/update fields against mass assignment and privilege-field injection.
- Keep policy enforcement centralized/shared where that reduces inconsistent copies, but do not move rules blindly across domain boundaries.
- Never trust client-editable role/profile/request metadata as the sole privilege source.

## Input and injection boundaries

Validate structured input against explicit schemas/types and enforce semantic constraints after parsing. Then use sink-appropriate safety:

- parameterized/prepared database APIs rather than string-built queries;
- argument-array process APIs rather than shell concatenation;
- context-aware output encoding for HTML/JS/URL/CSS contexts;
- safe template APIs and no evaluation of user-provided templates/code;
- allowlisted protocols/hosts or stronger destination policy for server-side URL fetches;
- canonicalized bounded filesystem paths with traversal/symlink/reparse controls;
- safe deserializers and explicit type/schema validation;
- upload type/size/content checks plus isolated storage/execution policy.

Sanitization is not a universal substitute for correct sink APIs.

## Browser/application security

Review as applicable:

- XSS sources/sinks and framework escape hatches;
- CSRF for ambient-cookie state changes;
- CORS as a browser read policy, not authentication;
- CSP and security headers as defense in depth;
- open redirects and OAuth redirect validation;
- clickjacking/frame policy for sensitive interfaces;
- postMessage origin/source validation;
- client-side secrets and privileged decisions.

Avoid cargo-cult header findings where the application threat model does not support the claimed impact.

## SSRF and outbound integrations

For user-influenced destinations verify:

- allowed schemes and destination policy;
- DNS/IP resolution behavior and redirects;
- private/link-local/metadata ranges where relevant;
- credential/header forwarding;
- response-size/time limits;
- egress/proxy controls where available.

String-prefix checks alone are usually insufficient for SSRF-sensitive code.

## File and path security

Check:

- canonical path containment under an allowed root;
- traversal and mixed separator/encoding cases;
- symlink/reparse-point behavior;
- extension versus actual content;
- archive extraction paths and expansion limits;
- executable/active content handling;
- overwrite/collision semantics;
- authorization to the referenced file/object.

## Secrets and cryptography

- Never hardcode or echo secrets in examples, logs, evidence, or client code.
- If a secret was exposed, source removal does not prove revocation; rotation/revocation is a separate required remediation where applicable.
- Use approved maintained cryptographic libraries/primitives; no custom crypto.
- Check nonce/IV uniqueness, randomness, key separation/storage/rotation, and authenticated encryption/signature verification as relevant.
- Do not encode volatile algorithm/version recommendations as timeless skill policy; use current project/security authority.

## Dependency and supply-chain security

Assess:

- dependency necessity and provenance;
- lockfile/pinning/integrity;
- known-vulnerability evidence when governed scanners/data are available;
- abandoned/unmaintained security-sensitive packages;
- dependency confusion/typosquatting risk;
- build scripts/postinstall hooks and downloaded executables;
- generated SBOM/provenance evidence where the project requires it.

Do not install or contact registries merely because this reference mentions scanning.

## Security tooling in SDLC

SAST, DAST, SCA, secret scanning, IaC/container scanners, and custom rules can be useful gates, but tune them for signal and verify material findings manually. A scanner configuration belongs to the governing repository/tooling workflow; this Tier 0 skill does not authorize new services, network calls, CI mutation, or runtime installation.

When a confirmed vulnerability is fixed, add a security regression test at the lowest level that reliably reproduces the exploit condition or violated invariant.

## Vulnerability triage

Prioritize using:

- exposure/reachability;
- attacker prerequisites and required privileges;
- exploit reliability;
- confidentiality/integrity/availability/business impact;
- blast radius and affected data/users;
- existing compensating controls;
- uncertainty/confidence.

CVSS/CWE/OWASP mappings can support consistency but do not replace contextual risk assessment. Do not import source-specific remediation SLAs as universal project deadlines.

## Threat-model handoff

For a feature/architecture change, derive testable security requirements from assets, data flows, trust boundaries, entry points, and abuse cases. If the question is mainly system-level control placement or trust architecture, hand to `security-architect` rather than duplicating that role.

## Verification and retest

For each confirmed finding:

1. preserve a safe reproducible failing condition where possible;
2. apply remediation through the governed implementation workflow;
3. rerun the same defensive test;
4. run relevant surrounding regression/security checks;
5. verify the control at the actual enforcement boundary;
6. record residual risk and anything that cannot be tested locally.

Never mark a vulnerability fixed because a patch looks plausible.

## Failure modes to challenge

- scanner result treated as confirmed exploitability;
- auth check without resource/action authorization;
- frontend validation treated as a server control;
- sanitization used instead of safe parameterized/sink APIs;
- CORS treated as authentication;
- secret deleted but not rotated after exposure;
- custom cryptography or home-grown token validation;
- global “security fix” that bypasses domain-specific policy;
- broad offensive testing beyond explicit authorization;
- weakening a control merely to make tests pass;
- compliance/coverage percentage reported as a security guarantee.

## Verification questions

- What untrusted value reaches what sensitive sink or privilege decision?
- Can another user/tenant alter or read the target resource?
- Does the control exist at the trusted enforcement boundary?
- Are security errors and logs safe yet diagnosable?
- Are confirmed findings represented by regression tests where practical?
- Were dependency/scanner results verified for reachability and configuration?
- Does remediation preserve existing authorization, data, and compatibility behavior?

## Specification-to-TDD composition

Trace security requirement → abuse case/observable failure → security invariant → owning application boundary → smallest remediation slice → lowest defensive failing test → RED → GREEN → REFACTOR → focused security regression + scanner/contract checks where governed → independent review → fresh verification → repository/KIS gate. This specialist advises; it does not authorize offensive actions, CI changes, credential use, or deployment.