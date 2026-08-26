# Specialist Skill Integration

`develop-code` remains the controller. Invoke only canonical skills available in the active runtime and applicable to the classified work.

| Need | Invocation | Return evidence |
|---|---|---|
| Unclear requirements/design | **REQUIRED SUB-SKILL:** Use `brainstorming` | Approved decisions or explicitly open decisions reflected in the spec |
| Explicit implementation plan | **REQUIRED SUB-SKILL:** Use `writing-plans` | Plan in the canonical project location, mapped to requirements |
| Independent read/investigation domains | Use `dispatching-parallel-agents` when isolation is real | Bounded per-domain findings plus integrated verification |
| Same-session task delegation | **REQUIRED SUB-SKILL:** Use `subagent-driven-development` | Per-task implementation, test, and review evidence |
| Inline or separate-session plan execution | **REQUIRED SUB-SKILL:** Use `executing-plans` | Completed task state and specified checks |
| Unknown bug or regression cause | **REQUIRED SUB-SKILL:** Use `systematic-debugging` | Reproduction, root-cause evidence, hypothesis result, verified fix |
| Behavior change | **REQUIRED SUB-SKILL:** Use `test-driven-development` | Observed failing test, minimal fix, passing test, safe refactor |
| Request review checkpoint | Use `requesting-code-review` | Independent findings against requirements and exact change |
| Assess received review feedback | Use `receiving-code-review` | Evidence-backed disposition and verified fixes |
| Completion claim | **REQUIRED SUB-SKILL:** Use `verification-before-completion` | Fresh command output supporting each claim |
| Authorized branch closeout | **REQUIRED SUB-SKILL:** Use `finishing-a-development-branch` | Verified head and repository-authorized integration handoff |

Do not copy a specialist's full process into lifecycle artifacts. Pass it canonical inputs and constraints, let it own its method, then bring its outputs back to the current gate.

## Harmonized upstream responsibilities

All 14 Superpowers 6.2.0 methods remain available as canonical skills, but overlapping authority is narrowed rather than duplicated:

- `using-superpowers` supplies current-skill selection and composition only; `develop-code` remains the code lifecycle controller and repository instructions remain higher authority.
- `using-git-worktrees` supplies isolation detection, workspace selection, and baseline discipline only; KIS and `github-delivery` own governed worktree, Git, and GitHub mutations.
- `writing-skills` supplies behavioral RED-GREEN-REFACTOR and pressure-testing method only; `create-skill`, `evaluate-skill`, and `improve-skill` own skill package and lifecycle decisions.

Remote publication, pull-request mutation, merge authority, deployment, credentials, runtime installation, and deletion never come from these specialist skills. Higher repository authority and live KIS/tool schemas remain controlling.

## Other review specialists

When installed and applicable, use `code-review`, `simpler-code`, `smarter-code`, and the repository's security review capability. If a named specialist is unavailable, record that fact and perform the base Review Contract; do not imitate an unavailable skill or claim its gate passed.
