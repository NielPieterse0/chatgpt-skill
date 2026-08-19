# ChatGPT Skill Adoption

## Authority

`README.md` is the repository entry point. It explains **what the project is**, **why it exists**, and **how to get started**.

**Rule:** If it helps a new developer understand or start using the repository, it belongs here. Otherwise, place it in the appropriate authoritative document and link to it.

## Overview

This repository provides a controlled process for evaluating, adapting, validating, and maintaining selected high-value skills. ChatGPT is the initial delivery target.

The shared Projects workspace catalogue is `C:\Projects\.agents\skills`. It is the canonical operational catalogue used by KIS Skills, while this repository remains the source of truth for its own accepted adoption decisions, runtime packages, security controls, and evaluation evidence. Catalogue presence does not itself grant repository runtime admission or enablement.

The Codex library at `C:\Users\piete\.codex\skills` and other source corpora are candidate inputs. Skills created or maintained there must still be deliberately reviewed before workspace or repository adoption.

The project exists to make skill adoption explicit, reviewable, reproducible, and maintainable rather than relying on ad hoc copies or undocumented assumptions. Its adapter-driven architecture keeps the portable adoption model separate from host integration so a future Codex target can reuse the same repository-owned canonical skills and controls.

## Goals

- Identify useful candidate skills from the shared workspace, Codex, repository-local, and other approved source surfaces.
- Evaluate scope, dependencies, compatibility, risks, overlap, and expected value before adoption.
- Adapt selected skills into repository-owned artifacts with clear provenance when repository runtime admission is required.
- Keep shared workspace catalogue state explicit and separate from repository runtime state.
- Keep portable adoption logic independent from target-specific adapters, starting with ChatGPT and preserving a future Codex path.
- Validate adopted skills and their supporting documentation.
- Keep working rules, implementation knowledge, and project navigation in their proper authoritative locations.

## Current Status

The repository has completed Changes 001–026, including KIS Work Management integration, repository/catalogue reconciliation, canonical workspace compliance and portability remediation, the KIS-governed three-skill GitHub pack, retirement of superseded GitHub workflow skills, retained-worktree reconciliation, and restoration of KIS-aligned `develop-code`, `develop-docs`, and `mcp-development` catalogue packages. The verified reconciliation baseline is `main` at `66912c994f94a7da67e6b92e01279f5ed03778ed`; GitHub Actions `Verify` run `31776682295` passed for that exact revision on 14 August 2026.

Repository runtime authority remains separate from shared workspace catalogue authority. `develop-code` and `develop-docs` are admitted repository Tier 2 project-content workflows, but `config/runtime-control.json` remains fail-closed with `skills_enabled: false`, so no repository skill is runtime-enabled merely because it is present in either catalogue. `modularity-assessment` remains approved for shared workspace catalogue adoption while its separate repository runtime release decision stays deferred pending the evaluation gates already recorded by this repository.

The previous cleanup and consolidation queue is closed. The next active milestone is Change 028 / issue #42, which hardens the shared skill-authority lifecycle from create → evaluate → improve → verify/admit/maintain. Its work is finding-first and must be split into bounded implementation slices when materially independent changes are discovered. The historical dirty `NielPieterse0/adopt-modularity-assessment` checkout remains preserved evidence and is not accepted current repository state.

## P0 Security Baseline

The repository enforces a fail-closed repository-runtime adoption boundary:

- only `skills/*/SKILL.md` is repository runtime-discoverable;
- `references/` and `.work/` are permanently excluded;
- every repository-adopted skill requires `adoption-manifest.json` with provenance, license, capability, integrity, approval, and rollback records;
- Tier 3 and Tier 4 capabilities are prohibited;
- `allowed-tools`, hooks, remote MCP, runtime installation, credentials, network access, and external mutation are rejected;
- `config/runtime-control.json` is the emergency kill switch and remains disabled;
- Git metadata and the configured private `origin` are required for completion validation.

The authoritative rules are in [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md).

## Quick Start

```powershell
Set-Location C:\Projects\ChatGPT-skill
Get-Content .\AGENTS.md
Get-ChildItem
```

Inspect the shared canonical workspace catalogue without modifying it:

```powershell
Get-ChildItem C:\Projects\.agents\skills -Directory
```

Inspect the Codex candidate source when relevant:

```powershell
Get-Content C:\Users\piete\.codex\skills\skills-index.json
```

Before editing:

1. Read [`AGENTS.md`](AGENTS.md).
2. Inspect the live repository state and applicable nested instructions.
3. For skill work, read the [`research synthesis`](docs/research/skill-adoption-research-synthesis.md) and its linked package, security, evaluation, adapter, and backlog owners.
4. Identify whether the task changes repository runtime state, shared workspace catalogue state, or both.
5. Identify the candidate skill, its authoritative source/evidence, and immutable revision or trusted-local identity.
6. Locate or create the authoritative specification, decision, plan, work item, and validation documentation required for the change.

## Common Workflow

1. **Select** a candidate or catalogue item from an approved source surface.
2. **Assess** its purpose, dependencies, compatibility, security implications, overlap, and maintenance cost.
3. **Decide** whether to adopt, adapt, defer, reject, withdraw, or suspend it, recording the decision in the appropriate repository record.
4. **Implement** the smallest coherent repository-owned or explicitly authorized shared-catalogue change.
5. **Validate** the affected skill/package/catalogue with targeted and repository-wide checks appropriate to the changed boundary.
6. **Document** provenance, usage, limitations, rollback, and authoritative references without duplicating implementation guidance in this README.

## Work Management

Work for this repository is tracked by issue-backed records and projected into the shared GitHub user Project `NielPieterse0/1`. The currently commissioned KIS Work Management capabilities and workflows are the operational control plane for reading, reconciling, and validating that lifecycle; repository operation must not depend on a particular KIS implementation checkout path.

The machine-readable binding is [`settings/projects/chatgpt-skill.json`](settings/projects/chatgpt-skill.json). It records the required KIS capability families and operations, the Project identity, and an exact-source safety rule: only records sourced from `NielPieterse0/chatgpt-skill` are mutation-eligible.

For each work item, read the source issue and current Project status before claiming it, use a clean issue worktree, keep lifecycle state current, complete required verification and review/merge, then close the source issue and reconcile its Project projection to `Done`. The issue remains the stable source identity throughout; stale Project state must be reconciled rather than silently treated as authoritative.

## Repository Structure

```text
AGENTS.md          Repository-wide execution contract
README.md          Project entry point and navigation
package.json       Fixed validation and catalog commands
.github/           CI, ownership, contribution, issue, and dependency automation
config/            Machine-enforced security policy and runtime kill switch
settings/          Repository-owned project and Work Management contract
schemas/           Adoption manifest contract
scripts/           Repository-owned validation and catalog tooling
skills/            Only repository runtime-discoverable adopted skills
references/        Untrusted source evidence and provenance material
docs/              Specifications, architecture, decisions, plans, standards, and operations
tests/             Automated security-gate tests
.work/             Temporary, generated, quarantine, and incident artifacts
```

`references/` and `.work/` are never repository runtime discovery roots. `skills/` admits only direct child skill directories that pass the security gate. The external workspace catalogue at `C:\Projects\.agents\skills` is managed separately through explicit tracked catalogue operations.

## Validation

Run the fixed repository checks:

```powershell
npm test
npm run verify-bootstrap  # controlled pre-Git bootstrap only
npm run verify            # required after Git origin is configured
npm run catalog           # returns an empty repo runtime catalog while the kill switch is disabled
```

Direct validator commands are also available:

```powershell
python scripts/skill_security.py validate --repo .
python scripts/skill_security.py catalog --repo .
python scripts/skill_security.py hash skills/<skill-name>
```

For final review, also run `git diff --check` and inspect `git status --short`. Catalogue-changing work must additionally refresh and re-read KIS Skills against `C:\Projects\.agents\skills`. Do not claim a check passed unless its command completed successfully. The one permitted pre-Git exception is `verify-bootstrap`; it does not satisfy completion validation.

## Authoritative Documentation

- [`docs/research/skill-adoption-research-synthesis.md`](docs/research/skill-adoption-research-synthesis.md): accepted research conclusions, requirements matrix, unresolved product questions, and output status.
- [`docs/standards/skill-package-standard.md`](docs/standards/skill-package-standard.md): canonical repository skill contents, progressive disclosure, resources, target overlays, and packaging exclusions.
- [`docs/testing/skill-evaluation-standard.md`](docs/testing/skill-evaluation-standard.md): trigger, output, efficiency, abuse, compatibility, and human-review gates.
- [`docs/plans/skill-adoption-implementation-backlog.md`](docs/plans/skill-adoption-implementation-backlog.md): current and historical implementation work, dependencies, and stop criteria.
- [`docs/operations/github-repository-hygiene.md`](docs/operations/github-repository-hygiene.md): accepted GitHub repository settings, main-branch controls, automation, and closeout checklist.
- [`SECURITY.md`](SECURITY.md): private vulnerability reporting and immediate containment.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): contribution and pull-request workflow.
- [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md): P0 trust zones, capability tiers, provenance, admission, discovery, disablement, validation, and incident-containment rules.
- [`schemas/skill-adoption-manifest.schema.json`](schemas/skill-adoption-manifest.schema.json): machine-readable repository adoption record contract.
- [`references/skills-knowledge-source-register.md`](references/skills-knowledge-source-register.md): curated hierarchy of Agent Skills specifications, product documentation, implementations, catalogs, security standards, evaluation research, and adoption-source requirements.
- [`docs/research/chatgpt-skill-adoption-deep-research-brief.md`](docs/research/chatgpt-skill-adoption-deep-research-brief.md): focused research scope for the portable skill package, ChatGPT coding-agent architecture, security controls, scripts, references, evals, and implementation decisions.
- [`AGENTS.md`](AGENTS.md): repository-wide behavioral rules, required workflow, constraints, validation expectations, and completion criteria.
- [`docs/architecture/skill-runtime-adapters.md`](docs/architecture/skill-runtime-adapters.md): authoritative ChatGPT-first adapter strategy and the boundary between portable adoption logic and target-specific integration.
- [`docs/architecture/import-isolate-handoff.md`](docs/architecture/import-isolate-handoff.md): responsibility boundary for externally acquired source material and finalized `import-isolate` handoffs.
- [`docs/architecture/plugin-portfolio-methodology.md`](docs/architecture/plugin-portfolio-methodology.md): plugin-versus-skill/app/adapter boundaries, portfolio lifecycle, intake/update/rollback flow, pilot rules, and reporting requirements.
- `docs/`: other product, architecture, decision, planning, coding, testing, and operational documents, when added.
- Nested `AGENTS.md` files: path-specific working rules, when added.
- Adopted skill directories: skill-specific implementation and usage documentation.

This README should link to authoritative documents as they are introduced rather than duplicate them.

## Contributing

Keep changes scoped, preserve unrelated work, follow the applicable `AGENTS.md`, update the relevant authoritative documentation, and include evidence for every validation claim.