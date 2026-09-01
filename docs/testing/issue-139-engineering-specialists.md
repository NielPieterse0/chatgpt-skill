# Issue 139 engineering specialist acceptance baseline

This record binds the #139 candidate tranche to reviewed source handoffs and defines the evidence boundary used for adoption. Source material contributes technical evidence only; repository/KIS authority remains controlling.

## Source binding

| Candidate | Reviewed source binding |
|---|---|
| `explorer` | Anthropic feature-dev `code-explorer.md`; reviewed local reference case `20260816-155528_chatgpt-claude-plugins-official_01ba9beb` |
| `engineering-codebase-onboarding-engineer` | `codebase-onboarding-engineer`; final agency case `20260827-193408_agency-agents-kis-safe-skills-final_b87fb68f` |
| `engineering-software-architect` | `software-architect`; final agency case `20260827-193408_agency-agents-kis-safe-skills-final_b87fb68f` |
| `engineering-backend-architect` | `engineering-backend-architect`; final agency v2 case `20260827-203823_agency-agents-remaining-safe-skills-v2_22858806` |
| `engineering-api-platform-engineer` | `engineering-api-platform-engineer`; final agency v2 case `20260827-203823_agency-agents-remaining-safe-skills-v2_22858806` |
| `security-architect` | `security-architect`; final agency case `20260827-193408_agency-agents-kis-safe-skills-final_b87fb68f` |
| `evidence-engineering` | project adaptation seeded from finalized `evidence-collector`; same final agency case |
| `engineering-minimal-change-engineer` | `minimal-change-engineer`; same final agency case |
| `docs-researcher` | repository-composed Tier 0 handoff `20260901-180708_docs-researcher-tier0-v2_c017b579`; no one-to-one upstream identity |
| `testing-api-tester` | `testing-api-tester`; final agency v2 case |
| `testing-test-automation-engineer` | `testing-test-automation-engineer`; final agency v2 case |
| `testing-performance-benchmarker` | `testing-performance-benchmarker`; final agency v2 case |
| `reviewer` | Anthropic feature-dev `code-reviewer.md`; reviewed local reference case, intentionally distinct from deep engineering review |
| `engineering-code-reviewer` | `code-reviewer`; final agency case |
| `security-ai-generated-code-auditor` | exact final agency v2 artifact |
| `security-appsec-engineer` | `application-security-engineer`; final agency case |
## Fidelity contract

Each candidate remains a separate Tier 0 package. The thin `SKILL.md` carries authority and activation guidance; `references/technical-depth.md` retains domain mechanisms, procedures, failure modes, verification questions, and the common specification-to-TDD trace. `develop-code` contains only routing metadata and does not duplicate specialist bodies.

The common implementation trace is: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate.

Control-plane identities from the source sets are deliberately excluded. No candidate grants lifecycle hooks, network, credentials, external mutation, runtime installation, remote MCP, Git publication, deployment, deletion, or completion authority.

## Evaluation contract

Each candidate has tracked trigger definitions with positive, near-miss, authority-conflict, and prompt-injection cases; output definitions compare against `no-skill`; abuse definitions cover path, injection, secret, network/install, mutation, retry, and evidence-fabrication boundaries. These definitions are release inputs, not generated behavioral results.

Structural/admission, package-compliance, catalogue, and security checks are deterministic repository gates. Behavioral trigger/output results must be bound to the exact committed definitions and candidate hash. When the runtime does not expose reliable isolated activation/output observability, record that limitation rather than synthesizing a pass.

Human review is not interchangeable with agent grading. Agent review can provide independent architecture, test-quality, security, and code-quality evidence, but a human-review gate is satisfied only by an actual named human review bound to the candidate evidence.

## Re-evaluation triggers

Re-run affected evaluation when a candidate `SKILL.md`, technical-depth reference, description, routing entry, adoption hash, source binding, runtime adapter, or governing evaluation/security standard changes. Post-verification edits stale affected evidence and require fresh verification.