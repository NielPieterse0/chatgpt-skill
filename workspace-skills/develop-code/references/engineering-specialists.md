# Engineering Specialist Routing

Use these Tier 0 specialists for technical depth inside the governing `develop-code` / repository / KIS workflow. They do not own work claiming, mutation authority, Git/GitHub actions, lifecycle state, approval, or completion.

## Routing rule

Choose by **current stage + concrete uncertainty**, not by loading the entire tranche. Prefer one primary specialist. Add a secondary specialist only when the task genuinely crosses a boundary, then hand back to the governing development workflow.

| Stage | Trigger / uncertainty | Primary specialist | Contribution | Boundary / hand-off |
|---|---|---|---|---|
| Repository orientation | New or unfamiliar repo; contributor needs architecture/build/test/state map | `engineering-codebase-onboarding-engineer` | Three-level repo map, boot sequence, boundaries, state/contracts, essential files | Use `explorer` for one specific feature path |
| Existing-behavior discovery | Feature/request/event/command path is unclear before design/change | `explorer` | Exact execution + data flow, state, side effects, dependencies, errors | Hand judgment to architect/reviewer; no edits |
| Documentation research | A technical decision depends on official docs/spec/version/freshness | `docs-researcher` | Primary-source hierarchy, claim tracing, normative/version reconciliation | Hand observed repository behavior to `explorer` |
| Cross-module/system design | Boundary, dependency direction, domain/data ownership, quality-attribute trade-off | `engineering-software-architect` | DDD/pattern selection, architecture seams, ADR/evolution reasoning | Hand backend/API/security detail to those specialists |
| Backend/service design | Transactions, persistence, queues/jobs, caching, retries, migrations, reliability | `engineering-backend-architect` | Data/transaction semantics, async delivery, migration, time budgets, SLO/operability | Public API lifecycle → API platform; system topology → software architect |
| API/platform design | Public/partner/service API contract, compatibility, versioning, pagination, idempotency, quotas, SDK DX | `engineering-api-platform-engineer` | Contract-first semantics, breaking-change/deprecation analysis, retry/error/client behavior | Verification → `testing-api-tester`; backend internals → backend architect |
| Security architecture | Trust boundaries, identities, authorization model, data/control-plane security, blast radius | `security-architect` | Threat modeling and testable control architecture | Code-level flaws → AppSec; generated-code patterns → AI auditor |
| AppSec review/hardening | Concrete application attack surface or code-level vulnerability concern | `security-appsec-engineer` | Source-to-sink analysis, authz, injection/browser/SSRF/path/secrets/dependencies, regression requirements | System control placement → security architect |
| AI-assisted code audit | Generated/scaffolded code may contain secret/RLS/authz/prompt/tool/default/hallucinated-API failures | `security-ai-generated-code-auditor` | Generated-code-specific security patterns, redacted findings, scan-fix-rescan evidence | Broader application security → AppSec |
| Implementation scoping | Change is at risk of unnecessary blast radius, cleanup, abstraction, or speculative flexibility | `engineering-minimal-change-engineer` | Smallest causal seam/diff while preserving root cause, safety, compatibility, tests | Architecture repair still required when causal boundary demands it |
| Evidence design | Requirement/completion claim needs defensible fail-before/pass-after proof | `evidence-engineering` | Claim→criterion→evidence mapping, evidence level/scope/freshness | Verification execution remains with governing workflow/tools |
| Test strategy | Need to decide what to automate, at what level, and how to keep it deterministic | `testing-test-automation-engineer` | Lowest reliable test level, fixtures, selectors, waits, flake/parallel/artifact strategy | API/perf depth → their specialists |
| API verification | Contract/authz/idempotency/pagination/concurrency/compatibility behavior must be falsified | `testing-api-tester` | Functional/negative/boundary/contract/integration API tests | Contract design → API platform; serious load → performance |
| Performance verification | Latency/throughput/saturation/capacity/regression claim needs reproducible evidence | `testing-performance-benchmarker` | Workload model, distributions, variance, bottleneck attribution, recovery/capacity | Do not optimize before evidence |
| Ordinary independent review | Bounded change needs high-signal defect review | `reviewer` | Precision-first correctness/security/regression/test findings | Deep architecture/concurrency/migration/operability → engineering reviewer |
| Deep engineering review | Complex/high-risk change spans invariants, data, concurrency, contracts, architecture, operability | `engineering-code-reviewer` | Deep falsification and prioritized evidence-backed findings | Security specialist may supplement attack-surface depth |

## Common compositions

Use compositions only when the boundary actually crosses:

- **Unfamiliar repo → feature change:** `engineering-codebase-onboarding-engineer` → `explorer` → relevant architect/domain specialist.
- **Specification-driven implementation:** architecture/domain specialist → `engineering-minimal-change-engineer` for scope discipline → TDD workflow → `evidence-engineering` → review.
- **API change:** `engineering-api-platform-engineer` + backend architect when storage/retry/async semantics matter → `testing-api-tester` → evidence/review.
- **Security-sensitive change:** `security-architect` for system controls → `security-appsec-engineer` for code enforcement → AI auditor only when generated-code-specific patterns apply → defensive regression evidence.
- **Performance-sensitive change:** backend/software architecture as needed → `testing-performance-benchmarker`; do not begin by optimizing from generic thresholds.
- **Review escalation:** start with `reviewer`; escalate to `engineering-code-reviewer` only for material deep-system concerns rather than loading both by default.

## Specification → TDD trace

For implementation work preserve:

requirement → observable acceptance criterion → domain/security/performance invariant → owning module/architectural boundary → smallest independently deliverable behavior slice → lowest appropriate test level → concrete failing test → RED → GREEN → REFACTOR → relevant boundary/contract/integration checks → independent review → focused fresh verification → repository/KIS gate.

Specialists provide knowledge at the relevant node in this trace. They do **not** replace Superpowers/TDD/debugging/review/verification workflow authority or KIS lifecycle controls.

## Routing anti-patterns

- Do not load all 16 “for completeness.” Progressive disclosure is the design.
- Do not use a reviewer to discover a feature that has not yet been traced.
- Do not ask API tester to design public compatibility policy or API platform engineer to grade test execution.
- Do not use test automation to justify browser/E2E when a lower level crosses the relevant boundary.
- Do not use minimal-change discipline to avoid a necessary root-cause, migration, security, or architectural fix.
- Do not infer approval/completion because one or more specialists agree.