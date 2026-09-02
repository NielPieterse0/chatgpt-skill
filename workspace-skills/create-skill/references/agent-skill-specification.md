---
reference_id: agent-skill-specification
title: Agent Skill Specification Reference
source_file: agent-skills-specification.md
source_type: external-specification
source_authority: source-evidence
verified_date: 2026-07-28
load_when:
  - creating a new Agent Skill package
  - validating or restructuring SKILL.md
  - deciding whether content belongs in SKILL.md, references, scripts, or assets
  - checking naming, frontmatter, path, progressive-disclosure, or validation requirements
---

# Agent Skill Specification Reference

## Purpose

Use this reference when creating, reviewing, or validating an Agent Skill package. It summarizes the package structure, `SKILL.md` contract, optional resources, progressive-disclosure model, file-reference rules, and validation guidance defined by the source specification.

This artifact is source-derived. It does not add client-specific runtime behavior or repository policy.

## Load Conditions

Load this file when the task requires one or more of the following:

- create a new skill package;
- validate or repair a `SKILL.md`;
- define required or optional frontmatter;
- decide where detailed content or executable resources belong;
- reduce the context cost of a large skill;
- verify skill naming and relative-path rules;
- prepare a package for structural validation.

Do not load this file merely to execute an already-understood skill workflow.

## Core Package Model

A skill is a directory containing at least one required file:

```text
skill-name/
├── SKILL.md          # Required: metadata and instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: supporting documentation
├── assets/           # Optional: templates and static resources
└── ...               # Additional files or directories are permitted
```

`SKILL.md` consists of:

1. YAML frontmatter delimited by `---`;
2. a Markdown instruction body after the closing delimiter.

## Required Frontmatter

| Field | Required | Constraints | Intended use |
|---|---:|---|---|
| `name` | Yes | 1–64 characters; lowercase letters, numbers, and hyphens only; no leading, trailing, or consecutive hyphens; must match parent directory | Stable skill identifier |
| `description` | Yes | 1–1024 characters; non-empty; describes what the skill does and when to use it | Catalog discovery and activation matching |

Minimal form:

```yaml
---
name: skill-name
description: Describe what the skill does and when it should be used.
---
```

## Optional Frontmatter

| Field | Constraints | Guidance |
|---|---|---|
| `license` | License name or reference to a bundled license file | Keep concise |
| `compatibility` | 1–500 characters when present | Include only for material environment requirements such as intended product, required packages, network access, or runtime version |
| `metadata` | Mapping of string keys to string values | Use reasonably unique keys to reduce collisions |
| `allowed-tools` | Space-separated pre-approved tool string | Experimental; implementation support may vary |

Example:

```yaml
---
name: pdf-processing
description: Extracts PDF text and tables, fills forms, and merges PDFs. Use when handling PDF documents, forms, or document extraction.
license: Apache-2.0
compatibility: Requires Python and access to local PDF files
metadata:
  author: example-org
  version: "1.0"
---
```

## `name` Decision Rules

| Check | Valid condition | Failure example |
|---|---|---|
| Length | 1–64 characters | More than 64 characters |
| Character set | `a-z`, `0-9`, `-` | `PDF-Processing` |
| Start/end | Must begin and end with an alphanumeric character | `-pdf`, `pdf-` |
| Repeated separators | No `--` | `pdf--processing` |
| Directory match | Must equal the parent directory name | Directory `pdf-tools/`, name `pdf-processing` |

Examples of valid names:

```yaml
name: pdf-processing
name: data-analysis
name: code-review
```

## `description` Decision Rules

A description should answer both questions:

1. What capability does the skill provide?
2. When should an agent use it?

It should include concrete task and domain keywords that support correct catalog matching.

Good:

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents, forms, or document extraction.
```

Weak:

```yaml
description: Helps with PDFs.
```

## Markdown Body

The body contains the operational instructions loaded when the skill activates. The source specification imposes no fixed body schema.

Recommended content:

- step-by-step instructions;
- representative inputs and outputs;
- common edge cases;
- explicit references to supporting files when needed.

The complete body is loaded at activation time. Move lengthy or specialized details into focused reference files rather than expanding `SKILL.md` indefinitely.

## Optional Resource Directories

### `scripts/`

Use for executable code an agent may run.

Scripts should:

- be self-contained or clearly document dependencies;
- produce helpful error messages;
- handle expected edge cases gracefully.

Supported languages depend on the agent implementation. Common examples include Python, Bash, and JavaScript.

### `references/`

Use for supporting documentation loaded only when required.

Typical contents:

- detailed technical references;
- schemas and structured formats;
- form templates;
- domain-specific guidance;
- extended examples or edge cases.

Keep each reference focused. Smaller, task-specific files reduce context usage during on-demand loading.

### `assets/`

Use for static resources such as:

- document or configuration templates;
- diagrams and example images;
- lookup tables;
- schemas or data files.

## Progressive Disclosure

Agent Skills use three disclosure tiers:

| Tier | Content | Loaded when | Source guidance |
|---|---|---|---|
| 1. Metadata | `name` and `description` | Session startup or catalog construction | Approximately 100 tokens per skill |
| 2. Instructions | Full `SKILL.md` body | Skill activation | Keep below approximately 5,000 tokens |
| 3. Resources | Scripts, references, and assets | Only when required by the instructions | Cost varies by resource |

Design implications:

- keep the catalog metadata precise;
- keep `SKILL.md` operational and compact;
- move deep detail into focused resources;
- load supporting files only when the active task requires them;
- keep the main `SKILL.md` under 500 lines.

## File Reference Rules

Reference bundled files using paths relative to the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run:
scripts/extract.py
```

Rules:

- use relative paths from the skill root;
- keep references one level deep from `SKILL.md`;
- avoid chains where one reference requires another reference before it can be understood;
- make the referenced file's purpose clear at the point of use.

## Placement Decision Table

| Content | Preferred location |
|---|---|
| Skill identity and activation description | `SKILL.md` frontmatter |
| Core workflow and mandatory operating instructions | `SKILL.md` body |
| Detailed domain knowledge | `references/` |
| Extended examples, schemas, or edge cases | `references/` |
| Deterministic executable logic | `scripts/` |
| Templates, diagrams, lookup data, or static resources | `assets/` |
| Client-specific behavior not defined by the package specification | Separate runtime or adapter documentation |

## Validation

The source recommends the `skills-ref` reference library:

```bash
skills-ref validate ./my-skill
```

The validator checks:

- `SKILL.md` frontmatter;
- required fields;
- naming conventions;
- package conformance covered by the reference implementation.

## Agent Checklist

Before treating a package as specification-conformant, verify:

- [ ] the skill directory contains `SKILL.md`;
- [ ] frontmatter begins and ends with `---`;
- [ ] `name` exists and matches the parent directory;
- [ ] `name` satisfies length, character, and hyphen rules;
- [ ] `description` exists and states both capability and use conditions;
- [ ] optional fields satisfy their constraints;
- [ ] the Markdown body contains actionable instructions;
- [ ] detailed content is separated into focused references where useful;
- [ ] scripts document dependencies and handle failures;
- [ ] bundled paths are relative to the skill root;
- [ ] references are not deeply nested;
- [ ] the main `SKILL.md` remains under 500 lines;
- [ ] structural validation has been run when the validator is available.

## Edge Cases and Failure Handling

| Situation | Source-supported treatment |
|---|---|
| `SKILL.md` missing | The directory is not a valid skill package |
| `name` differs from directory | Fails the strict specification |
| `description` is vague | Rewrite it to state capability and activation conditions |
| `compatibility` has no material requirement | Omit the field |
| Large instructions | Move detailed material into `references/` |
| Deep reference chains | Flatten to one-level references |
| Script depends on external software | Document the dependency clearly |
| `allowed-tools` is unsupported by a client | Treat it as experimental and client-dependent |

## Non-Portable or Experimental Elements

The package specification defines what is inside a skill directory. It does not mandate where skill directories are installed or how a particular agent discovers and activates them.

`allowed-tools` is explicitly experimental. A package must not assume uniform support across implementations.

Runtime-specific matters outside this reference include:

- discovery paths and scope precedence;
- trust gates;
- activation tools or mention syntax;
- permission enforcement;
- context retention;
- client UI metadata.

## Source Traceability

This reference summarizes:

- `agent-skills-specification.md`

Source topics retained:

- directory structure;
- `SKILL.md` frontmatter;
- field constraints;
- Markdown body guidance;
- optional directories;
- progressive disclosure;
- file references;
- validation.

No outside facts were added.
