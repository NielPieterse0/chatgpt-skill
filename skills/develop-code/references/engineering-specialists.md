# Engineering Specialist Routing

Use these Tier 0 specialists only for technical depth. Repository instructions and KIS, when present, remain the workflow, mutation, Git/GitHub, lifecycle, and completion authority.

| Need | Specialist | Contribution |
|---|---|---|
| Trace unfamiliar behavior | `explorer` | Entry points, execution paths, data flow, side effects, dependency evidence |
| Onboard to an unfamiliar repository | `engineering-codebase-onboarding-engineer` | Architecture, build/test surfaces, invariants, state, contracts, change seams |
| Cross-module architecture | `engineering-software-architect` | Boundaries, dependency direction, contracts, data ownership, resilience, evolution |
| Backend/system design | `engineering-backend-architect` | Transactions, persistence, async workflows, idempotency, caching, reliability, operability |
| API/platform contracts | `engineering-api-platform-engineer` | Schemas, compatibility, authz, idempotency, pagination, errors, quotas, SDK concerns |
| Security architecture | `security-architect` | Threat models, trust boundaries, identity, authorization, secrets, data protection |
| Requirement-linked proof | `evidence-engineering` | Observable criteria, fail-before/pass-after, evidence level, focused/broad verification |
| Minimize blast radius | `engineering-minimal-change-engineer` | Owning seam, compatibility, causal diff, rollback-friendly scope |
| Documentation-backed technical research | `docs-researcher` | Primary sources, version/freshness, claim tracing, conflict reconciliation |
| API verification | `testing-api-tester` | Contract, negative, authz, idempotency, pagination, concurrency, compatibility tests |
| Test automation strategy | `testing-test-automation-engineer` | Lowest appropriate level, deterministic fixtures, boundary realism, flake control |
| Performance evidence | `testing-performance-benchmarker` | Workloads, distributions, throughput, saturation, variance, bottleneck attribution |
| Ordinary independent review | `reviewer` | High-signal correctness, security, regression, edge-case, and test findings |
| Deep engineering review | `engineering-code-reviewer` | Invariants, concurrency, contracts, data, architecture, operability, regression depth |
| AI-assisted code audit | `security-ai-generated-code-auditor` | Hallucinated APIs, omitted controls, unsafe defaults, silent failure, weak tests |
| Application security | `security-appsec-engineer` | Injection, authorization, SSRF, browser, deserialization, path, secret, dependency risks |

## Composition

For specification-driven implementation, keep traceability from requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate.

Load only the specialist references needed for the current question. Do not merge these roles into one generic engineering skill, duplicate their technical bodies here, or treat any specialist as approval to mutate external state.