# Skill Adoption Research Synthesis

## Authority

This document is the repository-owned synthesis of the completed skill-adoption research. It owns cross-source conclusions, evidence classification, unresolved assumptions, and the status of the research outputs.

It does not replace the authoritative implementation owners:

- portable/runtime boundary: [`docs/architecture/skill-runtime-adapters.md`](../architecture/skill-runtime-adapters.md);
- skill package contract: [`docs/standards/skill-package-standard.md`](../standards/skill-package-standard.md);
- security and admission: [`docs/security/skill-adoption-security-standard.md`](../security/skill-adoption-security-standard.md);
- evaluation and release evidence: [`docs/testing/skill-evaluation-standard.md`](../testing/skill-evaluation-standard.md);
- sequenced implementation: [`docs/plans/skill-adoption-implementation-backlog.md`](../plans/skill-adoption-implementation-backlog.md).

When this synthesis conflicts with one of those owners, stop and reconcile the conflict rather than applying both.

## Status and Evidence Basis

- **Research date:** 2026-07-26
- **Integration date:** 2026-07-26
- **State:** Research conclusions integrated; prototype evidence remains outstanding
- **Initial target:** ChatGPT used as a chat-based coding agent
- **Future target:** Codex through a separate adapter consuming the same canonical skill and governance records

The synthesis is based on:

1. the complete local Agent Skills source set under [`references/`](../../references/);
2. the research scope in [`chatgpt-skill-adoption-deep-research-brief.md`](chatgpt-skill-adoption-deep-research-brief.md);
3. current repository architecture, security, validation, GitHub, and project decisions;
4. live Agent Skills and OpenAI product documentation verified on 2026-07-26;
5. the project conversation decisions that established a ChatGPT-first, adapter-driven, fail-closed adoption model.

The returned research agent report was not preserved as a standalone tracked repository artifact. This document therefore records the repository-owned conclusions supported by the available source set and live verification; it does not claim to reproduce unavailable report text verbatim.

## Executive Conclusions

1. **Treat skills as governed software supply-chain artifacts, not prompt files.** Admission requires immutable provenance, license review, content integrity, bounded capabilities, validation evidence, approval, and rollback.
2. **Keep one canonical portable skill.** ChatGPT metadata, activation representation, packaging, and capability mappings belong to the ChatGPT adapter. A future Codex adapter must consume the same canonical skill and adoption decision.
3. **Use progressive disclosure as the context architecture.** `name` and `description` carry activation; `SKILL.md` carries only the core workflow and critical gotchas; focused references and resources load only under explicit conditions.
4. **Do not use metadata as authorization.** `allowed-tools` is experimental and cannot enforce filesystem, network, credential, or mutation boundaries. Host and repository controls remain authoritative.
5. **Use the minimum capability tier that fits the workflow.** Tier 2 may declare bounded repository-relative project writes when a general development or documentation workflow requires them; explicit activation and human approval remain required. Higher-risk capabilities remain excluded.
6. **Prove value against a baseline.** A skill is not justified by plausible usefulness. It must improve representative outcomes over no skill or the previous skill version, with objective assertions, human review, and available cost evidence.
7. **Evaluate activation separately from output quality.** A useful skill with a poor description will not load reliably; a precise trigger with weak instructions adds no value. Both gates are required.
8. **Keep evals and governance outside the runtime package.** They govern admission and maintenance but should not consume skill context or enlarge the uploaded attack surface.
9. **Add scripts only when determinism earns the cost.** Scripts are justified for repeated, fragile, or mechanically verifiable work and must be non-interactive, bounded, idempotent, repository-scoped, dependency-controlled, and testable.
10. **Product scanning is supplementary.** ChatGPT upload scanning and workspace controls are useful signals, but they do not replace repository provenance, source review, capability enforcement, abuse testing, or rollback.
11. **Runtime behavior must be verified empirically.** ChatGPT discovery, automatic activation, explicit invocation, multi-skill behavior, context retention, observability, and workspace administration can change. Reverify the target surface before release decisions.
12. **Stop after one credible proof.** Do not grow a skill catalog until one low-risk skill demonstrates measurable value, safe packaging, target compatibility, and reversible operation.

## Requirements and Decision Matrix

| Concern | Source-supported requirement | Repository decision | Authority | Status |
|---|---|---|---|---|
| Portable package | A skill requires `SKILL.md`; scripts, references, and assets are optional | Canonical adopted skills follow the portable format plus a repository adoption manifest | Package standard; security standard | Accepted |
| Activation metadata | `name` and `description` are required and drive discovery/activation | Use intent-based descriptions with explicit adjacent exclusions and trigger evals | Package standard; evaluation standard | Accepted |
| Context use | Load metadata first, instructions on activation, resources on demand | Keep `SKILL.md` lean; every reference must have a load condition | Package standard | Accepted |
| OpenAI metadata | OpenAI implementations may use `agents/openai.yaml` for UI metadata | Keep OpenAI metadata in the ChatGPT adapter or generated package, never as canonical portable authority | Adapter architecture; package standard | Accepted |
| Discovery | Clients choose discovery locations and precedence | Repository runtime discovery is only direct children at `skills/*/SKILL.md`; target installation paths are adapter-owned | Security standard; adapter architecture | Implemented |
| Permissions | Portable metadata cannot guarantee host enforcement | Reject `allowed-tools`; enforce capabilities through repository policy, runtime controls, and explicit approval | Security standard | Implemented |
| Provenance | External sources require owner, revision, license, and integrity evidence | Require `adoption-manifest.json` with immutable revision, hash, capability tier, approval, and rollback | Security standard; schema | Implemented |
| Scripts | Scripts should be reusable, non-interactive, predictable, and dependency-aware | Initial scripts must have no runtime installation or network and must stay within declared repository scopes | Package standard; security standard | Accepted |
| Assets | Assets may contain templates and output resources | Treat assets as untrusted output inputs; scan active content and exclude unnecessary binaries | Package standard; security standard | Accepted |
| Trigger evaluation | Use realistic positive and near-miss negative prompts; repeated runs reduce nondeterminism | Require positive, near-miss, conflict, and prompt-injection cases before model activation | Evaluation standard | Specified, harness pending |
| Output evaluation | Compare with-skill to no-skill or previous version | Require representative baseline runs, objective assertions, evidence, and human review | Evaluation standard | Specified, pilot pending |
| Efficiency | Record token, duration, tool-call, and retry cost when available | Reject skills whose marginal value does not justify context and maintenance cost | Evaluation standard | Specified, measurement pending |
| Abuse resistance | Agentic systems need least privilege, untrusted-input handling, budgets, and recovery | Require traversal, malicious content, egress, cancellation, retry, and active-output abuse cases | Security standard; evaluation standard | Partly implemented |
| Disablement | Safe systems need suspension and rollback | Keep the global kill switch disabled until an admitted skill and target package pass all gates | Security standard | Implemented |
| Multi-target support | Client behavior differs despite a portable package | Use a narrow adapter contract; fail closed on unsupported required capabilities | Adapter architecture | Accepted, ChatGPT adapter pending |

## Repository-Wide Takeaways for Future Work

For any task that creates, modifies, evaluates, packages, installs, enables, suspends, or removes a skill:

1. classify the work as source research, canonical skill, security/admission, evaluation, or runtime-adapter work;
2. read the authoritative owner for that class before the first edit;
3. preserve source evidence separately from repository decisions;
4. keep the canonical skill target-independent and place target behavior behind the adapter boundary;
5. identify the capability tier and enforceable boundary before writing instructions or scripts;
6. define baseline and acceptance evidence before claiming adoption value;
7. keep generated runs and packaging evidence under `.work/`;
8. update only the single authoritative owner for each governed fact;
9. leave the runtime kill switch disabled until the full release gate passes;
10. report residual product limitations explicitly rather than encoding assumptions as policy.

## Required Research Output Status

| Required output | Repository owner | Status |
|---|---|---|
| Executive findings | This synthesis | Complete |
| Portable/OpenAI/security requirements matrix | This synthesis | Complete |
| Skill package standard | [`docs/standards/skill-package-standard.md`](../standards/skill-package-standard.md) | Complete |
| ChatGPT coding-agent architecture | [`docs/architecture/skill-runtime-adapters.md`](../architecture/skill-runtime-adapters.md), with target implementation deferred to the first adapter | Decision complete; implementation pending |
| Security standard | [`docs/security/skill-adoption-security-standard.md`](../security/skill-adoption-security-standard.md) | P0 implemented |
| Evaluation standard | [`docs/testing/skill-evaluation-standard.md`](../testing/skill-evaluation-standard.md) | Complete; harness pending |
| Machine-readable schemas | Adoption manifest schema | P0 complete; eval schemas deferred until consumed by a harness |
| Implementation backlog | [`docs/plans/skill-adoption-implementation-backlog.md`](../plans/skill-adoption-implementation-backlog.md) | Complete |
| Skill prototype evidence | `.work/evals/<skill-name>/` plus accepted summary in `docs/` | `develop-code` and `develop-docs` candidate evidence recorded; target/runtime compatibility remains pending |

## Unresolved Product and Implementation Questions

These remain empirical gates, not assumptions:

- exact ChatGPT packaging requirements for repository-generated skill archives;
- whether `agents/openai.yaml` is consumed identically across ChatGPT, Codex, and API surfaces;
- available activation and resource-loading observability in the target workspace;
- how long-running conversations preserve activated skill instructions during compaction;
- reliable measurement of trigger rate, token use, tool calls, retries, and cancellation in ChatGPT;
- target-specific handling of multiple simultaneously relevant skills;
- workspace-specific permissions, upload scanning outcomes, sharing, and installation behavior;
- enforceable host controls for repository-only reads or writes beyond the repository validator.

Resolve these through the first ChatGPT adapter and prototype tests. Do not broaden permissions or invent portability claims to work around missing product evidence.

## Immediate Decision

The minimum architecture is accepted for implementation with one condition: runtime enablement still requires structural, provenance, trigger, output, efficiency, abuse, human-review, adapter, and rollback evidence. Tier 2 repository-content workflows are admissible when their project-relative write scope is necessary and explicit activation plus human approval are retained.

The next work remains evidence-driven skill adoption and runtime validation. Broader catalog expansion and capabilities beyond the currently approved tiers require separate approval and enforceable controls.

## Source Basis

Primary local sources:

- [`references/agent-skills-specification.md`](../../references/agent-skills-specification.md)
- [`references/skills-best-practice.md`](../../references/skills-best-practice.md)
- [`references/optimising-skill-description.md`](../../references/optimising-skill-description.md)
- [`references/evaluating-skills.md`](../../references/evaluating-skills.md)
- [`references/using-scripts-skills.md`](../../references/using-scripts-skills.md)
- [`references/agents-skills-support.md`](../../references/agents-skills-support.md)
- [`references/skills-knowledge-source-register.md`](../../references/skills-knowledge-source-register.md)

Live sources and freshness rules are registered in [`references/skills-knowledge-source-register.md`](../../references/skills-knowledge-source-register.md). Product facts must be reverified before a target release or policy change.
