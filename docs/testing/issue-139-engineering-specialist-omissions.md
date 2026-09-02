# Issue 139 engineering specialist omission and adaptation ledger

This is the single review surface for meaningful source details intentionally not carried into the 16 Tier-0 specialist runtime packages, or deliberately changed during the full-depth redo. It prevents silent detail loss while keeping source persona, unsafe authority, brittle universal targets, and stale/vendor-specific prescriptions out of repository-owned instructions.

## Global exclusions across the tranche

| Source detail intentionally excluded or adapted | Reason | Restore only if |
|---|---|---|
| Persona, vibe, emoji/color, role-play identity, praise/encouragement instructions, autobiographical experience claims | Not technical knowledge; consumes context and can bias behavior | User explicitly wants persona behavior in a separate policy layer |
| “Memory” and “learning” claims | Models do not gain durable skill-local memory from these statements; would misrepresent runtime capability | A real governed persistence mechanism owns it |
| Source-specific `tools`, `model`, or equivalent client frontmatter | Agent Skills package authority and repository runtime controls own capabilities | Target adapter explicitly requires a permitted mapping |
| Network, credential, install, CI mutation, deployment, publication, external scanning, or lifecycle instructions | Tier 0 skills are knowledge/advisory only; source evidence cannot grant authority | Separate governing workflow explicitly authorizes the action |
| Raw live-looking secrets, exploit payloads, destructive examples, or copy-paste offensive recipes | Unnecessary risk; mechanisms are preserved defensively in prose/test requirements | A separately authorized defensive lab needs a bounded fixture |
| Generic numeric “success metrics” and fixed targets not grounded in this project (latency, coverage, 10x traffic, flake %, suite minutes, remediation days, etc.) | Examples in source are not universal engineering requirements | A project/product SLO, standard, or accepted issue explicitly adopts the value |
| Vendor/tool-specific CI/install snippets | Can become stale and improperly transfer execution authority | The repository already uses the exact tool/version and a governed implementation task needs it |
| Source statements that treat one architecture/tool/pattern as universally required | Conflicts with evidence-driven trade-off discipline | A governing project decision makes it mandatory |
| Repeated generic explanations already supplied by base model knowledge | Progressive disclosure should spend context on non-obvious specialist detail | Evaluation shows the omitted explanation materially improves behavior |

## Per-skill review ledger

### `docs-researcher`

Preserved: official/primary-source hierarchy; normative versus explanatory evidence; version/freshness identity; claim-to-source mapping; conflict reconciliation; primary repository evidence; documented/observed/inferred/unknown states; untrusted-document boundary.

Intentionally excluded/adapted:

- The source handoff's `license: project-owned` wording is retained as existing package metadata for now rather than being treated as technical method. License normalization is a repository/package-governance decision, not part of this technical-depth redo.
- No generic web-search or command-execution procedure was added; source material remains evidence, not authority.

### `engineering-api-platform-engineer`

Preserved: contract-first design; additive versus breaking change classes; semantic compatibility; version/deprecation lifecycle; error contracts; rate-limit observability; idempotency/retry semantics; pagination trade-offs; authentication versus authorization; SDK/generated-client compatibility; OpenAPI/protobuf/GraphQL evolution; developer experience and deprecation telemetry.

Intentionally excluded/adapted:

- Fixed “public APIs: 6–12+ months” deprecation runway is not universal; the package requires a consumer-appropriate runway and measurable exit criteria.
- `X-RateLimit-*` headers are treated as examples rather than mandatory names; documented protocol/vendor semantics govern.
- “Every API needs a typed SDK and portal” is conditional on consumer/platform needs, not a universal requirement.
- Source marketing/success metrics and persona language are excluded.

### `engineering-backend-architect`

Preserved: monolith/modular-monolith/microservice/serverless trade-offs; transactions/invariants; schema/index reasoning; expand-contract migration; backfill/reconciliation/rollback; time budgets; retries/backoff/jitter/idempotency; circuit/bulkhead concepts; queue delivery/ordering/DLQ/replay; caching consistency; contracts; structured observability/SLOs/tracing; backup/restore; database/performance attribution.

Intentionally excluded/adapted:

- Source fixed targets such as sub-20ms queries, sub-200ms APIs, 99.9% uptime, and 10x traffic are omitted as universal requirements.
- Hard-coded Kubernetes/multi-cloud/serverless prescriptions and illustrative ecommerce schemas are not copied verbatim; underlying mechanisms are retained.
- “WebSocket guaranteed ordering” is not treated as a generic promise; ordering must be explicitly designed per transport/system.

### `engineering-code-reviewer`

Preserved: correctness/security/maintainability/performance/test review; prioritized evidence-backed findings; invariants; concurrency; data migration; contracts; authorization; operability; test quality; architecture/dependency direction; candidate-finding falsification.

Intentionally excluded/adapted:

- Upstream emoji blocker/suggestion/nit formatting is not mandatory.
- A hard numerical confidence cutoff is not repository authority; high-confidence filtering is retained without inventing a universal threshold.
- “Praise good code” persona coaching is not a review-quality requirement.

### `engineering-codebase-onboarding-engineer`

Preserved: code-first facts; one-line / five-minute / deep-dive output; manifests/entry points; execution and data flows; boundaries/ownership; state/contracts; polyglot/monorepo/framework boot recognition; essential-file set; inspected/uninspected limits.

Intentionally excluded/adapted:

- Source says “avoid inference completely.” This is changed to **label inference** because architecture/ownership can sometimes only be inferred from wiring/import/contracts; presenting it as fact remains prohibited.
- “Things that look important but aren't” requires evidence; no dead-code declaration from naming/search alone.
- No implementation/refactor suggestions are added to onboarding; they route to the relevant specialist.

### `engineering-minimal-change-engineer`

Preserved: smallest causal diff; scope verbs; no “while I'm here” changes; follow-up separation; root-cause placement; compatibility/migration obligations; line/hunk necessity review; resistance to speculative abstractions/configuration/defensive code.

Intentionally excluded/adapted:

- “If you open a fourth file, stop” is too brittle and can prevent correct root-cause tracing.
- “Extract only at the fourth occurrence” is retained only as a warning against premature abstraction, not a numeric law.
- Fixed goals such as median diff <30 lines or 80% of fixes touching ≤2 files are omitted as universal metrics.
- “Delete it and see what breaks” is not a default dead-code technique because test completeness and user work cannot be assumed.

### `engineering-software-architect`

Preserved: DDD bounded contexts/aggregates/entities/value objects/domain services/events/repositories/anti-corruption layers; layered/hexagonal/onion/modular-monolith/microservice/event/CQRS trade-offs; inward dependency direction; data ownership; quality attributes; reversibility/evolution; ADRs; diagrams as communication aids.

Intentionally excluded/adapted:

- Event storming and C4 are useful methods, not mandatory architecture procedures.
- Microservices/event-driven/CQRS are never badges/defaults; the source pattern table is converted into constraint-driven selection.
- Persona/experience claims are excluded.

### `evidence-engineering`

Preserved: claim→evidence mapping; strongest practical evidence source; deterministic-first validation; fail-before/pass-after; explicit evidence scope; telemetry limits; negative/absence evidence; artifact/hash freshness; human review distinction; pass/fail/unverified triage.

Intentionally excluded/adapted:

- Screenshots are explicitly limited to claims they can directly demonstrate; they are not promoted to general completion proof.
- Evidence collection does not authorize running applications, mutation, or external publication.

### `explorer`

Preserved: feature discovery; execution and data-flow tracing; architecture layers; dependencies; state/side effects; error paths; indirection/binding; key algorithms/technical considerations where inspected; essential-file output; line/file evidence.

Intentionally excluded/adapted:

- Anthropic source `tools`/`model` frontmatter is not adopted.
- Technical-debt/improvement observations are allowed only as evidence-backed secondary observations; actual review/redesign routes to reviewer/architect to prevent scope bleed.
- WebFetch/WebSearch/Bash authority from the source is not transferred.

### `reviewer`

Preserved: bounded change scope; explicit project guideline compliance; bug/security/performance/test review; high-confidence filtering; concrete file/location + rationale + fix direction; one-pass high-signal feedback.

Intentionally excluded/adapted:

- Claude-specific `CLAUDE.md` assumption is generalized to the repository's active instructions.
- Source model/tool frontmatter is excluded.
- The source's “confidence ≥80” remains a useful provenance detail but is not made an immutable repository threshold.
- Praise/encouragement and emoji formatting are excluded.

### `security-ai-generated-code-auditor`

Preserved: client-exposed/hardcoded secrets; public-versus-privileged key distinction; provider rotation requirement; Supabase/Postgres RLS failure patterns including blanket allow policies; privileged `service_role` exposure; client-editable authorization metadata; LLM system-prompt/tool sinks; hallucinated/deprecated API checks; silent failures; scan→fix→rescan; stable fingerprints; secret redaction; honest heuristic confidence; CWE/LLM taxonomy as mapping, not proof.

Intentionally excluded/adapted:

- No raw secret values or exploit payload strings are copied.
- Provider-specific dashboard steps are not encoded; rotation is required through the governed provider workflow.
- Claims such as “audited thousands of apps” and assistant-specific personality language are excluded.
- Local scanner execution/network assumptions from source are not adopted as authority.

### `security-appsec-engineer`

Preserved: security-critical path review; authentication and resource/action authorization; injection; XSS/CSRF/browser boundaries; SSRF; path/upload/archive handling; deserialization; secrets/crypto; business logic/race; dependency/supply chain; scanner verification; security regression tests; contextual exploitability/blast-radius triage; retest.

Intentionally excluded/adapted:

- Source remediation SLAs (e.g. Critical 7 days / High 30 days / Medium 90 days) are organization policy examples, not universal deadlines.
- Training/security-champion program advice is not core code-review method and is omitted from the runtime specialist.
- Exact crypto algorithm/version examples are not timeless policy; use current governing security authority.
- Copy-paste offensive payloads and scanner installation/config snippets are not carried into Tier 0 instructions.

### `security-architect`

Preserved: assets/actors/data flows/trust boundaries; STRIDE and alternative threat-model methods; blast radius; identity and authorization models; least privilege/default deny; defense in depth; secure failure; data protection; network/cloud/workload; supply chain/build trust; distributed/API and AI-agent trust boundaries; testable security requirements; residual risk.

Intentionally excluded/adapted:

- Source mixes architecture with code-level SAST/DAST and vulnerability exploitation; those are separated to AppSec and governed security tooling.
- Fixed algorithm/version prescriptions such as TLS/AES examples are not encoded as permanent universal rules.
- Scanner/CI/CD and active security-testing recipes are excluded from this advisory architecture role.
- CVSS/OWASP/CWE labels support consistency but are not treated as proof or lifecycle authority.

### `testing-api-tester`

Preserved: functional/negative/boundary tests; schema/contracts; authentication/authorization; injection/resource-abuse boundaries; idempotency/retry/concurrency; pagination under mutation; errors/rate limits; compatibility; third-party/webhook behavior; documentation examples; deterministic data/isolation; performance handoff.

Intentionally excluded/adapted:

- Fixed source requirements such as 95% endpoint coverage, <200ms p95, 10x traffic, <0.1% errors, 90% automation, and <15-minute suite are not universal.
- Destructive SQL-injection payload examples are not copied; safe defensive rejection tests preserve the mechanism.
- Production monitoring/alert setup is not authorized by a Tier 0 test-design skill.
- “Every API must pass performance/security validation” is interpreted according to actual API risk/requirements rather than an unbounded universal campaign.

### `testing-performance-benchmarker`

Preserved: baseline-first method; realistic workload modeling; load/stress/spike/endurance/scalability classes; latency distributions and resource metrics; statistical variance/confidence discipline; bottleneck attribution; queueing/saturation/recovery; database/cache/distributed-system performance; capacity planning; before/after regression method; synthetic versus RUM distinction; modern web-performance concepts.

Intentionally excluded/adapted:

- Source fixed targets (LCP <2.5s, FID <100ms, CLS <0.1, 25% gains, 10x load, 90% etc.) are not universal acceptance criteria.
- **FID is explicitly treated as legacy**; current Core Web Vitals responsiveness uses INP, and current thresholds must be checked against authoritative web-performance docs when needed.
- k6/CI/monitoring implementation snippets are not copied as execution authority.
- ROI/conversion claims from generic source examples require actual business evidence before use.

### `testing-test-automation-engineer`

Preserved: lowest reliable test level/test pyramid; Playwright/Cypress domain depth; no hard sleeps as default synchronization; condition/web-first waits; semantic role/label selectors then stable test IDs; API/direct setup for unrelated prerequisites; per-test/worker data ownership; fixture scope; mocks versus real boundaries; flake taxonomy; retries as measurement rather than treatment; quarantine/root-cause; trace/screenshots/video/logs; sharding/parallel isolation; visual-regression lane; suite health and selective execution.

Intentionally excluded/adapted:

- Fixed “10 consecutive runs,” quarantine-within-24-hours, retries=0/1, 99.5% pass, <0.5% flake, and <10-minute suite targets are not universal repository rules.
- GitHub Actions/npm install/upload snippets are not adopted; actual repository CI/toolchain governs.
- “No hard sleeps ever” is narrowed: time delay can be the behavior under test, preferably via a controllable clock; otherwise condition-based synchronization is the default.
- Framework API names are examples whose current-version correctness must be verified before policy use.

## User review outcome

Anything in this ledger can be reconsidered individually. Restoring a detail should answer one of three questions first:

1. Is it durable technical knowledge rather than persona or generic filler?
2. Is it a project-specific requirement rather than an upstream example/metric?
3. Can it be restored without transferring runtime, credential, network, mutation, publication, deployment, or lifecycle authority?

Details not listed here are intended to be represented either in the skill entrypoint or its `references/technical-depth.md`. A future fidelity review should treat an unlisted material omission as a defect.