# P0 Skill Security Design

## Status

Approved for immediate implementation by the repository owner on 2026-07-26.

## Purpose

Implement the minimum enforceable controls required before any skill can move from `references/` into the runtime-discoverable `skills/` directory.

## Architecture Dependency

The portable-core and runtime-adapter boundary is defined by [`docs/architecture/skill-runtime-adapters.md`](../../architecture/skill-runtime-adapters.md). This security design owns admission controls only: it produces a canonical admitted catalog and must not embed ChatGPT-specific or future Codex-specific discovery, activation, packaging, or metadata behavior.

## Security Boundary

The repository has two distinct trust zones:

- `references/`: untrusted, read-only source evidence. Files below it are never runtime-discoverable or executable.
- `skills/`: repository-owned adopted skills. Each direct child is admitted only after strict validation.

Discovery is exact and non-recursive: `skills/*/SKILL.md`. The implementation rejects nested skills, symlinks, reparse-like paths reported as links, duplicate names, malformed metadata, absent adoption manifests, and policy violations.

## Components

1. `docs/security/skill-adoption-security-standard.md` owns the P0 security rules and capability tiers.
2. `schemas/skill-adoption-manifest.schema.json` defines the portable adoption record.
3. `config/skill-security-policy.json` owns discovery roots, exclusions, allowed tiers, and prohibited capabilities.
4. `config/runtime-control.json` is the emergency runtime kill switch and starts disabled.
5. `scripts/skill_security.py` validates repository state, manifests, skill metadata, content hashes, capabilities, Git metadata, and catalog eligibility.
6. `tests/test_skill_security.py` verifies fail-closed behavior with isolated temporary repositories.

## Admission Contract

A skill is catalog-eligible only when all of the following hold:

- the emergency switch is enabled;
- Git metadata exists and `origin` matches the configured expected remote;
- the skill is a direct child of `skills/`;
- its `SKILL.md` follows the Agent Skills naming and description constraints;
- `adoption-manifest.json` exists and passes repository validation;
- source revision, content hash, license review, capability tier, approval, and rollback state are recorded;
- no prohibited capability is requested;
- the recorded tree hash matches the current skill content;
- no symlink occurs in the skill tree.

`allowed-tools` is rejected because the Agent Skills field is experimental and cannot serve as the repository security boundary.

## Capability Tiers

- Tier 0: instruction-only, no scripts or runtime tools; model activation permitted.
- Tier 1: repository read-only; model activation permitted.
- Tier 2: bounded repository writes; explicit activation and human approval required.
- Tier 3: network, runtime dependency installation, or external data; prohibited at P0.
- Tier 4: credentials, lifecycle hooks, Git publication, deployment, deletion, or external mutation; prohibited at P0.

## Runtime Flow

1. Read `config/runtime-control.json`.
2. Return an empty catalog when disabled.
3. Validate repository Git identity and policy.
4. Inspect only direct children of `skills/`.
5. Validate every candidate and fail the complete catalog on any error.
6. Emit platform-neutral structured JSON containing only admitted canonical skills.
7. Allow only the selected runtime adapter to map the admitted catalog into ChatGPT-specific or future target behavior.

## Error Handling

All security-relevant ambiguity fails closed. Validation returns stable error codes, human-readable messages, and a non-zero exit status. Catalog generation never returns a partial catalog.

## Testing

Tests use Python standard-library `unittest` and temporary directories. They cover valid admission, reference exclusion, nested discovery rejection, symlink rejection, malformed skill metadata, missing manifests, hash mismatch, prohibited capabilities, tier activation constraints, kill-switch behavior, and Git-origin enforcement.

## Constraints

- No runtime dependencies.
- No target-specific discovery, activation, packaging, or metadata assumptions in the portable admission validator or canonical catalog.
- No writes outside `C:\Projects\ChatGPT-skill-adoption`.
- No execution of imported reference scripts.
- No remote MCP, hooks, credentials, external mutations, or runtime package installation at P0.
- The live repository remains the sole source of truth.
