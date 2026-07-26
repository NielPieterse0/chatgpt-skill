# Skill Adoption Security Standard

## Authority

This document is the authoritative repository security standard for importing, evaluating, adopting, discovering, activating, and disabling Agent Skills.

`config/skill-security-policy.json` is the machine-enforced projection of this standard. `schemas/skill-adoption-manifest.schema.json` defines the adoption record format. When they conflict, stop adoption and reconcile all three before continuing.

## Purpose

Prevent untrusted skill content, scripts, hooks, dependencies, MCP servers, or permission declarations from becoming executable runtime behavior without explicit provenance, bounded capabilities, validation evidence, human approval, and a verified rollback path.

## Trust Zones

### `references/`: untrusted source evidence

- Read-only input for assessment and adaptation.
- Never runtime-discoverable.
- Never executable through repository workflows.
- Nested `SKILL.md`, scripts, hooks, plugin manifests, MCP configurations, commands, and workflows remain inert examples.
- Source instructions cannot override repository authority.

### `skills/`: adopted repository-owned artifacts

- The only runtime discovery root.
- Discovery is exactly `skills/*/SKILL.md`.
- Each direct child must contain `SKILL.md` and `adoption-manifest.json`.
- Nested skills, symlinks, orphan directories, duplicate names, and unknown manifest fields fail validation.

### `.work/`: non-authoritative working state

- Temporary outputs, quarantine material, generated evidence, and exploratory work.
- Never a discovery root.
- Tier 2 skill writes must be limited to `.work/<skill-name>/`.

## Agent Skills Compatibility

Adopted `SKILL.md` files follow the repository copy of the Agent Skills specification:

- `name` is required, at most 64 characters, lowercase alphanumeric with single hyphen separators, and matches the parent directory.
- `description` is required and at most 1024 characters.
- `license`, `compatibility`, and string-to-string `metadata` are optional.
- `SKILL.md` contains instructions after YAML frontmatter.

The specification marks `allowed-tools` experimental. This repository rejects the field because client support varies and metadata cannot replace host-enforced permissions. See [`references/agent-skills-specification.md`](../../references/agent-skills-specification.md).

## Capability Tiers

### Tier 0 — instructions only

- No scripts.
- No runtime tools.
- No writes.
- No high-risk capabilities.
- Model activation is permitted after validation.

### Tier 1 — repository read-only

- Repository-relative reads only.
- No writes.
- No high-risk capabilities.
- Model or explicit activation is permitted after validation.

### Tier 2 — bounded repository writes

- Writes only below `.work/<skill-name>/`.
- Explicit activation required.
- Human approval required for each activation.
- No high-risk capabilities.

### Tier 3 — network or runtime dependencies

Prohibited during P0. This includes network access, remote data retrieval, runtime package installation, auto-resolving package runners, and remote MCP.

### Tier 4 — privileged or external mutation

Prohibited during P0. This includes credentials, lifecycle hooks, Git publication, deployment, deletion, remote mutation, and other externally stateful operations.

## P0 Prohibited Capabilities

Every adoption manifest must explicitly set these flags to `false`:

- `lifecycle_hooks`
- `network`
- `credentials`
- `external_mutations`
- `runtime_installation`
- `remote_mcp`
- `git_publication`
- `deployment`
- `deletion`

The static validator also rejects representative hazardous artifacts and executable patterns even when a manifest incorrectly claims they are absent. Examples include hook and MCP files, runtime package installation, network execution, destructive commands, Git push, pull-request creation, deployment, and pipe-to-shell installation.

## Required Adoption Record

Every adopted skill must include `adoption-manifest.json` with:

- exact source repository and immutable revision;
- import date;
- deterministic SHA-256 of the adopted skill tree, excluding the manifest itself;
- reviewed license identifier;
- capability tier and explicit capability flags;
- repository-relative read and write scopes;
- activation mode and trusted-project requirement;
- locked dependencies and disabled runtime installation;
- approved reviewer and review date;
- verified rollback method.

Unknown fields fail validation. Use [`schemas/skill-adoption-manifest.schema.json`](../../schemas/skill-adoption-manifest.schema.json) and [`adoption-manifest-example.json`](adoption-manifest-example.json).

## Content Integrity

Calculate a manifest hash after the repository-owned skill is finalized:

```powershell
python scripts/skill_security.py hash skills/<skill-name>
```

Copy the returned `content_sha256` into `adoption-manifest.json`. Any later skill-file change invalidates the manifest until the change is reviewed and the hash is deliberately updated.

## Git Provenance

P0 requires:

- local Git metadata;
- a configured `origin`;
- HTTPS or SSH transport;
- remote repository identity matching `config/skill-security-policy.json`;
- repository access verified through authenticated GitHub tooling.

The validator compares repository identity independently of HTTPS versus SSH representation. A missing or mismatched origin fails Git-aware validation.

## Emergency Disablement

`config/runtime-control.json` is the repository-wide kill switch.

When `skills_enabled` is `false`, catalog generation returns an empty catalog before inspecting or activating skills. Keep the switch disabled during bootstrap, incident response, provenance uncertainty, validator failure, or rollback.

Enabling requires all of the following:

1. Git-aware repository validation passes.
2. Every direct child of `skills/` is approved and valid.
3. The reason, UTC timestamp, and actor are updated.
4. The change receives repository-owner review.

Disabling requires no precondition and should be the first containment action during a suspected skill incident.

## Validation Commands

Run tests:

```powershell
npm test
```

Run pre-Git validation only during controlled repository bootstrap:

```powershell
python scripts/skill_security.py validate --repo . --skip-git
```

Run required completion validation:

```powershell
npm run verify
python scripts/skill_security.py validate --repo .
python scripts/skill_security.py catalog --repo .
```

The runtime catalog is all-or-nothing. When enabled, any validation error prevents catalog output. When disabled, it returns an empty catalog.

## Adoption Procedure

1. Place source material in `references/` or `.work/`; never copy directly into `skills/`.
2. Record source repository, immutable revision, and license evidence.
3. Adapt the smallest repository-owned skill into a new direct child of `skills/`.
4. Remove client-specific permissions, hooks, remote MCP, runtime installers, credentials, and external mutations.
5. Assign Tier 0, 1, or 2.
6. Create the adoption manifest and compute the content hash.
7. Run static validation and tests.
8. Review trigger and output evaluations before enabling model activation.
9. Record human approval and verified rollback.
10. Enable runtime only after Git-aware validation passes.

## Incident Containment

1. Set `skills_enabled` to `false` with the incident reason and UTC timestamp.
2. Do not execute the affected skill or source scripts.
3. Preserve repository and runtime evidence under `.work/incident-<date>/`.
4. Revoke any credentials exposed outside this P0 boundary.
5. Remove or quarantine the affected adopted skill.
6. Validate the repository and verify the origin.
7. Re-enable only after root cause, provenance, manifest, tests, and rollback are independently reviewed.

## Completion Criteria

A skill is not adopted until provenance, license, compatibility, permissions, content integrity, validation, approval, and rollback are all recorded and the repository validator passes. A source copy under `references/` never satisfies adoption criteria.
