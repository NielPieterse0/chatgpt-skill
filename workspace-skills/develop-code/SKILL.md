---
name: develop-code
description: 'Use when creating, changing, fixing, refactoring, or completing production code and specialist development methods such as brainstorming, planning, TDD, debugging, review, or completion verification may improve the work. In KIS-managed repositories, KIS remains the workflow and execution authority; this skill only selects and composes specialist methods. Not for read-only explanation, standalone review with no requested changes, or pure research.'
---

# Develop Code

Use the repository's current development workflow. Add specialist methods where they improve reasoning, implementation quality, testing, review, or verification.

This skill is not a second workflow engine. It does not redefine KIS lifecycle state, classification, change structure, worktree policy, Git/GitHub operations, verification gates, or closeout rules.

## Authority

1. Follow explicit user instructions, repository instructions, and authoritative project documentation.
2. If the repository is KIS-managed, load `kis-mcp` and use KIS discovery/current state before deciding how to proceed.
3. Treat live KIS workflow, classification, change/workspace structure, and capability schemas as authoritative. Do not reproduce or freeze those details here.
4. Use the current KIS terms and locations, including the active `.work` change/slice structure when KIS defines one. Do not invent a parallel `superpowers`, slug, spec, or plan tree.
5. Specialist skills provide methods only. They do not grant mutation, lifecycle-transition, Git/GitHub, deployment, or completion authority.

If KIS is unavailable or the repository does not use it, follow the repository's native workflow and use the standalone guidance in this skill.
## Select Specialist Methods

Load [Specialist integration](./references/superpowers-integration.md) and select only methods relevant to the current phase and risk. When the task needs deeper engineering-domain analysis, load [Engineering specialist routing](./references/engineering-specialists.md) and then only the relevant specialist skill.

- Requirements, architecture, or trade-offs need thinking before commitment: use `brainstorming`.
- Unfamiliar code, architecture, backend/API design, evidence engineering, test strategy, performance, deep review, or AppSec needs specialist depth: select the narrowest role from `engineering-specialists.md` rather than expanding this router.
- A non-trivial implementation needs an explicit executable plan: use `writing-plans`.
- A behavior change needs implementation: use `test-driven-development` unless the governing workflow records an exception.
- A defect has an unknown cause: use `systematic-debugging` before proposing fixes.
- Independent investigation or implementation domains can be isolated safely: consider `dispatching-parallel-agents` or `subagent-driven-development`.
- An approved plan needs execution support: consider `executing-plans`.
- A review checkpoint is reached: use `requesting-code-review`; use `receiving-code-review` when acting on review feedback.
- A completion claim is approaching: use `verification-before-completion` to strengthen evidence, without replacing the repository/KIS completion gate.
- Branch closeout is already authorized by the governing workflow: `finishing-a-development-branch` may supply method guidance.

Complexity should increase specialist rigor, not create a competing classification model. In KIS-managed work, read the current KIS classification and scale specialist use accordingly. For complex, high-risk, uncertain, or cross-boundary work, default toward explicit brainstorming, planning, test strategy, review, and verification unless current KIS/repository guidance says otherwise.

Do not reproduce a specialist skill from memory. Invoke the available skill, pass it the current authoritative constraints and artifacts, use its method, then return control to the governing repository/KIS workflow.
## Standalone Mode

When KIS is not the repository authority:

1. Read repository instructions and discover the existing test, build, lint, security, release, documentation, and Git conventions.
2. Define the requested outcome, boundaries, exclusions, unknowns, acceptance evidence, and recovery needs.
3. Use [Standalone scaling](./references/classification.md) only to decide how much specification, planning, review, and verification is warranted.
4. Prefer existing project artifact locations. If none exist and durable artifacts are useful, use [Standalone artifact guidance](./references/artifact-contracts.md).
5. Keep requirements, implementation tasks, tests/evidence, and review findings traceable for non-trivial work.
6. Reassess scope and risk when discovery changes the problem.

The standalone fallback is intentionally lightweight. It must not claim to emulate KIS or copy KIS-specific classifications, transitions, capability schemas, or change-management rules.

## Review and Completion

Specialist review supplements the governing workflow. Check requirements, correctness, edge cases, failure handling, security/privacy where applicable, test relevance, maintainability, unnecessary complexity, scope discipline, evidence freshness, and rollback/recovery.

Fix blocking findings and rerun affected checks. Any implementation edit invalidates affected review or verification evidence.

Close only through the repository's governing workflow. Report implemented scope, specialist methods used, review findings, verification evidence, skipped checks, recovery/rollback, residual risks, and optional follow-ups. Never describe unverified behavior as complete.