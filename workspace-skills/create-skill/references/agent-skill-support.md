---
reference_id: agent-skill-support
title: Agent Skill Support Reference
source_file: agents-skills-support.md
source_type: external-implementation-guide
source_authority: source-evidence
verified_date: 2026-07-28
load_when:
  - implementing Agent Skills support in an agent or development tool
  - defining skill discovery scopes, precedence, and trust handling
  - building a skill catalog or activation mechanism
  - managing skill permissions, resources, context retention, or repeated activation
  - adapting skills to local, cloud-hosted, sandboxed, or subagent runtimes
---

# Agent Skill Support Reference

## Purpose

Use this reference when implementing or reviewing Agent Skills support in an AI agent, development tool, client, or runtime adapter.

It summarizes the complete source lifecycle:

1. discover skills;
2. parse `SKILL.md`;
3. disclose available skills;
4. activate selected skills;
5. preserve effective skill context over time.

This is an implementation guide, not the portable package specification. Runtime choices are presented as options where the source allows multiple approaches.

## Load Conditions

Load this file when the task involves:

- selecting skill discovery locations;
- handling project, user, organization, or built-in scopes;
- defining collision precedence;
- applying project trust checks;
- parsing or tolerating malformed skill metadata;
- constructing the model-visible catalog;
- selecting file-read or dedicated-tool activation;
- enabling explicit user activation;
- listing bundled resources without eagerly loading them;
- managing file permissions;
- preserving activated instructions during context compaction;
- avoiding duplicate activation;
- delegating complex skills to subagents.

Do not load this file for ordinary skill authoring unless runtime integration decisions are part of the task.

## Core Principle: Progressive Disclosure

A skills-compatible agent uses three disclosure tiers:

| Tier | Loaded content | Timing | Approximate cost |
|---|---|---|---|
| 1. Catalog | Skill name and description | Session start | About 50–100 tokens per skill |
| 2. Instructions | Full `SKILL.md` content or body | When activated | Under 5,000 tokens recommended |
| 3. Resources | Scripts, references, and assets | When instructions require them | Varies |

The catalog gives the model awareness of available capabilities without paying the cost of every full instruction set. Only relevant skills and resources are loaded.

## Lifecycle Overview

```text
discover
  ↓
parse and diagnose
  ↓
store minimum skill record
  ↓
filter and disclose catalog
  ↓
activate by model or user
  ↓
load instructions
  ↓
load supporting resources on demand
  ↓
preserve and deduplicate active skill context
```

## Step 1: Discover Skills

### Discovery Scopes

Most local agents scan at least:

- project-level skills;
- user-level skills.

Additional possible scopes:

- organization-managed skills;
- skills bundled with the agent;
- user-configured paths;
- ancestor directories up to a repository root;
- XDG configuration locations;
- compatibility locations used by other clients.

### Directory Conventions

| Scope | Path pattern | Status |
|---|---|---|
| Project | `<project>/.<client>/skills/` | Client-native convention |
| Project | `<project>/.agents/skills/` | Cross-client convention |
| User | `~/.<client>/skills/` | Client-native convention |
| User | `~/.agents/skills/` | Cross-client convention |
| Project/User | `.claude/skills/` | Optional compatibility location |

The portable Agent Skills specification defines package contents, not installation locations. Discovery paths are implementation choices.

### Discovery Target

Within a skills directory, discover immediate or bounded subdirectories containing a file named exactly:

```text
SKILL.md
```

Ignore unrelated files such as a top-level `README.md`.

### Bounded Scanning

Practical safeguards:

- skip irrelevant trees such as `.git/` and `node_modules/`;
- optionally respect `.gitignore`;
- cap traversal depth;
- cap the number of scanned directories;
- record diagnostics for skipped or failed locations.

The source gives example bounds of roughly 4–6 directory levels and 2,000 directories. These are examples, not portable specification requirements.

### Collision Precedence

Universal source convention:

```text
project-level skill overrides user-level skill
```

Within the same scope, choose either first-found or last-found precedence, apply it consistently, and warn when one skill shadows another.

### Trust Gate

Project skills may originate from an untrusted repository. Consider loading them only after the user marks the project as trusted.

The purpose is to prevent a newly cloned repository from silently injecting instructions into the agent context.

### Cloud and Sandbox Discovery

| Skill scope | Typical provisioning approach |
|---|---|
| Project | Scan the cloned or mounted repository |
| User | Provision from a configuration repository, uploaded package, URL, or account storage |
| Organization | Managed registry or administrator-controlled source |
| Built-in | Package as deployment assets |

After provisioning, parsing, disclosure, and activation follow the same lifecycle.

## Step 2: Parse `SKILL.md`

### Parsing Sequence

1. Require an opening `---` at the start of the file.
2. Find the closing `---`.
3. Parse the YAML block.
4. Extract required and optional metadata.
5. Treat all remaining content as the Markdown body.

### Malformed YAML Compatibility

Skills authored for other clients may contain YAML accepted by permissive parsers but rejected by strict parsers. A common case is an unquoted colon in a scalar:

```yaml
description: Use this skill when: the user asks about PDFs
```

The source suggests an optional compatibility fallback, such as:

- quoting the affected scalar;
- converting it to a YAML block scalar;
- retrying the parse.

Any repair should produce a diagnostic rather than silently hiding the issue.

### Lenient Runtime Validation

The implementation guide deliberately distinguishes runtime compatibility from strict package conformance.

| Condition | Runtime handling |
|---|---|
| Name differs from parent directory | Warn and load when possible |
| Name exceeds 64 characters | Warn and load when possible |
| Description missing or empty | Skip and log an error |
| YAML completely unparseable | Skip and log an error |
| Cosmetic or non-critical issue | Record diagnostic; do not block loading |

Strict conformance remains owned by the package specification. Lenient loading exists to improve interoperability.

### Minimum Skill Record

Store at least:

| Field | Source |
|---|---|
| `name` | Frontmatter |
| `description` | Frontmatter |
| `location` | Absolute path to `SKILL.md` |

Use a map keyed by `name` for activation lookup.

The base directory is the parent of `location`; use it to resolve relative paths and enumerate bundled resources.

### Store Body or Load Later

| Strategy | Benefit | Cost |
|---|---|---|
| Store body during discovery | Faster activation | More aggregate memory; may not reflect later file changes |
| Read body at activation | Lower aggregate memory; observes file changes | Additional activation-time file read |

Choose according to runtime constraints.

## Step 3: Disclose Skills to the Model

### Catalog Record

For each available skill, disclose:

- `name`;
- `description`;
- optionally `location`.

`location` is useful when:

- activation uses file reads;
- the model must resolve relative resource paths.

It may be omitted when a dedicated activation tool returns the skill directory.

Example:

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extract PDF text, fill forms, merge files. Use when handling PDFs.</description>
    <location>/home/user/.agents/skills/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```

### Catalog Placement

| Option | Strength |
|---|---|
| System prompt section | Simplest and broadly compatible |
| Dedicated activation-tool description | Keeps the system prompt cleaner and couples discovery with activation |

Both approaches are source-supported.

### Behavioral Instruction

Tell the model:

- skills provide specialized instructions;
- it must load a matching skill before proceeding;
- how activation occurs;
- how relative paths are resolved.

Keep the catalog instruction concise. Detailed behavior belongs in the activated skill.

### Catalog Filtering

Hide unavailable skills entirely when:

- disabled by the user;
- denied by permissions;
- excluded from model-driven activation.

Do not expose a skill and then block every activation attempt.

### Empty Catalog

When no skills are available:

- omit the catalog;
- omit skill-use behavioral instructions;
- do not display an empty catalog element;
- do not register an activation tool with no valid skill names.

## Step 4: Activate Skills

### Model-Driven Activation

The common pattern is model judgment:

1. model reads the catalog;
2. model matches the task to a description;
3. model loads the selected skill.

The source does not require harness-side keyword matching.

### Activation Patterns

| Pattern | Use when | Characteristics |
|---|---|---|
| File-read activation | Model can access files | Simplest; uses existing file-read capability |
| Dedicated activation tool | Model cannot read files, or stronger control is needed | Can validate names, enforce permissions, wrap content, list resources, and track activation |

For a dedicated tool, constrain the skill-name input to discovered names. Do not register the tool when no skills are available.

### User-Explicit Activation

Provide a direct user path, such as:

- `/skill-name`;
- `$skill-name`;
- mention syntax;
- autocomplete selection.

The harness should resolve and inject the selected skill so the model does not need a separate activation turn.

### Content Delivered at Activation

Two source-supported options:

| Option | Behavior |
|---|---|
| Full file | Deliver YAML frontmatter and Markdown body |
| Body only | Parse and remove frontmatter before delivery |

Both work. Full-file delivery may preserve compatibility information useful at execution time. Body-only delivery is common for dedicated tools.

### Structured Wrapping

A dedicated tool may wrap activated content:

```xml
<skill_content name="pdf-processing">
[SKILL.md instructions]

Skill directory: /home/user/.agents/skills/pdf-processing
Relative paths in this skill are relative to the skill directory.

<skill_resources>
  <file>scripts/extract.py</file>
  <file>references/pdf-spec-summary.md</file>
</skill_resources>
</skill_content>
```

Benefits:

- separates skill instructions from other context;
- supports later identification during compaction;
- exposes resource names without loading their contents;
- communicates the base directory for relative paths.

### Resource Enumeration

When activating a skill:

- list bundled scripts, references, and assets when useful;
- do not eagerly read every resource;
- let the model load specific files on demand;
- cap very large listings and indicate incompleteness.

### Permission Allowlisting

When file access is permission-gated, consider allowlisting the skill directory so normal use of bundled resources does not trigger repeated confirmation prompts.

This is a runtime permission choice, not authorization granted by skill metadata.

## Step 5: Manage Skill Context

### Protect Activated Instructions

Skill instructions are durable behavioral context. Exempt them from pruning or ordinary summarization during context compaction.

Possible mechanisms:

- mark activation outputs as protected;
- identify wrapped skill content by structured tags;
- rehydrate protected skill content after compaction.

Losing activated instructions may silently degrade behavior without producing an explicit error.

### Deduplicate Activation

Track skills activated in the current session. When the same skill is requested again:

- reuse the existing active instructions;
- avoid injecting duplicate copies;
- reload only when the runtime intentionally supports refresh semantics.

### Subagent Delegation

An optional advanced pattern:

1. create a separate subagent session;
2. inject the selected skill into that session;
3. let the subagent perform the focused workflow;
4. return a summary or result to the main conversation.

Use this for workflows that benefit from isolated context. It is not required for skills support.

## Runtime Decision Table

| Decision | Source-supported options | Selection criterion |
|---|---|---|
| Skill source | Filesystem, registry, upload, bundled asset | Deployment environment |
| Discovery paths | Client-native, `.agents/skills/`, compatibility paths | Interoperability goals |
| Catalog placement | System prompt or tool description | Runtime architecture |
| Activation | File read or dedicated tool | File access and control requirements |
| Activation payload | Full file or body only | Metadata needs and parser design |
| Body storage | Discovery time or activation time | Memory, freshness, and latency |
| Resource handling | Enumerate, then load on demand | Context efficiency |
| Context preservation | Protected messages or identifiable wrappers | Compaction implementation |
| Complex execution | Main session or subagent | Workflow isolation needs |

## Agent Implementation Checklist

### Discovery

- [ ] project and user scopes are defined;
- [ ] optional organization and built-in scopes are explicit;
- [ ] discovery paths are bounded;
- [ ] `.git/`, `node_modules/`, and other irrelevant trees are excluded;
- [ ] collision precedence is deterministic;
- [ ] project-level skills override user-level skills;
- [ ] shadowing produces a diagnostic;
- [ ] project trust is considered.

### Parsing

- [ ] frontmatter delimiters are recognized;
- [ ] YAML and Markdown body are separated;
- [ ] required fields are extracted;
- [ ] malformed YAML produces diagnostics;
- [ ] missing descriptions cause the skill to be skipped;
- [ ] strict conformance and lenient runtime loading are not conflated;
- [ ] each record stores `name`, `description`, and `location`.

### Disclosure

- [ ] the catalog contains only usable skills;
- [ ] catalog entries include name and description;
- [ ] location is included when required for file reads or path resolution;
- [ ] model instructions explain how to activate skills;
- [ ] filtered skills are hidden;
- [ ] empty catalogs and unusable activation tools are omitted.

### Activation

- [ ] model-driven activation is supported;
- [ ] users have an explicit activation path;
- [ ] file-read or dedicated-tool behavior is defined;
- [ ] dedicated tools constrain skill names;
- [ ] the activation payload format is documented;
- [ ] relative paths resolve from the skill directory;
- [ ] bundled resources are enumerated without eager loading;
- [ ] permission handling does not create repeated unnecessary prompts.

### Context Management

- [ ] activated skill instructions survive compaction;
- [ ] duplicate activations are suppressed;
- [ ] refresh behavior is explicit when supported;
- [ ] optional subagent delegation is isolated and observable.

## Edge Cases and Failure Handling

| Situation | Recommended handling |
|---|---|
| Untrusted project | Do not load project skills until trust is established |
| Duplicate skill names | Apply deterministic precedence and warn |
| Invalid but repairable YAML | Attempt bounded fallback and record a diagnostic |
| Missing description | Skip the skill |
| Completely unparseable file | Skip and log the error |
| Permission-denied skill | Exclude it from the model-visible catalog |
| No skills available | Omit the catalog and activation tool |
| Hallucinated dedicated-tool name | Reject through an enum or equivalent constrained input |
| Large resource directory | Cap the listing and state that it is incomplete |
| Repeated activation | Avoid duplicate instruction injection |
| Context compaction | Preserve activated instructions |
| Local user skills in a cloud sandbox | Provision from an external source |

## Portable Versus Runtime-Specific

| Concern | Portable package specification | Runtime implementation |
|---|---:|---:|
| `SKILL.md` format | Yes | Consumes it |
| Frontmatter field constraints | Yes | May apply lenient compatibility handling |
| Skill installation paths | No | Yes |
| Scope precedence | No | Yes |
| Project trust | No | Yes |
| Catalog format | No | Yes |
| Activation mechanism | No | Yes |
| Permission enforcement | No | Yes |
| Context preservation | No | Yes |
| Subagent delegation | No | Optional |

## Source Traceability

This reference summarizes:

- `agents-skills-support.md`

Source topics retained:

- progressive disclosure;
- discovery scopes and directory conventions;
- bounded scanning;
- collision precedence;
- trust considerations;
- cloud and sandbox provisioning;
- frontmatter parsing;
- malformed YAML;
- lenient validation;
- minimum stored fields;
- catalog construction and placement;
- filtering and empty-catalog handling;
- model-driven and user-explicit activation;
- file-read and dedicated-tool activation;
- full-file and body-only delivery;
- structured wrapping;
- resource enumeration;
- permission allowlisting;
- context preservation;
- activation deduplication;
- optional subagent delegation.

No outside facts were added.
