# ChatGPT Skill Adoption

## Authority

`README.md` is the repository entry point. It explains **what the project is**, **why it exists**, and **how to get started**.

**Rule:** If it helps a new developer understand or start using the repository, it belongs here. Otherwise, place it in the appropriate authoritative document and link to it.

## Overview

This repository provides a controlled process for adopting selected high-value skills from the Codex global skills library. ChatGPT is the initial delivery target.

The project exists to make skill adoption explicit, reviewable, reproducible, and maintainable rather than relying on ad hoc copies or undocumented assumptions. Its adapter-driven architecture keeps the portable adoption model separate from host integration so a future Codex target can reuse the same canonical adopted skills and controls.

The live repository is the sole source of truth for accepted project state. The external Codex skills library and its index are read-only source inputs.

## Goals

- Identify useful candidate skills from the Codex global skills library.
- Evaluate scope, dependencies, compatibility, risks, and expected value before adoption.
- Adapt selected skills into repository-owned artifacts with clear provenance.
- Keep portable adoption logic independent from target-specific adapters, starting with ChatGPT and preserving a future Codex path.
- Validate adopted skills and their supporting documentation.
- Keep working rules, implementation knowledge, and project navigation in their proper authoritative locations.

## Current Status

The repository has completed its research-integration and P0 security baseline, and KIS Work Management is now the required tracked-work control plane. `develop-code` and `develop-docs` are admitted canonical Tier 2 project-content workflows. The global runtime kill switch remains disabled, so no skill is runtime-enabled.

The reconciliation queue is closed. There is no active implementation slice in the authoritative backlog. `modularity-assessment` is deferred until target behavioral execution and activation observability are available; the current `tdd-change-discipline` draft is not admitted because its mandatory gate/governance assumptions conflict with this repository; and GitHub governance enforcement is recorded as an external provider limitation without weakening repository policy. New adoption work must enter through issue-backed Work Management intake.

## P0 Security Baseline

The repository now enforces a fail-closed skill adoption boundary:

- only `skills/*/SKILL.md` is runtime-discoverable;
- `references/` and `.work/` are permanently excluded;
- every adopted skill requires `adoption-manifest.json` with provenance, license, capability, integrity, approval, and rollback records;
- Tier 3 and Tier 4 capabilities are prohibited;
- `allowed-tools`, hooks, remote MCP, runtime installation, credentials, network access, and external mutation are rejected;
- `config/runtime-control.json` is the emergency kill switch and starts disabled;
- Git metadata and the configured private `origin` are required for completion validation.

The authoritative rules are in [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md).

## Quick Start

```powershell
Set-Location C:\Projects\ChatGPT-skill
Get-Content .\AGENTS.md
Get-ChildItem
```

Review the external candidate index without modifying it:

```powershell
Get-Content C:\Users\piete\.codex\skills\skills-index.json
```

Before editing:

1. Read [`AGENTS.md`](AGENTS.md).
2. Inspect the live repository state and applicable nested instructions.
3. For skill work, read the [`research synthesis`](docs/research/skill-adoption-research-synthesis.md) and its linked package, security, evaluation, adapter, and backlog owners.
4. Identify the candidate skill and its source files.
5. Locate or create the authoritative specification, decision, plan, or validation documentation required for the change.

## Common Workflow

1. **Select** a candidate from the external skills index.
2. **Assess** its purpose, dependencies, compatibility, security implications, and maintenance cost.
3. **Decide** whether to adopt, adapt, defer, or reject it, recording the decision in the appropriate repository document.
4. **Implement** the smallest coherent repository-owned version.
5. **Validate** the adopted artifacts with targeted and repository-wide checks.
6. **Document** provenance, usage, limitations, and authoritative references without duplicating implementation guidance in this README.

## Work Management

Work for this repository is tracked by issue-backed records and projected into the shared GitHub user Project `NielPieterse0/1`. KIS Work Management in `C:\Projects\kis-mcp` is the operational control plane for reading, reconciling, and validating that lifecycle.

The machine-readable binding is [`settings/projects/chatgpt-skill.json`](settings/projects/chatgpt-skill.json). It records the KIS schema source, required capabilities and operations, the Project identity, and an exact-source safety rule: only records sourced from `NielPieterse0/chatgpt-skill` are mutation-eligible.

For each work item, read the source issue and current Project status before claiming it, use a clean issue worktree, keep lifecycle state current, complete required verification and review/merge, then close the source issue and reconcile its Project projection to `Done`. The issue remains the stable source identity throughout; stale Project state must be reconciled rather than silently treated as authoritative.

## Repository Structure
```text
AGENTS.md          Repository-wide execution contract
README.md          Project entry point and navigation
package.json       Fixed validation and catalog commands
.github/            CI, ownership, contribution, issue, and dependency automation
config/            Machine-enforced security policy and runtime kill switch
settings/          Repository-owned project and Work Management contract
schemas/           Adoption manifest contract
scripts/           Repository-owned validation and catalog tooling
skills/            Only runtime-discoverable adopted skills
references/        Untrusted source evidence and provenance material
docs/              Specifications, architecture, decisions, plans, standards, and operations
tests/             Automated security-gate tests
.work/             Temporary, generated, quarantine, and incident artifacts
```

`references/` and `.work/` are never skill discovery roots. `skills/` is tracked with its own README and admits only direct child skill directories that pass the security gate.

## Validation
Run the fixed repository checks:

```powershell
npm test
npm run verify-bootstrap  # controlled pre-Git bootstrap only
npm run verify            # required after Git origin is configured
npm run catalog           # returns an empty catalog while the kill switch is disabled
```

Direct validator commands are also available:

```powershell
python scripts/skill_security.py validate --repo .
python scripts/skill_security.py catalog --repo .
python scripts/skill_security.py hash skills/<skill-name>
```

For final review, also run `git diff --check` and inspect `git status --short`. Do not claim a check passed unless its command completed successfully. The one permitted pre-Git exception is `verify-bootstrap`; it does not satisfy completion validation.

## Authoritative Documentation

- [`docs/research/skill-adoption-research-synthesis.md`](docs/research/skill-adoption-research-synthesis.md): accepted research conclusions, requirements matrix, unresolved product questions, and output status.
- [`docs/standards/skill-package-standard.md`](docs/standards/skill-package-standard.md): canonical skill contents, progressive disclosure, resources, target overlays, and packaging exclusions.
- [`docs/testing/skill-evaluation-standard.md`](docs/testing/skill-evaluation-standard.md): trigger, output, efficiency, abuse, compatibility, and human-review gates.
- [`docs/plans/skill-adoption-implementation-backlog.md`](docs/plans/skill-adoption-implementation-backlog.md): dependency-ordered work for the first prototype, ChatGPT adapter, package validation, and future targets.
- [`docs/operations/github-repository-hygiene.md`](docs/operations/github-repository-hygiene.md): accepted GitHub repository settings, main-branch controls, automation, and closeout checklist.
- [`SECURITY.md`](SECURITY.md): private vulnerability reporting and immediate containment.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): contribution and pull-request workflow.

- [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md): P0 trust zones, capability tiers, provenance, admission, discovery, disablement, validation, and incident-containment rules.
- [`schemas/skill-adoption-manifest.schema.json`](schemas/skill-adoption-manifest.schema.json): machine-readable adoption record contract.

- [`references/skills-knowledge-source-register.md`](references/skills-knowledge-source-register.md): curated hierarchy of Agent Skills specifications, product documentation, implementations, catalogs, security standards, evaluation research, and adoption-source requirements.
- [`docs/research/chatgpt-skill-adoption-deep-research-brief.md`](docs/research/chatgpt-skill-adoption-deep-research-brief.md): focused research scope for the portable skill package, ChatGPT coding-agent architecture, security controls, scripts, references, evals, and implementation decisions.

- [`AGENTS.md`](AGENTS.md): repository-wide behavioral rules, required workflow, constraints, validation expectations, and completion criteria.
- [`docs/architecture/skill-runtime-adapters.md`](docs/architecture/skill-runtime-adapters.md): authoritative ChatGPT-first adapter strategy and the boundary between portable adoption logic and target-specific integration.
- [`docs/architecture/import-isolate-handoff.md`](docs/architecture/import-isolate-handoff.md): responsibility boundary for externally acquired source material and finalized `import-isolate` handoffs.
- `docs/`: other product, architecture, decision, planning, coding, testing, and operational documents, when added.
- Nested `AGENTS.md` files: path-specific working rules, when added.
- Adopted skill directories: skill-specific implementation and usage documentation.

This README should link to authoritative documents as they are introduced rather than duplicate them.

## Contributing

Keep changes scoped, preserve unrelated work, follow the applicable `AGENTS.md`, update the relevant authoritative documentation, and include evidence for every validation claim.
