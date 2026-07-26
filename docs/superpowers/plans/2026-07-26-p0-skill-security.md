# P0 Skill Security Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a fail-closed security and provenance gate that prevents unreviewed source skills from becoming runtime-discoverable.

**Architecture:** A dependency-free Python validator reads repository-owned JSON policy and runtime-control files, validates direct-child adopted skills against strict metadata and manifest contracts, verifies content integrity and Git origin, and emits an all-or-nothing canonical catalog. The `references/` corpus remains outside every executable and discovery path. Target-specific discovery, activation, packaging, and metadata are delegated to runtime adapters under the boundary defined in [`docs/architecture/skill-runtime-adapters.md`](../../architecture/skill-runtime-adapters.md); ChatGPT is the initial target.

**Tech Stack:** Python 3.10+ standard library, JSON Schema documentation, `unittest`, Markdown.

## Global Constraints

- Work only inside `C:\Projects\ChatGPT-skill-adoption`.
- Discover only `skills/*/SKILL.md`; never scan `references/`.
- Reject symlinks, duplicate names, nested skills, malformed metadata, unapproved capabilities, and integrity mismatches.
- Reject `allowed-tools`; runtime permissions are host-enforced.
- Runtime starts disabled.
- Tier 3 and Tier 4 skills are prohibited at P0.
- No external dependencies or runtime installation.

---

### Task 1: Define failing security behavior tests

**Files:**
- Create: `tests/test_skill_security.py`
- Create: `scripts/__init__.py`

**Interfaces:**
- Consumes: none.
- Produces: expected public functions `load_json`, `compute_skill_hash`, `validate_repository`, and `build_catalog` in `scripts.skill_security`.

- [ ] Write tests for valid admission, exact discovery, reference exclusion, nested-skill rejection, symlink rejection, metadata validation, missing manifest, hash mismatch, prohibited capabilities, explicit Tier 2 activation, kill switch, and Git-origin validation.
- [ ] Run `python -m unittest discover -s tests -v` and confirm failure because `scripts.skill_security` does not exist.

### Task 2: Add policy, runtime control, and manifest schema

**Files:**
- Create: `config/skill-security-policy.json`
- Create: `config/runtime-control.json`
- Create: `schemas/skill-adoption-manifest.schema.json`

**Interfaces:**
- Produces: stable JSON keys consumed by `scripts.skill_security`.

- [ ] Define direct-child discovery and permanent exclusions.
- [ ] Define allowed tiers `[0, 1, 2]` and prohibited capabilities.
- [ ] Set `skills_enabled` to `false`.
- [ ] Define the complete adoption manifest contract and disallow unknown fields.
- [ ] Validate both JSON files structurally.

### Task 3: Implement the validator and catalog gate

**Files:**
- Create: `scripts/skill_security.py`

**Interfaces:**
- `compute_skill_hash(skill_dir: Path) -> str`
- `validate_repository(repo_root: Path, *, require_git: bool = True) -> ValidationReport`
- `build_catalog(repo_root: Path, *, require_git: bool = True) -> dict[str, object]`
- CLI commands: `validate`, `catalog`, `hash`.

- [ ] Implement strict frontmatter parsing and Agent Skills field constraints.
- [ ] Implement manifest shape, provenance, license, approval, rollback, activation, filesystem, dependency, and capability validation.
- [ ] Implement deterministic tree hashing excluding `adoption-manifest.json`.
- [ ] Implement exact non-recursive discovery and symlink rejection.
- [ ] Implement Git metadata and expected-origin validation.
- [ ] Implement the emergency kill switch and all-or-nothing catalog output.
- [ ] Run the test suite and make every test pass.

### Task 4: Publish authoritative security documentation

**Files:**
- Create: `docs/security/skill-adoption-security-standard.md`
- Create: `docs/security/adoption-manifest-example.json`
- Modify: `AGENTS.md`
- Modify: `README.md`

**Interfaces:**
- Produces: authoritative human and machine navigation for future adoption work.

- [ ] Document trust zones, capability tiers, admission criteria, prohibited behaviors, Git provenance, emergency disablement, and validation commands.
- [ ] Add a valid example manifest.
- [ ] Reference the standard from `AGENTS.md` without duplicating implementation detail.
- [ ] Add security setup and validation entry points to `README.md`.

### Task 5: Verify and establish Git baseline

**Files:**
- Modify through Git tooling only: repository metadata and private `origin`.

**Interfaces:**
- Produces: local Git metadata, initial commit, private remote, configured `origin`, and matching `config/skill-security-policy.json` expected origin.

- [ ] Run the complete unit test suite.
- [ ] Run `python scripts/skill_security.py validate --repo . --skip-git` before Git initialization.
- [ ] Initialize and publish the repository privately through the approved repository workflow.
- [ ] Record the verified remote in policy.
- [ ] Run Git-aware validation and catalog generation.
- [ ] Run `git diff --check` and inspect final status.
