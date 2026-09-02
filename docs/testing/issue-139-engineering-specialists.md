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
## Corrective full-depth redo — 2026-09-02

This corrective iteration starts from accepted `origin/main` `f8c538ded741aa86f1a8a11c3a633e2f4c99cf39`. The prior implementation and #146 human KIS-harmony approval remain historical evidence for `6f2a5ac62dc4a758654ab35c011ade9c632d4fe3`; they are not silently rebound to changed bytes.

Loaded skill-development methods: `create-skill`, `writing-skills`, `evaluate-skill`, and `improve-skill`. The optional `plugin-eval` CLI was not installed on this execution surface, so no plugin-eval report is claimed; repository-owned evaluation and security standards remain authoritative.

### Corrective adopted-content identities

| Package | Adopted-content SHA-256 |
|---|---|
| `explorer` | `37ef9ed68bbf76baa73cb013e82e24ce0b9572c11dc58e5694d79d2f461cf244` |
| `engineering-codebase-onboarding-engineer` | `2001667e6d2dacbcd45738ea1d52c7fb915ea265bd3934bfebf66742f589cc2a` |
| `engineering-software-architect` | `4390a76dc718904622b00879973f3007ab31f66408b468edc5af4863e3e277f8` |
| `engineering-backend-architect` | `a1b8765a11de29b9a3b70155c4532cb88c8d60bbac60a10623462b88f6f3bf4a` |
| `engineering-api-platform-engineer` | `495e279fd63178c1564bbdef8f747f1827d378e2d115db8127de0663bc7f7d29` |
| `security-architect` | `2b5b3791af40568781e80bd5fb3e7eebad29bfba882344b5660f053c42e4d114` |
| `evidence-engineering` | `5cf358b94788ed8e9aa83d839482677609303a25c46a3ce3ec3709c97558d1f5` |
| `engineering-minimal-change-engineer` | `586d419647320fe9aad6533488212eae94f3159c58f3bfd40b431d3656fec847` |
| `docs-researcher` | `f3482a6eae07b7a56835bcad329b5720292ef0972ace075aa4a6a88ca3a40017` |
| `testing-api-tester` | `f6e3f8bd0689812efe91b40738e34d59779f5269add575dfe0f7650f776500b6` |
| `testing-test-automation-engineer` | `1835f19024d67c2de1492b35c063efbdd873c1c7244b650ab98091ca6fc933e2` |
| `testing-performance-benchmarker` | `a6a24f73eee14c29e7b330a70b3db0967b0a5f229c739aaa7b2cafca7f486c5e` |
| `reviewer` | `f25911c59c4d264843459703ae16d8cf4f978d1e603a5bdc949c7295127fb9c0` |
| `engineering-code-reviewer` | `eab8815c39aec8566fe47339301022df1479cc62ea2d10d8ac424b615e6969e4` |
| `security-ai-generated-code-auditor` | `ce2ca6e46b616bd72b5dc80d6198c68e21e54e4ccd8c1f66f39814b753d60417` |
| `security-appsec-engineer` | `858d752272e8181dd9205207549cc447bfc5d9fab808f738551805a9642c2891` |
| `develop-code` routing package | `d40076f2789b32feb94be37874f6eee0aecb8f6e0da40f59b2aca3c1ad2f9539` |

### Fresh evaluation and verification boundary

The tracked definitions are unchanged from `f8c538ded741aa86f1a8a11c3a633e2f4c99cf39`. Each of the 16 specialists still has 16 trigger cases (6 positive, 6 near-miss, 2 conflict, 2 prompt-injection), 3 output cases against `no-skill`, and 8 abuse cases. This proves definition coverage only; it does not synthesize target-runtime behavioral results.

Fresh deterministic checks on the corrective bytes passed: adopted-content hashing for all 16 specialists plus the changed `develop-code` router; `python scripts/skill_security.py validate --repo .`; `python scripts/project_contract.py validate --repo .`; `npm run verify-compliance`; `git diff --check`; and full `npm run verify` with 261 tests passing and 4 platform-permission skips. The full verify also passed project contract, compliance, catalogue-evaluation, plugin-portfolio, intake, security, and catalogue generation.

Target-isolated automatic activation/output observability was not newly available in this run. No new trigger-rate, output-quality, efficiency, or runtime-compatibility pass is claimed. The corrective release decision therefore relies only on deterministic package/security/evaluation-definition evidence plus the explicit review evidence recorded for the corrective diff; any later target surface that exposes reliable isolated behavioral observability must rerun the unchanged tracked cases against these exact hashes.

The omission/adaptation review for the redo is recorded in [`issue-139-engineering-specialist-omissions.md`](issue-139-engineering-specialist-omissions.md). An unlisted material source omission remains a defect rather than an implicit simplification.