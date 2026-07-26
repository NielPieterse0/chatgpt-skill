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

The repository is in its bootstrap stage. The initial root governance and entry-point documents are present; adopted skill artifacts and supporting authority documents should be added through the repository workflow defined in [`AGENTS.md`](AGENTS.md).

## Quick Start

```powershell
Set-Location C:\Projects\ChatGPT-skill-adoption
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
3. Identify the candidate skill and its source files.
4. Locate or create the authoritative specification, decision, plan, or validation documentation required for the change.

## Common Workflow

1. **Select** a candidate from the external skills index.
2. **Assess** its purpose, dependencies, compatibility, security implications, and maintenance cost.
3. **Decide** whether to adopt, adapt, defer, or reject it, recording the decision in the appropriate repository document.
4. **Implement** the smallest coherent repository-owned version.
5. **Validate** the adopted artifacts with targeted and repository-wide checks.
6. **Document** provenance, usage, limitations, and authoritative references without duplicating implementation guidance in this README.

## Repository Structure

The repository uses the following high-level structure as content is added:

```text
AGENTS.md          Repository-wide execution contract
README.md          Project entry point and navigation
.work/             Temporary and generated working artifacts
skills/            Adopted repository-owned skill artifacts
docs/              Specifications, architecture, decisions, plans, and standards
references/        Curated external knowledge, source snapshots, and provenance material
tests/              Automated validation for adopted skills and supporting tooling
```

Directories beyond the root documents are created only when required by an adopted change.

## Validation

Use the commands documented by the relevant authoritative repository files. For documentation-only changes, verify Markdown consistency, referenced paths, authority boundaries, and run the following when Git metadata is available:

```powershell
git diff --check
git status --short
```

Do not treat missing validation infrastructure as a successful check. Record unavailable checks and add appropriate validation as the repository evolves.

## Authoritative Documentation

- [`references/skills-knowledge-source-register.md`](references/skills-knowledge-source-register.md): curated hierarchy of Agent Skills specifications, product documentation, implementations, catalogs, security standards, evaluation research, and adoption-source requirements.
- [`docs/research/chatgpt-skill-adoption-deep-research-brief.md`](docs/research/chatgpt-skill-adoption-deep-research-brief.md): focused research scope for the portable skill package, ChatGPT coding-agent architecture, security controls, scripts, references, evals, and implementation decisions.

- [`AGENTS.md`](AGENTS.md): repository-wide behavioral rules, required workflow, constraints, validation expectations, and completion criteria.
- [`docs/architecture/skill-runtime-adapters.md`](docs/architecture/skill-runtime-adapters.md): authoritative ChatGPT-first adapter strategy and the boundary between portable adoption logic and target-specific integration.
- `docs/`: other product, architecture, decision, planning, coding, testing, and operational documents, when added.
- Nested `AGENTS.md` files: path-specific working rules, when added.
- Adopted skill directories: skill-specific implementation and usage documentation.

This README should link to authoritative documents as they are introduced rather than duplicate them.

## Contributing

Keep changes scoped, preserve unrelated work, follow the applicable `AGENTS.md`, update the relevant authoritative documentation, and include evidence for every validation claim.
