# Skill Runtime Adapter Architecture

## Authority

This document owns the repository-wide boundary between portable skill-adoption logic and target-specific skill behavior. It defines the adapter methodology used to support ChatGPT now and other skill runtimes later.

Repository working rules remain in [`AGENTS.md`](../../AGENTS.md). Skill security and admission controls remain in the applicable documents under [`docs/security/`](../security/).

## Decision

ChatGPT is the initial delivery target.

The adoption methodology, canonical skill records, validation rules, provenance, security decisions, and evaluation model must remain independent of any one host. ChatGPT-specific discovery, activation, packaging, metadata, tools, and capability mappings must be isolated behind a ChatGPT adapter.

A future Codex adapter must be addable or selectable without redesigning the portable adoption core. Target capability differences may require adapter-specific behavior, but must not create separate competing sources of truth for the adopted skill.

## Architectural Boundaries

### Portable adoption core

The portable core owns:

- candidate assessment and adoption decisions;
- canonical skill identity, content, provenance, and version records;
- Agent Skills specification validation;
- repository security policy and admission status;
- platform-neutral capability declarations;
- canonical catalog generation;
- shared evaluation cases and acceptance criteria.

The portable core must not assume a target-specific installation path, activation syntax, tool name, prompt injection mechanism, catalog envelope, permission model, or product-only metadata field.

### Runtime adapters

Each runtime adapter owns only the mapping from the portable adopted skill to one target environment, including:

- target discovery and installation locations;
- target catalog and activation representation;
- target-specific metadata or configuration;
- tool and capability mapping;
- unsupported-feature handling;
- packaging or publication needed by that target;
- target-specific validation and compatibility evidence.

Adapters must consume the canonical adopted skill and admission result. They must not redefine provenance, approval, security tier, or canonical skill identity.

### Adopted skill content

Keep reusable instructions and resources in the canonical adopted skill wherever practical. Place host-specific instructions or configuration in the responsible adapter or an explicitly named target overlay. Do not fork an entire skill merely to change host integration details.

When target behavior cannot be represented without changing the canonical skill, record the reason and the cross-target consequence in an authoritative decision document before changing the core contract.

## Processing Model

Use this sequence:

1. Inspect and assess the source candidate.
2. Create or update the canonical repository-owned adopted skill and provenance record.
3. Run portable metadata, security, integrity, and evaluation checks.
4. Pass only admitted canonical skills to the selected runtime adapter.
5. Apply target-specific mappings and reject unsupported or ambiguous capabilities.
6. Run adapter contract tests and target-specific validation.
7. Publish or expose only the adapter output approved for that target.

Do not transform an external source skill directly into a target runtime artifact without first establishing the canonical repository-owned adoption record.

## Initial ChatGPT Target

The first adapter targets ChatGPT-specific skill workflows. Initial implementation and validation may optimize for ChatGPT capabilities, but target assumptions must remain inside the ChatGPT adapter boundary.

ChatGPT-specific tests must demonstrate both:

- correct target behavior; and
- preservation of the canonical skill's approved intent, security constraints, provenance, and acceptance criteria.

## Future Codex Target

A Codex adapter should implement the same adapter contract against the same canonical adopted skills. Introducing it should require target mappings and target tests, not a duplicate adoption pipeline or a second canonical skill catalog.

Where ChatGPT and Codex capabilities differ, each adapter must declare the supported mapping and fail closed for unsupported required behavior. Silent capability loss is not acceptable.

## Implementation Rules

- Prefer explicit adapter modules over host-condition branches spread through core code.
- Keep target dispatch at a narrow boundary.
- Define adapter inputs and outputs as stable, machine-readable contracts before adding multiple adapters.
- Require every adapter to declare target identity, supported capabilities, unsupported required capabilities, and validation results.
- Reuse canonical fixtures across adapter tests.
- Add cross-adapter parity tests for behavior that is intended to remain portable.
- Do not add a generalized framework beyond the minimum contract needed by the current ChatGPT adapter and a credible future Codex adapter.

When implementation directories are introduced, use an explicit target structure such as `adapters/chatgpt/` and later `adapters/codex/`. Do not create empty scaffolding before it is required by an implemented change.

## Validation

A change affecting the core or an adapter is complete only when applicable evidence shows:

- portable validation still passes without target-specific assumptions;
- the selected adapter accepts the canonical contract;
- required capabilities are mapped or rejected explicitly;
- target-specific tests pass;
- shared acceptance criteria remain valid;
- no duplicate canonical skill, provenance, security, or approval record was introduced.

## Source Basis

The Agent Skills format provides a portable skill package centered on `SKILL.md` and progressively loaded resources; it does not mandate host discovery locations or activation mechanisms. The repository therefore treats target integration as an adapter concern.

- [`references/agent-skills-specification.md`](../../references/agent-skills-specification.md)
- [`references/agents-skills-support.md`](../../references/agents-skills-support.md)
