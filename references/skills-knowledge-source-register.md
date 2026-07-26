# Agent Skills Knowledge Source Register

## Authority

This document is the repository's curated register of external Agent Skills knowledge sources. It identifies where to research specifications, product behavior, implementation patterns, security, provenance, evaluation, and candidate skill artifacts.

It does **not** override [`AGENTS.md`](../AGENTS.md), the Agent Skills specification, product-owner documentation, or repository decisions. External material remains an input until deliberately adopted into this repository.

## Research Snapshot

- **Research date:** 2026-07-26
- **Scope:** Agent Skills based on `SKILL.md`, including authoring, activation, portability, installation, evaluation, security, provenance, and representative catalogs.
- **Selection standard:** Prefer standards bodies, product owners, verified vendor repositories, government or industry security bodies, and primary research.
- **Exclusions:** SEO summaries, copied tutorials, anonymous collections, and registry popularity rankings are not treated as authority.
- **Freshness rule:** Verify live documentation before any adoption decision. Product behavior, supported paths, frontmatter extensions, installation commands, and preview status change frequently.

## Source Priority

Use sources in this order when they conflict:

1. **Repository authority:** applicable `AGENTS.md`, accepted specifications, decisions, and tests in this repository.
2. **Open format authority:** the live Agent Skills specification and its reference validator.
3. **Product authority:** current documentation from the product owner for product-specific behavior.
4. **Owner implementation:** official source repositories, built-in skills, and verified vendor catalogs.
5. **Security and governance standards:** OWASP, NIST, OpenSSF, SLSA, SPDX, and REUSE.
6. **Peer-reviewed or preprint research:** evidence and hypotheses, not normative requirements.
7. **Community catalogs and registries:** discovery leads only; never evidence of quality, safety, ownership, or compatibility.

### Conflict Rules

- The Agent Skills specification governs portable package format.
- OpenAI documentation governs ChatGPT and Codex behavior.
- Vendor extensions are not portable unless independently supported by each target client.
- A repository README does not override a skill's own license or the product owner's current documentation.
- Registry presence, install count, stars, or search rank do not establish trust.
- For security-sensitive adoption, the stricter applicable rule wins.

## Required Baseline Sources

These sources should be consulted for every skill adoption or modification.

| ID | Source | Primary use |
|---|---|---|
| AS-01 | [Agent Skills specification](https://agentskills.io/specification) | Portable structure, frontmatter, resource layout, progressive disclosure, and validation rules. |
| AS-02 | [Agent Skills documentation index](https://agentskills.io/llms.txt) | Discover the complete current documentation set before researching individual pages. |
| AS-03 | [Agent Skills reference repository](https://github.com/agentskills/agentskills) | Specification source, issue history, contribution context, and `skills-ref` validator implementation. |
| AS-04 | [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices) | Scope, context discipline, progressive disclosure, control calibration, gotchas, templates, and validation loops. |
| AS-05 | [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) | Trigger-query design, positive and negative cases, repeated runs, train/validation splits, and description iteration. |
| AS-06 | [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) | With-skill versus baseline evaluation, assertions, grading evidence, timing, token cost, and iteration. |
| OA-01 | [Skills in ChatGPT](https://help.openai.com/en/articles/20001066) | Current ChatGPT availability, creation, installation, sharing, administration, and cross-product behavior. |
| OA-02 | [OpenAI Academy: Using skills](https://openai.com/academy/skills/) | OpenAI's practical guidance for repeatable workflows, inputs, outputs, guardrails, and skill sizing. |
| OA-03 | [OpenAI Skills catalog](https://github.com/openai/skills) | Codex-compatible reference implementations, installation model, per-skill licensing, and official system skills. |
| OA-04 | [OpenAI `skill-creator`](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md) | Current Codex authoring workflow, bundled-resource guidance, UI metadata, initialization, and validation patterns. |
| SEC-01 | [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) | Least privilege, untrusted input handling, human approval, sandboxing, logging, budgets, and adversarial testing. |
| GOV-01 | [SPDX specifications](https://spdx.dev/use/specifications/) | Standard license identifiers and software-component metadata. |

## Local Reference Snapshots

The repository currently contains local snapshots of core Agent Skills guidance:

- [`agent-skills-specification.md`](agent-skills-specification.md)
- [`optimising-skill-description.md`](optimising-skill-description.md)
- [`evaluating-skills.md`](evaluating-skills.md)
- [`agents-skills-support.md`](agents-skills-support.md)
- [`using-scripts-skills.md`](using-scripts-skills.md)
- [`skills-best-practice.md`](skills-best-practice.md)

Treat these as convenient research snapshots, not live authority. Before changing repository policy or adopting a skill, compare the relevant snapshot with the current source at `agentskills.io`.

## Full Source Register

### 1. Open Format and Authoring Guidance

| ID | Source | Owner | What it contributes | Use and caveats |
|---|---|---|---|---|
| AS-01 | [Specification](https://agentskills.io/specification) | Agent Skills project | Required directory and `SKILL.md` structure; required and optional frontmatter; progressive disclosure; resource conventions. | Normative starting point for portable skills. Experimental fields may have uneven client support. |
| AS-02 | [Documentation index](https://agentskills.io/llms.txt) | Agent Skills project | Machine-readable index of all current documentation pages. | Use before broad research to avoid relying on stale or incomplete navigation. |
| AS-03 | [Specification and documentation repository](https://github.com/agentskills/agentskills) | Agent Skills project | Source history, issues, discussions, licenses, and validation library. | Use repository history to understand changes; do not treat open proposals as adopted specification. |
| AS-04 | [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices) | Agent Skills project | Domain grounding, coherent scope, context efficiency, defaults, procedures, gotchas, templates, checklists, and validation loops. | Primary authoring guidance. Apply through repository-specific tests rather than copying examples verbatim. |
| AS-05 | [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) | Agent Skills project | Trigger eval design and iterative description optimization. | Use near-miss negatives and held-out validation to avoid over-broad triggers and overfitting. |
| AS-06 | [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) | Agent Skills project | Test cases, baselines, assertions, evidence-based grading, benchmark aggregation, human review, and iteration. | Required basis for demonstrating value beyond the unskilled baseline. |
| AS-07 | [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts) | Agent Skills project | Version-pinned commands, self-contained scripts, non-interactive interfaces, structured output, idempotency, dry runs, and bounded output. | Apply when a skill needs deterministic or repeatedly reused logic. |
| AS-08 | [How to add skills support to an agent](https://agentskills.io/client-implementation/adding-skills-support) | Agent Skills project | Discovery, parsing, catalogs, activation, resource loading, precedence, trust, compaction, and deduplication. | Architecture reference for clients and compatibility analysis. Product implementations may deliberately differ. |
| AS-09 | [`skills-ref` validator](https://github.com/agentskills/agentskills/tree/main/skills-ref) | Agent Skills project | Reference validation for frontmatter and naming conventions. | Run against portable skills; supplement with repository-specific semantic, security, and execution checks. |

### 2. OpenAI and ChatGPT Sources

| ID | Source | Owner | What it contributes | Use and caveats |
|---|---|---|---|---|
| OA-01 | [Skills in ChatGPT](https://help.openai.com/en/articles/20001066) | OpenAI | Current product availability, user workflows, skill creation and installation, sharing, workspace permissions, and portability claims. | Highest authority for ChatGPT-specific behavior. Recheck frequently because rollout and administration details change. |
| OA-02 | [OpenAI Academy: Using skills](https://openai.com/academy/skills/) | OpenAI | Practical skill selection, workflow decomposition, inputs, outputs, guardrails, final checks, and comparison with GPTs and Projects. | Best OpenAI source for non-code workflow design. It is guidance, not a file-format specification. |
| OA-03 | [OpenAI Skills catalog](https://github.com/openai/skills) | OpenAI | Official Codex catalog, curated and experimental groupings, installation workflow, and per-skill licenses. | Preferred source of Codex examples. Inspect the exact skill directory and license before reuse. |
| OA-04 | [OpenAI `skill-creator`](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md) | OpenAI | Codex's current skill authoring procedure, `agents/openai.yaml`, resource selection, initialization, and validation. | Primary implementation reference for this repository's ChatGPT/Codex adaptation work. OpenAI-specific metadata is not automatically portable. |
| OA-05 | [OpenAI `skill-installer`](https://github.com/openai/skills/blob/main/skills/.system/skill-installer/SKILL.md) | OpenAI | Codex installation behavior for curated and external GitHub skills, destination paths, authentication fallbacks, and update assumptions. | Installation reference only. A successful install does not establish trust or compatibility. |
| OA-06 | [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/) | OpenAI | Product-level examples of using skills for tools, documents, deployment, research, and long-running workflows. | Useful for adoption goals and representative use cases; not a technical specification. |
| OA-07 | [Plugins in Codex](https://help.openai.com/en/articles/20001256-plugins-in-codex/) | OpenAI | Relationship between skills, apps, app templates, workspace enablement, and underlying permissions. | Use when an adopted skill depends on connectors or external actions. A plugin does not itself grant data access. |
| OA-08 | [OpenAI Evals API](https://platform.openai.com/docs/api-reference/evals) | OpenAI | Structured evaluation objects, data sources, runs, and repeatable model comparisons. | Relevant when repository evaluation grows beyond local scripts. Product API usage is optional. |
| OA-09 | [OpenAI Graders API](https://platform.openai.com/docs/api-reference/graders) | OpenAI | String, similarity, and model-based grading primitives. | Use only where grader reliability is understood; retain deterministic checks for mechanical assertions. |

### 3. Anthropic Sources

| ID | Source | Owner | What it contributes | Use and caveats |
|---|---|---|---|---|
| AN-01 | [Extend Claude with skills](https://code.claude.com/docs/en/skills) | Anthropic | Claude Code discovery paths, invocation controls, product extensions, and open-standard alignment. | Product authority for Claude Code, not ChatGPT. Useful for portability analysis. |
| AN-02 | [Agent Skills in the Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/skills) | Anthropic | Programmatic SDK loading and configuration patterns. | Use when comparing hosted or SDK-based skill activation. |
| AN-03 | [Anthropic Skills repository](https://github.com/anthropics/skills) | Anthropic | Official examples, templates, production document skills, specification material, and partner skills. | Strong pattern source. Check each directory's license; some document skills are source-available rather than open source. |
| AN-04 | [Anthropic official `skill-creator`](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md) | Anthropic | Current Anthropic evaluation-driven skill creation workflow. | Useful comparison with OpenAI's creator. Claude-specific frontmatter and packaging behavior may not transfer. |

### 4. Client Implementations and Interoperability

These sources are useful for identifying portability boundaries. They do not redefine the Agent Skills specification.

| ID | Source | Owner | What it contributes | Use and caveats |
|---|---|---|---|---|
| GH-01 | [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | GitHub | Supported Copilot surfaces, discovery, automatic loading, and `gh skill` integration. | Product authority for GitHub Copilot. |
| GH-02 | [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) | GitHub | Personal and project installation paths, creation workflow, and frontmatter behavior. | Use for Copilot CLI compatibility tests. |
| GH-03 | [Manage agent skills with GitHub CLI](https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/) | GitHub | `gh skill` discovery, installation, pinning by tag or commit, preview, update, publish, and provenance metadata. | Public-preview behavior can change. GitHub explicitly warns that discovered skills are not verified. |
| VS-01 | [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills) | Microsoft | VS Code paths, settings, creation UI, and Agent Skills behavior. | Product authority for VS Code. Verify version-specific settings. |
| GG-01 | [Agent Skills in Gemini CLI](https://geminicli.com/docs/cli/skills/) | Google | Discovery, activation, trust boundaries, management commands, and resource access. | Product authority for Gemini CLI. Useful for cross-client activation tests. |
| GG-02 | [Gemini CLI skills getting started](https://geminicli.com/docs/cli/tutorials/skills-getting-started/) | Google | Troubleshooting discovery, exact file placement, trust, and frontmatter requirements. | Use for practical compatibility diagnostics. |
| JB-01 | [Skills in JetBrains AI Assistant](https://www.jetbrains.com/help/ai-assistant/agent-skills.html) | JetBrains | Import from Codex or Claude, IDE and project scopes, installation locations, and supported agents. | Product behavior may depend on IDE and plugin version. |
| MS-01 | [Agent Skills in Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/agents/skills) | Microsoft | File, inline, class, and MCP sources; provider architecture; progressive loading; resource and script tools. | Strong implementation reference for building skill-capable agents. Framework-specific APIs are not portable skill metadata. |
| ROO-01 | [Skills in Roo Code](https://roocodeinc.github.io/Roo-Code/features/skills/) | Roo Code | Cross-agent `.agents/skills` paths, precedence, mode-specific extensions, and loading behavior. | Official product documentation but lower project relevance than OpenAI, GitHub, Google, or Microsoft sources. |

### 5. Official and Curated Skill Catalogs

Catalogs provide candidate artifacts and design examples. Prefer owner-authored skills for the owner's own products.

| ID | Catalog | Owner | Value | Trust treatment |
|---|---|---|---|---|
| CAT-01 | [OpenAI Skills](https://github.com/openai/skills) | OpenAI | Codex system, curated, and experimental skills. | High-value source for Codex patterns; review per-skill license and status. |
| CAT-02 | [Anthropic Skills](https://github.com/anthropics/skills) | Anthropic | Broad examples and production document skills. | High-value source; mixed licensing requires directory-level review. |
| CAT-03 | [Awesome GitHub Copilot](https://github.com/github/awesome-copilot) | GitHub | Community-contributed skills, agents, instructions, plugins, and learning material curated under GitHub's organization. | Discovery and examples, not automatic trust. Review contributor, history, license, scripts, and external references. |
| CAT-04 | [Google Skills](https://github.com/google/skills) | Google | Skills for Google products and technologies, including Google Cloud. | Prefer for Google product workflows; inspect the exact source and compatibility. |
| CAT-05 | [Gemini Skills](https://github.com/google-gemini/gemini-skills) | Google | Skills for Gemini API, SDK, and model or agent interactions. | Prefer for Gemini-specific work. Validate Codex compatibility before adoption. |
| CAT-06 | [Microsoft Skills](https://github.com/microsoft/skills) | Microsoft | Skills, MCP servers, custom agents, and instructions for Microsoft SDKs and products. | Prefer for Microsoft product workflows. Separate skill artifacts from other customization types. |
| CAT-07 | [MicrosoftDocs Agent Skills](https://github.com/MicrosoftDocs/Agent-Skills) | Microsoft | Curated skills grounded in Microsoft Learn documentation. | Good source for documentation-grounded patterns; verify synchronization and license. |
| CAT-08 | [NVIDIA Skills](https://github.com/NVIDIA/skills) | NVIDIA | Official, NVIDIA-verified product skills with catalog and provenance practices. | Strong example of vendor-owned verification and release governance. |
| CAT-09 | [Cloudflare Skills](https://github.com/cloudflare/skills) | Cloudflare | Skills for Cloudflare Workers, Agents SDK, and platform workflows. | Prefer for Cloudflare tasks; inspect scripts and current platform requirements. |
| CAT-10 | [Elastic Agent Skills](https://github.com/elastic/agent-skills) | Elastic | Official Elastic product skills. | Prefer for Elastic tasks; confirm client support and installation method. |

### 6. Security, Provenance, and Licensing

| ID | Source | Owner | What it contributes | Repository use |
|---|---|---|---|---|
| SEC-01 | [AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) | OWASP | Least privilege, authorization, input validation, sandboxing, human approval, logging, schema validation, memory isolation, budgets, and red teaming. | Baseline security checklist for any skill that reads untrusted content, runs scripts, or invokes tools. |
| SEC-02 | [OWASP Agentic Security Initiative](https://genai.owasp.org/initiatives/agentic-security-initiative/) | OWASP | Agentic threat models, Top 10 risks, governance resources, and secure MCP guidance. | Use for broader threat modeling and periodic security-policy refresh. |
| SEC-03 | [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) | OWASP | Goal hijacking, tool misuse, identity and privilege abuse, memory poisoning, cascading failures, and related agentic risks. | Map adopted skill capabilities and mitigations to relevant risk categories. |
| SEC-04 | [NIST AI RMF Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | NIST | Lifecycle risk management, governance, measurement, and management actions for generative AI. | Use for repository-level governance and risk records, especially for high-impact skills. |
| SEC-05 | [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) | NVIDIA | Open-source scanner focused on malicious patterns and security risks in Agent Skills. | Candidate supplementary scanner. Validate its detection scope and false-positive behavior before making it a gate. |
| SEC-06 | [NVIDIA verified-skill documentation](https://docs.nvidia.com/skills) | NVIDIA | Skill cards, scanning, signing, release gates, and integrity verification. | Reference architecture for mature skill supply-chain governance. NVIDIA-specific mechanisms are not universal standards. |
| GOV-01 | [SPDX specifications](https://spdx.dev/use/specifications/) | SPDX / Linux Foundation | Standard component and license metadata; SPDX is ISO/IEC 5962:2021. | Record licenses using standard identifiers and expressions where possible. |
| GOV-02 | [SPDX license handling](https://spdx.dev/learn/handling-license-info/) | SPDX / Linux Foundation | Canonical short identifiers, license text, and URLs. | Normalize source and adopted-artifact license records. |
| GOV-03 | [REUSE tutorial](https://reuse.software/tutorial/) | Free Software Foundation Europe | Practical file-level copyright and license annotation. | Candidate approach when copied or adapted sources have mixed licenses. |
| GOV-04 | [SLSA specification](https://slsa.dev/spec/v1.2/) | OpenSSF / SLSA project | Source and build provenance, attestation, verification, and integrity levels. | Use as a conceptual model for recording exact source revisions and verifying generated packages. |
| GOV-05 | [OpenSSF Scorecard](https://openssf.org/projects/scorecard/) | OpenSSF | Automated source-repository security posture checks. | Supporting signal when assessing external repositories; never a substitute for reviewing the skill itself. |
| GOV-06 | [GitHub dependency review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review) | GitHub | Dependency changes, vulnerabilities, licenses, and enforcement in pull requests. | Apply when adopted skills add package manifests or lock files. |

### 7. Evaluation and Emerging Research

Research sources are useful for hypotheses, metrics, and threat awareness. The 2026 papers below are recent preprints unless publication status is independently verified.

| ID | Source | Focus | Repository use |
|---|---|---|---|
| RES-01 | [From Registry to Repository: How AI Agent Skills Are Written, Adapted, and Maintained](https://arxiv.org/abs/2607.00911) | Empirical study of public and personal skill reuse, customization, and maintenance. | Supports treating skills as maintained software artifacts rather than one-time prompt files. Do not convert findings directly into policy without replication or review. |
| RES-02 | [Under the Hood of SKILL.md: Semantic Supply-chain Attacks on AI Agent Skill Registry](https://arxiv.org/abs/2605.11418) | Discovery, selection, and governance manipulation through skill metadata and instructions. | Supports strict registry distrust, description review, retrieval grounding, and independent provenance checks. |
| RES-03 | [From Anatomy to Smells: An Empirical Study of SKILL.md in Agent Skills](https://arxiv.org/abs/2607.01456) | Taxonomy of skill content and proposed skill smells. | Candidate source for future lint rules; validate the detector and definitions before adoption. |
| RES-04 | [A Framework for Evaluating Agentic Skills at Scale](https://arxiv.org/abs/2606.17819) | Cross-model, task-based evaluation of skill utility and instruction adherence. | Supports testing across model and harness configurations rather than assuming a skill's value is universal. |
| RES-05 | [Agent Skill Evaluation and Evolution: Frameworks and Benchmarks](https://arxiv.org/abs/2606.11435) | Survey of evaluation, trajectory distillation, compression, reinforcement learning, and benchmark gaps. | Use for research planning and metric selection, not as normative procedure. |
| RES-06 | [Skills That Don't Exist: A Large-Scale Study of Hallucinated Skill Recommendation in LLM Agents](https://arxiv.org/abs/2607.12340) | Hallucinated skill names and registry-squatting risk. | Requires exact-source verification; never install a skill solely because an agent recommended a plausible name. |
| RES-07 | [SkillCorpus: Consolidating and Evaluating the Open Skill Ecosystem](https://arxiv.org/abs/2607.15557) | Large-scale aggregation, filtering, matching, and evaluation of community skills. | Evidence that curation and retrieval quality matter; results remain research evidence, not a trusted catalog. |

### 8. Discovery Tools and Registries

| ID | Source | Owner | Appropriate use | Restrictions |
|---|---|---|---|---|
| DISC-01 | [GitHub CLI `gh skill`](https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/) | GitHub | Discover, preview, install, pin, publish, and update skills from GitHub repositories. | Preview every skill, pin an immutable revision, and independently review it. GitHub states that skills are not verified. |
| DISC-02 | [Skills.sh directory](https://www.skills.sh/) | Vercel ecosystem | Broad discovery of public skills and ecosystem trends. | Search index only. Popularity and presence do not establish owner identity, safety, license, or quality. |
| DISC-03 | [`npx skills` tooling](https://github.com/vercel-labs/skills) | Vercel Labs | Install and manage skills across multiple supported clients. | Tool convenience does not replace provenance, security, license, or compatibility review. Pin versions and inspect network and filesystem effects. |
| DISC-04 | [Awesome GitHub Copilot skills directory](https://awesome-copilot.github.com/skills/) | GitHub community project | Browsable discovery of Copilot-oriented skills. | Treat individual contributions as third-party artifacts unless their owner and source are independently verified. |

## Decision Lookup

| Decision | First sources to consult | Required follow-through |
|---|---|---|
| Is the skill structurally valid? | AS-01, AS-09 | Run the reference validator and repository checks. |
| Will ChatGPT or Codex use it as intended? | OA-01, OA-03, OA-04 | Test in the actual target surface; do not infer from Claude or Copilot behavior. |
| Is the description likely to trigger correctly? | AS-05 | Build realistic positive and near-miss negative queries, repeat runs, and retain a held-out set. |
| Does the skill improve outcomes? | AS-06, OA-08, OA-09 | Compare against no-skill or prior-skill baselines and record quality, time, and token deltas. |
| Is it portable? | AS-01, AS-08, then target-client docs | Identify vendor extensions and run the same evals in each supported client. |
| Are scripts appropriate? | AS-07 | Require non-interactive interfaces, pinned dependencies, safe defaults, structured output, and deterministic tests. |
| Is an external skill safe to inspect or adopt? | SEC-01 through SEC-06 | Review instructions, scripts, references, assets, external downloads, permissions, secrets, and destructive actions. Use a sandbox for execution. |
| Is provenance adequate? | DISC-01, GOV-04, GOV-05 | Record owner, canonical URL, immutable commit or tag, retrieval date, hashes where practical, and repository security signals. |
| Can content legally be reused? | Skill license, GOV-01 through GOV-03 | Review every relevant directory and file; preserve notices and record modifications. Absence of a license means no reuse permission should be assumed. |
| Is a registry result trustworthy? | None by default | Resolve to the canonical owner repository and repeat the full provenance, license, security, and compatibility review. |

## Minimum Adoption Record

Every externally sourced skill considered for adoption should record at least:

```yaml
source:
  owner: "<verified owner or organization>"
  canonical_url: "<repository or product-owner URL>"
  skill_path: "<path within source repository>"
  source_ref: "<immutable commit SHA or signed release tag>"
  retrieved_at: "YYYY-MM-DD"
  content_hash: "<hash when practical>"
  license: "<SPDX expression or exact source statement>"
  notices: []

assessment:
  target_products: []
  portable_spec_version: "<version or retrieval date>"
  vendor_extensions: []
  external_dependencies: []
  required_tools: []
  required_permissions: []
  network_access: []
  secrets_or_credentials: []
  destructive_capabilities: []
  untrusted_input_paths: []

validation:
  structural_checks: []
  trigger_evals: []
  output_evals: []
  security_review: []
  license_review: []
  compatibility_tests: []

adoption:
  decision: "adopt | adapt | defer | reject"
  local_changes: []
  rationale: "<evidence-based decision>"
  reviewer: "<reviewer>"
  reviewed_at: "YYYY-MM-DD"
```

## External Skill Review Gates

A candidate should not become repository-owned until all applicable gates pass:

1. **Identity:** Resolve the canonical owner and repository. Reject ambiguous mirrors or names that exist only in agent output.
2. **Revision:** Select an immutable commit or signed release, not an unpinned branch tip.
3. **License:** Confirm permission for every copied or adapted file and preserve required notices.
4. **Content:** Review `SKILL.md`, scripts, references, assets, hidden files, symlinks, generated files, and external download instructions.
5. **Permissions:** Enumerate filesystem, shell, network, connector, secret, and write capabilities; reduce them to least privilege.
6. **Execution:** Run scripts only in a bounded sandbox with disposable inputs and no production credentials.
7. **Structure:** Validate against the Agent Skills specification and repository rules.
8. **Triggering:** Test positive, near-miss negative, and conflict cases against adjacent skills.
9. **Utility:** Demonstrate measurable benefit over the baseline or previous version.
10. **Portability:** Test every claimed target client and document product-specific deviations.
11. **Maintenance:** Assign ownership, update cadence, upstream monitoring, and a removal path.
12. **Diff review:** Record exactly what was copied, rewritten, removed, or added.

## Refresh Policy

- **Before every adoption:** Verify the live specification, target-product documentation, exact source revision, license, and security posture.
- **Monthly while the project is actively adopting skills:** Review OpenAI Skills, ChatGPT Skills documentation, OpenAI `skill-creator`, Agent Skills specification changes, and high-impact security advisories.
- **Quarterly:** Recheck all baseline sources, supported client behavior, OWASP guidance, and the repository's adopted-source records.
- **On product or agent upgrade:** Rerun structural, trigger, output, and compatibility evals for affected skills.
- **On upstream change:** Compare against the pinned source, assess relevance, and adopt changes deliberately rather than auto-syncing.
- **On new research:** Treat findings as hypotheses until methods, data, and applicability have been reviewed.

## Research Gaps

The current ecosystem still lacks a universally adopted standard for:

- immutable package identity and dependency resolution;
- cryptographic signing and verification across clients;
- capability and permission manifests with enforceable semantics;
- portable vendor-extension negotiation;
- registry publisher verification and namespace protection;
- standardized trigger and output benchmark formats;
- compatibility claims across model, client, operating system, and tool versions;
- safe update and rollback behavior;
- lifecycle metadata such as deprecation, ownership transfer, and end-of-support.

Until these gaps close, this repository should treat skill adoption as a controlled software supply-chain process, not as prompt-file copying.
