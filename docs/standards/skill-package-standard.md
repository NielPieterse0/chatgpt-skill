# Skill Package Standard

## Authority

This document owns the repository contract for canonical adopted skill contents, supporting resources, target overlays, generated runtime packages, and packaging exclusions.

Security admission and capability tiers are governed by [`docs/security/skill-adoption-security-standard.md`](../security/skill-adoption-security-standard.md). Runtime-specific mappings are governed by [`docs/architecture/skill-runtime-adapters.md`](../architecture/skill-runtime-adapters.md). Evaluation evidence is governed by [`docs/testing/skill-evaluation-standard.md`](../testing/skill-evaluation-standard.md).

## Package Layers

### 1. Source evidence

External and comparative material lives under `references/` or temporary `.work/` paths. It is untrusted, non-authoritative, non-discoverable, and never executed by repository workflows.

### 2. Canonical adopted skill

The canonical repository-owned skill lives at:

```text
skills/<skill-name>/
├── SKILL.md
├── adoption-manifest.json
├── LICENSE.txt                 # when required by the adopted license
├── references/                # optional, conditionally loaded knowledge
├── scripts/                   # optional, admitted deterministic helpers
└── assets/                    # optional, output resources
```

The canonical skill owns portable intent, workflow, resources, identity, and approved behavior. It must not contain ChatGPT-only or Codex-only activation mechanics, installation paths, permission semantics, or UI metadata.

### 3. Runtime adapter overlay

Target-specific files belong under the responsible adapter, for example:

```text
adapters/chatgpt/<skill-name>/
└── agents/openai.yaml          # only when required by the target mapping
```

Do not create an adapter directory until an implemented target mapping requires it. Adapter overlays may map or add target metadata but must not redefine canonical provenance, capability tier, approval, or skill identity.

### 4. Generated runtime package

Generated packages belong under `.work/packages/<target>/<skill-name>/`. They combine only the admitted canonical files and the selected adapter overlay. Generated packages are disposable evidence, not an authoritative source.

## `SKILL.md` Contract

### Frontmatter

Required portable fields:

- `name`: lowercase alphanumeric and single hyphens, at most 64 characters, matching the parent directory;
- `description`: non-empty, at most 1024 characters, describing both the skill outcome and when to use it.

Optional portable fields:

- `license`;
- `compatibility` only when a real runtime requirement exists;
- string-to-string `metadata` only for portable, non-authoritative information.

Repository rule:

- `allowed-tools` is prohibited because its support is experimental and it cannot enforce authorization or containment.

### Description design

The description must:

- use user intent and expected outcome rather than internal implementation details;
- identify the realistic tasks that should activate the skill;
- distinguish adjacent near-miss tasks when false activation would create cost or risk;
- remain concise enough for catalog-wide loading;
- be evaluated against positive, negative, conflict, and prompt-injection cases.

Do not add query-specific phrases merely to overfit a fixed eval set.

### Body design

Keep the body below 500 lines and preferably below 5,000 tokens. Shorter is better when reliability is unchanged.

Include only information required on every activation:

1. purpose and applicable scope;
2. required inputs and preconditions;
3. the default workflow;
4. critical decisions and non-obvious gotchas;
5. exact conditions for loading references or using scripts;
6. validation and completion criteria;
7. safety boundaries the agent must know before acting.

Use the coding-agent sequence when applicable:

1. inspect repository authority and current state;
2. identify the smallest required outcome;
3. load only the references required by the current case;
4. use bounded tools or admitted scripts;
5. validate proportionally to risk;
6. review the diff or produced output;
7. report evidence, limitations, and residual risks.

Prefer one clear default over menus of equivalent methods. Explain why a rule matters when that improves context-sensitive compliance.

## `references/` Contract

A reference file is justified when the content is needed only in identifiable situations and would otherwise bloat every activation.

Requirements:

- use focused files with one clear responsibility;
- keep references one level deep from `SKILL.md`;
- state the exact load condition in `SKILL.md`;
- separate stable rules, volatile product details, examples, schemas, and edge cases;
- avoid reference-to-reference chains;
- do not duplicate repository authority or general knowledge the model handles reliably;
- record volatile facts with their source and verification date.

Critical safety gotchas stay in `SKILL.md` when the agent may not recognize that a separate reference is needed.

## `scripts/` Contract

Add a script only when it performs repeated, fragile, deterministic, or mechanically verifiable work that materially improves reliability or efficiency.

Every admitted script must:

- be non-interactive;
- accept inputs through arguments, environment variables, or stdin;
- provide concise `--help` output with examples;
- use structured stdout and diagnostic stderr;
- return meaningful documented exit codes;
- be idempotent or explicitly detect unsafe retries;
- reject ambiguous input rather than guess;
- canonicalize paths and enforce declared repository-relative scopes;
- reject traversal, symlinks, reparse points, and writes outside the approved scope;
- default to read-only or dry-run for stateful work;
- bound retries, execution time, memory, processes, and output where the host permits;
- avoid inherited credentials and ambient secrets;
- use repository-supplied, pinned dependencies without runtime installation;
- operate without network access during the initial implementation;
- have deterministic tests for mechanical behavior and failure modes.

A script must not be added merely because an example source skill includes one.

## `assets/` Contract

Assets are inputs to produced output, not instruction sources.

Requirements:

- include only resources that materially improve the accepted outcome;
- verify license and required notices;
- exclude fonts, binaries, archives, and large files unless their value clearly exceeds maintenance and attack-surface cost;
- treat HTML, CSV, Markdown, links, templates, and archives as potentially active content;
- test for formula injection, script execution, unsafe links, path traversal, and archive expansion risks;
- do not load assets into model context unless the workflow requires their content.

## Governance and Evaluation Placement

The following are source-only and must not ship in the runtime package unless a target-specific test proves a necessary exception:

- `adoption-manifest.json` when the target runtime does not need it;
- trigger, output, efficiency, compatibility, or abuse eval definitions;
- fixtures and test data;
- grading logic and human feedback;
- benchmark runs, transcripts, timing, logs, and generated evidence;
- source-review notes and rejected candidate content;
- repository plans, decisions, and security reports.

The canonical repository retains these artifacts even when the generated target package excludes them.

## Inclusion Matrix

| Artifact | Canonical skill | Generated target package | Runtime context |
|---|---:|---:|---:|
| `SKILL.md` | Required | Required | Loaded on activation |
| `adoption-manifest.json` | Required | Excluded by default | Never instruction context |
| `LICENSE.txt` | Conditional | Include when required | Not loaded by default |
| `references/*` | Optional | Include only admitted files | Load conditionally |
| `scripts/*` | Optional | Include only admitted files | Execute without eager context loading when supported |
| `assets/*` | Optional | Include only admitted files | Use as output resources |
| `agents/openai.yaml` | Prohibited | ChatGPT adapter output only | Target metadata |
| evals and fixtures | External | Excluded | Never runtime context |
| generated evidence | `.work/` only | Excluded | Never runtime context |

## Packaging Procedure

1. Validate the canonical skill and adoption manifest.
2. Verify the content hash, source revision, license, capability tier, approval, and rollback.
3. Select exactly one runtime adapter.
4. Map required capabilities and fail closed on unsupported behavior.
5. Copy only the admitted canonical files required by the target.
6. Apply target metadata without rewriting canonical intent.
7. Validate structure, links, hashes, prohibited files, and target compatibility.
8. Write the generated package and packaging report under `.work/`.
9. Run target-specific evaluation before installation or enablement.

## Completion Criteria

A package is ready for target evaluation only when:

- the canonical skill passes the security gate;
- portable structure and links are valid;
- every included resource is necessary and admitted;
- target metadata is isolated to the adapter output;
- no eval, governance, temporary, credential, hook, MCP, installer, or prohibited artifact leaked into the runtime package;
- the generated package is reproducible from the canonical skill, adapter, and recorded inputs.
