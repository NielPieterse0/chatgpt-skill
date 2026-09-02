# Security Architecture Technical Depth

Load this reference when the problem is architectural: assets, identities, trust boundaries, data flows, attack surfaces, control placement, blast radius, or security requirements. Use `security-appsec-engineer` for code-level vulnerability assessment/remediation and `security-ai-generated-code-auditor` for AI-generated-code-specific patterns.

## Security architecture starts with the system

Establish:

- protected assets and business impact;
- actors, identities, service principals, administrators, and external parties;
- data classification and lifecycle;
- entry points and externally reachable surfaces;
- data/control flows;
- trust boundaries and privilege transitions;
- dependencies, supply chain, and control-plane services;
- deployment/runtime topology where it changes trust or blast radius.

Do not start with a checklist of controls. First determine what must be protected, from whom, and where trust changes.

## Adversarial questions

For every component/boundary ask:

1. What can be abused rather than merely used incorrectly?
2. What happens when this component or control fails?
3. What privileges or data become reachable after compromise?
4. What is the blast radius?
5. Which assumptions does the design make about identity, network, client, operator, or dependency trust?
6. What evidence would falsify the assumption that this boundary is safe?

## Threat modeling

Use a structured method that fits the system. STRIDE is useful for systematically checking:

- spoofing / identity compromise;
- tampering / integrity violation;
- repudiation / insufficient accountability;
- information disclosure;
- denial of service / resource exhaustion;
- elevation of privilege.

PASTA, attack trees, misuse/abuse cases, or domain-specific methods may be better for some systems. The framework is a coverage aid, not the output.

For each threat record:

- affected asset/component/boundary;
- attacker position/prerequisites;
- attack path or abuse scenario;
- existing controls;
- likelihood/feasibility and uncertainty;
- impact and blast radius;
- residual risk;
- testable mitigation/security requirement.

## Trust-boundary analysis

Mark every transition where one party or component cannot safely assume the other's claims or input are trustworthy, including:

- Internet/client → edge/API;
- browser/mobile → server;
- API gateway → service;
- service → service;
- application → database/cache/queue;
- tenant/user → shared platform;
- CI/build → artifact/deployment;
- workload → cloud/control plane;
- application → third-party integration;
- model/agent → tool or external action.

At each boundary define authentication, authorization, validation, confidentiality/integrity, replay/idempotency, rate/resource controls, logging/audit, and failure behavior as applicable.

## Identity and authentication architecture

Separate identity proof from access policy.

Consider:

- human, workload, device, and service identities;
- credential issuance, storage, rotation, revocation, and recovery;
- federation/trust relationships;
- token audience/scope/lifetime and key trust;
- MFA/passkeys or stronger assurance where the risk warrants it;
- machine-to-machine identity and secretless/short-lived credential options;
- session/token theft and replay.

Do not prescribe one identity technology universally. Map assurance to threat and operational constraints.

## Authorization architecture

Choose policy structure from the resource/action model:

- RBAC for stable role-to-permission relationships;
- ABAC for contextual/resource attributes;
- relationship-based models where graph relationships drive access;
- policy-as-code or centralized decision services where consistency and auditability justify them.

Regardless of model:

- default deny;
- least privilege;
- server/trusted-side enforcement;
- tenant/resource/action-specific checks;
- explicit administrative break-glass behavior;
- policy-change auditability;
- no reliance on client-editable claims for privilege.

## Defense in depth

Layer controls so one failure does not become total compromise. Depending on the threat model this can include:

- edge/request filtering and resource limits;
- strong identity and authorization;
- schema/input validation;
- safe sink APIs and output encoding;
- network/workload segmentation;
- least-privileged service/database identities;
- encrypted/authenticated transport and protected stored data;
- secrets/key management;
- isolation/sandboxing;
- immutable/auditable security events;
- detection and recovery.

Avoid security theater: duplicate controls should reduce a specific residual risk, not merely increase checklist count.

## Secure failure and degradation

Model control failure explicitly:

- identity provider unavailable;
- authorization service unavailable;
- key/secrets service unavailable;
- logging/audit pipeline degraded;
- rate limiter/cache unavailable;
- dependency returns malformed or malicious data;
- network partition or stale policy/config;
- clock skew affecting token validity;
- incident disables a component.

Prefer fail-closed for authorization/security decisions unless a documented availability requirement justifies a carefully bounded alternative. Make emergency/break-glass paths explicit, auditable, time-bounded, and separately authorized.

## Data protection architecture

For sensitive data define:

- minimization and collection purpose;
- ownership/source of truth;
- classification and access policy;
- encryption/authentication in transit and at rest as warranted;
- key ownership/rotation/recovery;
- retention/deletion/backups;
- logs/telemetry redaction;
- data residency/segmentation requirements if applicable;
- export/download/admin access;
- non-production/test-data handling.

Cryptographic primitive and version choices should follow current project/security authority rather than stale hard-coded algorithms in source material.

## Network, workload, and cloud boundaries

Assess:

- ingress/egress policy;
- service-to-service identity and authorization;
- network segmentation and namespace/account/project boundaries;
- cloud IAM/service roles;
- public storage/databases/endpoints;
- metadata/control-plane access;
- container/workload privileges and host boundaries;
- multi-tenant isolation;
- administrative interfaces and control-plane credentials.

“Internal network” is not a sufficient trust boundary by itself.

## Supply-chain and build architecture

Map trust in:

- source repositories and protected branches;
- CI runners/build agents;
- dependency registries and lockfiles;
- generated code and code-generation tools;
- artifact provenance/signatures/digests;
- deployment identities;
- third-party actions/plugins/scripts;
- update/rollback channels.

A connected or popular supplier is not automatically trusted. Define verification and least privilege at each handoff.

## API and distributed-system security

At service/API boundaries consider:

- broken object/function authorization;
- replay/idempotency abuse;
- resource exhaustion and rate/cost limits;
- schema and version compatibility affecting security controls;
- webhook/event authenticity and replay;
- queue/topic permissions and poison messages;
- SSRF through integrations/fetchers;
- GraphQL/WebSocket/stream-specific resource and authorization behavior;
- observability across trust boundaries.

Use AppSec for code-level validation of these controls.

## AI/agent security architecture

When a model/agent can consume untrusted content or invoke tools, add trust boundaries for:

- user/retrieved/tool-provided content versus system/developer instructions;
- model output versus deterministic policy/validation;
- tool invocation authorization;
- credentials exposed to tools/runtime;
- filesystem/network/external-mutation scope;
- human approval for consequential actions;
- cross-origin resource/tool access;
- persistence/memory of untrusted content.

Treat model behavior as non-authoritative and potentially manipulable. Policy enforcement must live outside generated text where possible.

## Security requirements

Convert architectural threats into requirements that can be tested, for example:

- only the owning tenant can read resource X;
- service A can call operation B but not administrative operation C;
- failed token validation produces no application-side effect;
- webhook replay outside the accepted window is rejected;
- untrusted URL input cannot reach disallowed network ranges;
- a compromised low-privilege component cannot retrieve deployment credentials.

Avoid vague requirements such as “use encryption” or “follow zero trust.”

## Risk prioritization

Prioritize using exposure, prerequisites, exploitability, impact, blast radius, existing controls, detectability/recovery, and uncertainty. Standard scoring systems can aid consistency but do not replace contextual business/system impact.

## Failure modes to challenge

- checklist before system/data-flow understanding;
- network location treated as trust;
- authentication treated as authorization;
- shared admin/service credential with broad blast radius;
- control failure behavior left implicit;
- security control that cannot be tested or observed;
- threat model containing threats but no owner/testable mitigation;
- architectural advice drifting into unapproved active exploitation;
- exact algorithm/version recommendations copied as timeless policy;
- security architecture claiming compliance/readiness without governance evidence.

## Deliverable structure

Provide:

1. system/assets/actors summary;
2. trust-boundary/data-flow map;
3. prioritized threat/abuse scenarios;
4. current controls and gaps;
5. security architecture recommendations with trade-offs;
6. testable security requirements;
7. residual risks/assumptions;
8. handoffs to AppSec, identity, operations, or verification specialists.

## Verification questions

- Are all privilege and data transitions represented as trust boundaries?
- Can each material threat be tied to an asset and plausible path?
- Does every recommended control reduce a named risk?
- What happens when each critical security dependency/control fails?
- Is blast radius bounded after one component/credential compromise?
- Are requirements specific enough for defensive tests?
- Are implementation-level findings handed to AppSec rather than mixed into architecture authority?

## Specification-to-TDD composition

Trace security requirement → abuse case → architectural invariant/trust boundary → owning component/interface → smallest enforceable behavior slice → lowest defensive test → RED → GREEN → REFACTOR → integration/AppSec checks → independent security review → fresh evidence → governing repository/KIS gate. This skill defines architecture and requirements only; it does not authorize scanning external systems, credentials, production changes, or offensive exploitation.