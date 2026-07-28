# Create Skill Reference Artifacts Design

## Authority and Status

This design records the approved structure and acceptance criteria for two source-derived reference artifacts intended for the future `create-skill` skill.

It does not create or admit a runtime skill, alter repository security policy, redefine the canonical skill package standard, or authorize moving draft material into `skills/`. Repository authority remains with `AGENTS.md` and the authoritative documents it references.

- **Design date:** 2026-07-28
- **Status:** Approved for implementation planning
- **Selected approach:** Two focused references
- **Initial staging location:** `.work/create-skill-draft/references/`
- **Future canonical location:** `skills/create-skill/references/`, only after the skill and its adoption manifest pass the repository admission process

## Required Outcome

Create two concise, agent-readable and machine-friendly Markdown references:

```text
.work/create-skill-draft/
└── references/
    ├── agent-skill-package-contract.md
    └── agent-skill-runtime-lifecycle.md
```

The files must support progressive discovery. Each file has one responsibility and an explicit load condition. Neither file may require loading the other.

## Source Basis

Primary source evidence:

- `references/agent-skills-specification.md`
- `references/agents-skills-support.md`

Repository constraints and adaptations:

- `AGENTS.md`
- `docs/research/skill-adoption-research-synthesis.md`
- `docs/standards/skill-package-standard.md`
- `docs/security/skill-adoption-security-standard.md`

The primary source files remain evidence, not repository policy. The reference artifacts must preserve source-supported requirements and label repository adaptations separately.

## Component Design

### 1. `agent-skill-package-contract.md`

**Responsibility:** Summarize the portable Agent Skills package format and the decisions required when creating or validating a skill package.

**Load when:**

- creating a new skill package;
- validating or restructuring `SKILL.md`;
- deciding whether content belongs in `SKILL.md`, `references/`, `scripts/`, or `assets/`;
- checking naming, frontmatter, path, progressive-disclosure, or validation requirements.

**Required content:**

1. portable directory model;
2. required and optional `SKILL.md` frontmatter fields;
3. exact field constraints for `name` and `description`;
4. body-design guidance and recommended size limits;
5. responsibilities of `references/`, `scripts/`, and `assets/`;
6. progressive-disclosure tiers and context implications;
7. relative-path and one-level-reference rules;
8. structural validation guidance;
9. edge cases and non-portable or experimental elements;
10. repository adaptations, including the prohibition on `allowed-tools`.

**Exclusions:**

- runtime discovery paths;
- client catalog construction;
- activation-tool design;
- context compaction and activation deduplication;
- target-specific packaging or UI metadata.

### 2. `agent-skill-runtime-lifecycle.md`

**Responsibility:** Summarize how an agent or development tool discovers, discloses, activates, and retains skills over a session.

**Load when:**

- implementing or reviewing skills support in an agent, client, or runtime adapter;
- defining discovery scopes or collision precedence;
- designing a skill catalog or activation tool;
- handling trust, malformed metadata, resource permissions, context retention, or repeated activation;
- assessing cloud-hosted, sandboxed, or subagent-based skill execution.

**Required content:**

1. three-tier progressive-disclosure lifecycle;
2. project, user, organization, and built-in discovery scopes;
3. supported directory conventions and their portability status;
4. bounded scanning rules and collision precedence;
5. project trust gating;
6. `SKILL.md` parsing and malformed-YAML handling;
7. minimum skill-record fields;
8. catalog disclosure and filtering;
9. model-driven and user-explicit activation patterns;
10. file-read versus dedicated-tool activation trade-offs;
11. structured wrapping and resource enumeration;
12. permission allowlisting considerations;
13. context-compaction protection and activation deduplication;
14. optional subagent delegation;
15. repository adaptations and unresolved target-specific behavior.

**Exclusions:**

- full frontmatter field reference;
- detailed package-authoring guidance already owned by the package-contract reference;
- target-specific implementation claims not supported by verified product evidence;
- authorization claims based only on portable metadata.

## Shared Reference Format

Each reference must start with compact YAML metadata:

```yaml
---
reference_id: <stable-kebab-case-id>
source_class: external-specification
source_authority: source-evidence
status: draft
verified_date: 2026-07-28
load_when:
  - <specific condition>
source_files:
  - <repository-relative source path>
repository_adaptations:
  - <authoritative repository document>
---
```

The Markdown body must use this section order unless a section is genuinely inapplicable:

1. `Purpose`
2. `Load Conditions`
3. `Source Status`
4. `Core Model`
5. `Requirements`
6. `Decision Tables`
7. `Agent Checklist`
8. `Edge Cases and Failure Handling`
9. `Non-Portable or Experimental Elements`
10. `Repository Adaptations`
11. `Source Traceability`

The artifacts must favor tables, closed lists, explicit conditions, and checklists over long narrative prose.

## Authority Separation

Every substantive statement must fit one of these classes:

| Class | Meaning | Required treatment |
|---|---|---|
| Source requirement | Explicitly required by the attached source | State directly and trace to the source file |
| Source guidance | Recommended or optional in the attached source | Preserve modal language such as “should,” “consider,” or “optional” |
| Repository adaptation | Project-owned rule that narrows or changes source guidance | Label under `Repository Adaptations` and name its authoritative owner |
| Runtime-specific choice | Implementation option selected by a client or adapter | Mark as non-portable and avoid presenting it as specification law |
| Unresolved fact | Not established by the source or current repository evidence | State as unresolved; do not infer or silently fill the gap |

Conflicts must be preserved and explained. The artifacts must not silently reconcile strict specification validation with a runtime implementation’s lenient parsing strategy.

## Progressive-Discovery Integration

The future `create-skill/SKILL.md` should load the references with explicit conditions equivalent to:

```markdown
Read `references/agent-skill-package-contract.md` when creating, validating,
or restructuring a skill package.

Read `references/agent-skill-runtime-lifecycle.md` only when the task includes
implementing or evaluating skill discovery, disclosure, activation, permissions,
or session-context behavior in an agent or runtime adapter.
```

Ordinary skill creation must not load the runtime-lifecycle reference by default.

## Data Flow

1. Read each primary source in full.
2. Extract requirements, recommendations, options, edge cases, and examples.
3. Assign each extracted point to exactly one reference artifact.
4. Remove duplicated general knowledge and examples that do not improve decisions.
5. Add repository adaptations only from named authoritative documents.
6. Verify that every claim is source-supported or explicitly labeled as a repository adaptation.
7. Stage the draft files under `.work/create-skill-draft/references/`.
8. Promote them into a canonical skill only through the repository admission and implementation workflow.

## Error and Conflict Handling

- When the sources do not support a requested claim, state that the point is unsupported.
- When strict specification rules conflict with lenient runtime behavior, describe both and identify their different purposes.
- Treat directory conventions such as `.agents/skills/` as implementation conventions, not requirements of the portable package specification.
- Treat `allowed-tools` as experimental source metadata and prohibited by current repository policy.
- Treat runtime behavior, product permissions, context retention, and activation observability as target-dependent unless empirically verified.
- Do not copy source HTML components, navigation boilerplate, duplicate examples, or documentation-site presentation markup.

## Acceptance Criteria

The implementation is acceptable only when:

- exactly two focused reference files are produced;
- each file has one clear responsibility and explicit load conditions;
- every source-supported requirement is represented in the correct artifact or deliberately omitted with rationale;
- source requirements, source guidance, repository adaptations, and unresolved facts are visibly distinct;
- no reference-to-reference dependency exists;
- no runtime-discoverable `SKILL.md` or adoption manifest is created;
- no source document is modified;
- no ChatGPT- or Codex-specific behavior is presented as portable specification;
- the references are concise enough for conditional loading and contain no unnecessary copied prose;
- Markdown structure, relative paths, metadata consistency, and internal links are valid;
- a final review finds no placeholders, unsupported claims, duplicated authority, or unrecorded assumptions.

## Validation Design

Implementation validation must include:

1. confirm both expected paths exist under `.work/create-skill-draft/references/`;
2. inspect YAML metadata for stable identifiers, source paths, load conditions, and verification date;
3. compare the package-contract artifact against the package specification source;
4. compare the runtime-lifecycle artifact against the skills-support source;
5. search for prohibited placeholders such as `TBD` and `TODO`;
6. verify that `allowed-tools` is not presented as repository authorization;
7. verify that no path under `skills/` changed;
8. verify Markdown structure and source traceability;
9. run `git diff --check` if tracked repository files are changed during implementation;
10. report checks that cannot run rather than claiming success.

## Non-Goals

This work does not:

- create the `create-skill` skill;
- define its final `SKILL.md` workflow or trigger description;
- create an adoption manifest;
- add scripts, assets, evals, runtime adapters, or OpenAI metadata;
- enable runtime discovery;
- move the draft references into the canonical `skills/` tree;
- resolve broader product questions about ChatGPT or Codex skill behavior.

## Implementation Boundary

The next phase may create only the two staged reference files and the minimum supporting directories under `.work/create-skill-draft/`. Any expansion into canonical skill implementation, evaluation, admission, packaging, GitHub closeout, or runtime enablement requires a separate approved plan and the applicable repository gates.
