# Deep Research Brief: Secure ChatGPT Skill Adoption

## Authority

This document defines the focused research required before this repository adopts or activates Agent Skills for OpenAI ChatGPT-oriented coding workflows.

The portable-core and runtime-adapter boundary is governed by [`docs/architecture/skill-runtime-adapters.md`](../architecture/skill-runtime-adapters.md). This research may test that decision and propose an explicit amendment, but must not silently replace it.

It is a research brief, not an implementation specification, security approval, or adoption decision. Accepted findings must be converted into the appropriate repository-owned specification, architecture, security, testing, or decision artifact before implementation.

## Status

- **State:** Proposed research scope
- **Research date:** 2026-07-26
- **Initial target:** OpenAI ChatGPT used as a chat-based coding agent
- **Future target path:** Codex through a separate runtime adapter, not a duplicate adoption core
- **Primary outcome:** A minimal, secure, testable, maintainable, and adapter-driven skill-adoption architecture

## Research Objective

Determine the smallest effective system that lets ChatGPT use repository-owned skills to improve coding-agent outcomes while preserving:

- portable Agent Skills compliance;
- a host-independent canonical adoption core;
- OpenAI-specific compatibility through the initial ChatGPT adapter;
- a credible future Codex adapter path without duplicating canonical records;
- progressive disclosure and low context cost;
- bounded filesystem, tool, network, and credential access;
- measurable value over an unskilled baseline;
- reproducible provenance, validation, rollback, and maintenance.

The central question is:

> What is the minimum skill package, governance model, runtime boundary, and evaluation loop that produces material coding-agent value in ChatGPT without importing unnecessary complexity or latent supply-chain risk?

## Required Source Set

### Portable Agent Skills authority

Research must reconcile the complete supplied Agent Skills set:

1. [`agent-skills-specification.md`](../../references/agent-skills-specification.md) — package structure, frontmatter, progressive disclosure, references, scripts, assets, and structural validation.
2. [`skills-best-practice.md`](../../references/skills-best-practice.md) — scope, context discipline, procedures, gotchas, templates, validation loops, and resource selection.
3. [`optimising-skill-description.md`](../../references/optimising-skill-description.md) — activation descriptions, positive and near-miss trigger cases, repeated runs, and train/validation splits.
4. [`evaluating-skills.md`](../../references/evaluating-skills.md) — with-skill versus baseline evaluation, assertions, evidence, human review, timing, and token cost.
5. [`using-scripts-skills.md`](../../references/using-scripts-skills.md) — script interfaces, dependency control, structured output, idempotency, dry runs, and bounded output.
6. [`agents-skills-support.md`](../../references/agents-skills-support.md) — discovery, catalogs, activation, resource loading, trust, collision handling, context preservation, and deduplication.
7. [`skills-knowledge-source-register.md`](../../references/skills-knowledge-source-register.md) — repository source hierarchy, provenance, licensing, product authority, and adoption gates.

Local snapshots are research inputs. Live sources must be checked before a repository decision is accepted.

### OpenAI product authority

Use current OpenAI documentation and owner-maintained implementations to establish ChatGPT-specific behavior:

- OpenAI Help: Skills in ChatGPT.
- OpenAI Academy: Using skills.
- OpenAI Skills catalog.
- OpenAI `skill-creator`, including `agents/openai.yaml` and its resource-generation guidance.

Research must distinguish:

- portable Agent Skills requirements;
- OpenAI-supported extensions;
- Codex-only conventions;
- ChatGPT behavior that requires empirical verification.

### Security evidence

Use the attached **Skills Security Deep Dive** as source evidence. Store it under `references/` with provenance before treating it as a durable repository source; it is not yet an authoritative security standard.

The research must address every material finding, especially:

- unrestricted shell or write permissions;
- lifecycle hooks and automatic dependency installation;
- remote MCP trust and wildcard permissions;
- recursive discovery of quarantined references;
- skill poisoning and name shadowing;
- transcript, diff, path, identity, and credential exposure;
- unbounded loops, retries, token use, and cancellation blocking;
- missing provenance and tamper evidence;
- runtime download-and-execute patterns;
- writes outside the repository boundary;
- prompt injection through files, tool output, MCP responses, and generated content;
- active-output injection in HTML, CSV, Markdown, links, and archives;
- non-portable permission semantics;
- missing trigger, output, and abuse evaluation.

Use OWASP AI Agent Security guidance as the external security baseline. Product upload scanning is a supplementary signal, not the repository security boundary.

## Scope

### In scope

- The portable and OpenAI-specific skill package contract.
- `SKILL.md` content, frontmatter, description, control level, and context budget.
- Conditional `references/` loading and reference ownership.
- Deterministic `scripts/` design and execution boundaries.
- `assets/` handling and active-output risks.
- OpenAI UI metadata under `agents/openai.yaml`.
- Trigger, output, efficiency, compatibility, and abuse evals.
- Provenance, licensing, capability declarations, approval, packaging, and revocation.
- ChatGPT activation, explicit invocation, tool use, repository editing, validation, and reporting.
- The minimum repository structure and automation needed to enforce the result.

### Out of scope

- Adopting a large skill catalog.
- General plugin or MCP platform design unrelated to an adopted skill.
- Autonomous deployment, publication, credentialed external mutation, or production operations.
- Background agents, infinite loops, lifecycle hooks, or silent package installation.
- Implementing the future Codex adapter or full cross-client parity; the research must still preserve and test the adapter boundary needed to add it later.
- Building controls that ChatGPT cannot enforce unless a practical host-side enforcement point exists.

## Research Questions

### 1. Portable skill package

1. Which files are required, optional, source-only, or prohibited in an installable ChatGPT skill?
2. What belongs in `SKILL.md` because it is needed on every activation, and what must move to conditional references?
3. Which gotchas and safety constraints must remain in `SKILL.md` because the agent may not recognize when to load a separate reference?
4. Should evals and governance metadata ship with the skill, or remain external to keep the runtime package minimal?
5. Which Agent Skills fields are portable, and which OpenAI fields require an adapter layer?

### 2. ChatGPT coding-agent behavior

1. How does ChatGPT discover, activate, combine, and explicitly invoke skills in the target workspace?
2. What tool, file, and connector controls are actually enforceable in ChatGPT rather than merely declared in frontmatter?
3. How should a skill encode the coding-agent workflow: inspect, decide, edit, validate, review, and report?
4. How are skill instructions preserved during long conversations and context compaction?
5. What observability exists for activation, resource loading, tool use, failure, and user approval?

### 3. References and context efficiency

1. What is the minimum `SKILL.md` context needed to produce a reliable behavior change?
2. Which reference files should be loaded by explicit conditions rather than generic links?
3. How should references separate authoritative rules, API details, examples, templates, and edge cases?
4. What limits prevent deep chains, duplicated authority, stale guidance, or context flooding?

### 4. Scripts and deterministic execution

1. When does a bundled script create enough reliability or efficiency to justify its security and maintenance cost?
2. Which languages and runtimes are available in the target ChatGPT execution surface?
3. How will scripts enforce repository-only paths, non-interactive operation, safe defaults, timeouts, output limits, and deterministic exit codes?
4. How will dependencies be pinned and supplied without runtime installation or uncontrolled network access?
5. How will destructive or external operations be blocked, dry-run first, or require explicit user confirmation?

### 5. Security and supply chain

1. What is the enforceable boundary between `references/`, adopted `skills/`, and generated `.work/` artifacts?
2. Where are provenance, immutable source revision, hash, license, capabilities, approvals, and rollback recorded?
3. How are symlinks, traversal, name collisions, recursive discovery, hidden files, and unexpected executables rejected?
4. Which capability tiers may auto-activate, require explicit invocation, or require per-action confirmation?
5. How are untrusted instructions in source code, documents, tool output, MCP responses, and filenames isolated as data?
6. What controls prevent secret, transcript, diff, customer, or machine-identity egress?
7. What emergency disable, quarantine, revocation, and incident evidence are required?

### 6. Evaluation and release

1. Does the skill trigger for realistic positive cases and avoid adjacent near-misses?
2. Does it produce better outcomes than ChatGPT without the skill or with the previous version?
3. What quality improvement justifies added tokens, time, tool calls, and maintenance?
4. Which assertions are deterministic, which require model grading, and which require human review?
5. Which abuse cases must pass before automatic activation is permitted?
6. What evidence is required to adopt, update, suspend, or remove a skill?

## Provisional Target Architecture
The research should attempt to falsify or confirm this minimal design while conforming to the authoritative adapter boundary.

```text
skills/<skill-name>/                  Canonical repository-owned adopted skill
├── SKILL.md                          Portable activation metadata + core workflow
├── references/                       Conditionally loaded knowledge
├── scripts/                          Deterministic bounded helpers only
├── assets/                           Output resources; not instructions
└── LICENSE.txt                       Skill license when applicable

adapters/chatgpt/                     Initial target adapter
├── adapter contract + capability map
├── OpenAI metadata or overlays       Including agents/openai.yaml when required
└── target packaging + validation

adapters/codex/                       Future target adapter; not implemented in this research

governance/skills/<skill-name>.yaml   Canonical provenance, risk, approval, and hash

tests/skills/<skill-name>/
├── trigger-cases.json                Positive, near-miss, conflict, injection cases
├── output-evals.json                 Baseline tasks and objective assertions
├── abuse-cases.json                  Filesystem, input, egress, retry, output attacks
└── fixtures/                         Bounded synthetic inputs

tests/adapters/chatgpt/               ChatGPT contract and target behavior tests

tools/
├── validate-skill.*                  Structure, links, manifests, policies, hashes
└── package-skill.*                   Combine an admitted skill with one selected adapter

.work/packages/chatgpt/               Generated ChatGPT runtime packages
.work/evals/<skill-name>/              Generated runs, grading, timing, and evidence
```

Do not create empty adapter scaffolding. Introduce `adapters/chatgpt/` only with the first implemented target mapping.

### Rationale to validate

- **Canonical skills stay portable.** Target metadata and activation mechanics do not become part of the authoritative cross-target skill record.
- **Runtime packages stay lean.** The packager combines only the admitted canonical files and ChatGPT adapter material required by the target.
- **Governance stays authoritative and machine-readable.** Provenance and approval are not mixed into model instructions or duplicated by adapters.
- **Evals stay outside the runtime package.** Test data and grading logic do not consume skill context or expand the uploaded attack surface unless packaging tests prove a better layout.
- **OpenAI metadata remains an adapter concern.** `agents/openai.yaml` may appear in a generated ChatGPT package but must not redefine the portable skill contract.
- **A future Codex target reuses the core.** It must consume the same canonical skill and governance records through a separate adapter.
- **Generated evidence stays disposable.** Iteration outputs belong in `.work/`, while accepted decisions and standards move into `docs/`, `governance/`, or tests.

## Provisional Design Rules

The final research may revise these rules only with evidence.

### `SKILL.md`

- Keep the portable `name` and `description` fields authoritative for activation.
- Use an intent-based description that says when to use the skill and identifies adjacent exclusions.
- Keep the body below the specification guidance and materially shorter where possible.
- Include only the core workflow, required decisions, critical gotchas, resource-loading conditions, validation loop, and completion criteria.
- Prefer one clear default over menus of equivalent methods.
- Encode the coding-agent sequence as:
  1. inspect repository authority and state;
  2. identify the smallest required change;
  3. load only needed references;
  4. use bounded tools or scripts;
  5. validate proportionally to risk;
  6. review the diff or output;
  7. report evidence, limitations, and remaining risks.
- Do not treat `allowed-tools` as the security boundary; support is experimental and product-dependent.

### `references/`

- Give every governed fact one authoritative owner.
- Keep files focused and shallow; avoid reference-to-reference chains.
- State the exact condition for loading each reference from `SKILL.md`.
- Separate stable rules from examples and volatile product/API details.
- Do not duplicate repository authority or general knowledge the model already handles reliably.

### `scripts/`

- Add a script only for repeated, fragile, deterministic, or mechanically verifiable work.
- Require non-interactive flags or stdin, concise `--help`, structured stdout, diagnostic stderr, meaningful exit codes, idempotency, and bounded output.
- Canonicalize and validate all paths against the repository root; reject traversal, links, and reparse points.
- Default to read-only or dry-run; writes must target declared repository paths.
- Disable network and inherited credentials by default.
- Prohibit runtime dependency installation in the initial implementation.
- Pin dependencies and integrity data in the repository-owned build or execution environment.
- Enforce timeout, process, memory, retry, and output limits outside the model instructions where possible.

### `assets/`

- Treat assets as output inputs, not instruction sources.
- Scan templates and generated HTML, CSV, Markdown, links, and archives for active-content or formula injection.
- Exclude fonts, binaries, and large resources unless they materially improve the accepted outcome and their license is verified.

### Evals

Use the smallest useful evaluation set first:

- **Trigger:** 6 realistic positives, 6 near-miss negatives, 2 conflict cases, and 2 prompt-injection cases; run repeatedly where ChatGPT observability permits.
- **Output:** 3 representative tasks with and without the skill, objective assertions, evidence-based grading, and human review.
- **Abuse:** path traversal, malicious filenames/content, secret-bearing input, denied network, cancellation, retry/idempotency, and active-output injection.
- **Efficiency:** capture available duration, token, tool-call, and retry signals; reject skills whose marginal value does not justify their cost.

Expand test counts only when early evidence shows ambiguity, nondeterminism, material risk, or insufficient coverage.

## Capability Model to Evaluate

| Tier | Capability | Proposed activation |
|---|---|---|
| 0 | Instructions only; no tools | Automatic after trigger validation |
| 1 | Repository read-only | Automatic in a trusted project after trigger validation |
| 2 | Bounded repository writes | Explicit invocation or approval before mutation |
| 3 | Network, package resolution, external data | Per-run approval and enforced allowlists |
| 4 | Credentials, Git publication, deployment, deletion, hooks, external mutation | Explicit invocation plus action-level confirmation; excluded from the initial implementation |

The initial proof should use only Tier 0 or Tier 1. Tier 2 may be evaluated only after repository-bound write enforcement exists. Tiers 3 and 4 are research-only until separate controls and approval are accepted.

## Security Control Mapping

Every security finding must be converted into this evidence format:

| Field | Required content |
|---|---|
| Finding | Source finding and affected artifact pattern |
| Threat | Credible attacker, trust boundary, and impact |
| Control | Preventive, detective, and recovery controls |
| Enforcement point | Repository validator, packager, ChatGPT setting, tool policy, script runner, or human approval |
| Test | Static check, runtime abuse case, or manual review evidence |
| Residual risk | Risk that ChatGPT or the repository cannot enforce |
| Decision | Accept, mitigate, exclude, defer, or reject |

A prose instruction in `SKILL.md` is not an enforcement point for filesystem, network, credentials, destructive actions, or authorization.

## Research Method

### Phase 1: Reconcile authorities

- Compare local snapshots with current Agent Skills and OpenAI sources.
- Build a compact requirements matrix: portable, OpenAI extension, repository decision, and unresolved behavior.
- Record conflicts without silently choosing a source.

### Phase 2: Map threats to enforceable controls

- Validate each supplied security finding against the reference corpus.
- Separate controls ChatGPT provides from controls the repository must implement.
- Reject controls that rely only on model obedience for authorization or containment.

### Phase 3: Design the minimum package and lifecycle

- Define runtime package contents and source-only artifacts.
- Define adoption, packaging, installation, activation, update, suspension, and removal flows.
- Define capability tiers and the initial deny list.

### Phase 4: Prototype one low-risk skill

- Select one narrow Tier 0 or Tier 1 coding workflow with real project evidence.
- Build only the files required to test the architecture.
- Do not adopt a complex external skill as the first proof.

### Phase 5: Evaluate value and abuse resistance

- Run trigger, output, efficiency, and abuse evaluations.
- Compare against no-skill and, when applicable, previous-skill baselines.
- Inspect execution traces for wasted work, ignored instructions, and hidden retries.

### Phase 6: Decide and specify

- Accept, revise, or reject the provisional architecture.
- Produce repository-owned standards and a sequenced implementation backlog.
- Stop when the minimum architecture is decision-ready; do not expand into catalog adoption.

## Required Research Outputs

1. **Executive findings:** decisive conclusions, unsupported assumptions, and product constraints.
2. **Requirements matrix:** portable specification, OpenAI behavior, security requirement, and repository decision.
3. **Skill package standard:** exact responsibilities for `SKILL.md`, `agents/`, `references/`, `scripts/`, `assets/`, license, and packaging exclusions.
4. **ChatGPT coding-agent architecture:** discovery, activation, repository access, tool use, approval, context handling, and completion flow.
5. **Security standard:** capability tiers, deny list, provenance, sandboxing, egress, secrets, prompt injection, output safety, revocation, and incident controls.
6. **Evaluation standard:** trigger, output, efficiency, compatibility, human review, and abuse gates.
7. **Machine-readable schemas:** adoption manifest and evaluation formats only where automation will consume them.
8. **Implementation backlog:** P0, P1, and P2 controls with dependency order, owner, evidence, and stop criteria.
9. **Prototype evidence:** one low-risk skill demonstrating whether the architecture materially improves ChatGPT outcomes.

## Initial Deny List

The first implementation must reject or exclude:

- recursive repository-wide skill discovery;
- activation from `references/` or `.work/`;
- symlinks or reparse points in skill packages;
- duplicate or shadowed skill names;
- unrestricted shell, write, edit, or MCP wildcards;
- lifecycle hooks;
- runtime package installation;
- remote download-and-execute instructions;
- inherited credentials or ambient secrets;
- transcript mining;
- external transmission of repository diffs without explicit approval;
- infinite loops, unbounded retries, or cancellation blocking;
- Git commit, push, PR creation, deployment, deletion, or external mutation;
- writes outside `C:\Projects\ChatGPT-skill-adoption`;
- unpinned external dependencies or mutable source revisions.

## Decision Criteria

Recommend adoption only when all applicable criteria are evidenced:

```text
structurally valid
+ portable core identified
+ OpenAI extensions isolated
+ source and license verified
+ immutable revision and hash recorded
+ permissions minimized and enforceable
+ repository and egress boundaries tested
+ dependencies controlled
+ trigger precision demonstrated
+ output value demonstrated over baseline
+ abuse tests passed
+ human review recorded
+ rollback and disable path verified
```

Reject or defer a skill when:

- ChatGPT already performs the task reliably without it;
- the skill adds more context or maintenance cost than measurable value;
- critical behavior depends on unsupported client semantics;
- permissions cannot be enforced outside model instructions;
- provenance or licensing is incomplete;
- scripts require uncontrolled installation, credentials, network, or external writes;
- trigger ambiguity creates material false activation risk;
- the skill cannot be safely disabled or rolled back.

## Completion Criteria

The research is complete when:

- every required source has been reconciled and dated;
- every material security finding maps to an enforcement point and test;
- the runtime/source/test/governance boundaries are explicit;
- the ChatGPT-specific architecture distinguishes verified behavior from assumptions;
- one low-risk prototype has baseline, skilled, efficiency, and abuse evidence;
- P0 controls are specified before any broader adoption;
- unresolved product limitations and residual risks are explicit;
- the resulting implementation plan is bounded, sequenced, and ready for approval.

## Stop Rule

Stop after the minimum secure architecture and one representative proof are decision-ready. Do not begin broad skill adoption, remote MCP integration, lifecycle automation, credentialed actions, or external publication as part of this research.
