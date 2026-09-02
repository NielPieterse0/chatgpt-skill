# Specialist Skill Integration

Repository instructions and, when present, KIS remain the workflow authority. `develop-code` selects specialist methods that add reasoning or engineering depth the governing workflow does not itself prescribe.

| Need | Specialist method | Contribution |
|---|---|---|
| Requirements/design need exploration | `brainstorming` | Clarified decisions, trade-offs, and open questions |
| Implementation needs a durable plan | `writing-plans` | Executable tasks mapped to current requirements |
| Independent read/investigation domains | `dispatching-parallel-agents` | Bounded parallel findings with integrated verification |
| Independently reviewable implementation tasks | `subagent-driven-development` | Per-task implementation, tests, and review evidence |
| Approved plan needs execution support | `executing-plans` | Plan execution with checkpoints |
| Unknown defect/regression cause | `systematic-debugging` | Reproduction, root-cause evidence, hypothesis tests, verified fix |
| Behavior change | `test-driven-development` | Failing test, minimal implementation, passing test, safe refactor |
| Request a review | `requesting-code-review` | Independent findings against current requirements and change |
| Process review feedback | `receiving-code-review` | Evidence-backed disposition and verified corrections |
| Completion evidence | `verification-before-completion` | Fresh evidence supporting completion claims |
| Authorized branch closeout | `finishing-a-development-branch` | Method guidance for an already authorized integration path |

Use complexity only to scale rigor. In KIS-managed work, consume the current KIS classification rather than translating it into a local taxonomy. Complex or high-risk work generally benefits from more explicit brainstorming, planning, testing, review, and verification.

## Boundaries

- `using-superpowers` may help discover and compose available specialist skills; it does not replace repository or KIS workflow authority.
- `using-git-worktrees` may contribute isolation guidance only when the governing workflow permits it. KIS or repository-native rules own actual workspace/Git decisions.
- `writing-skills` applies to skill-authoring method; repository skill lifecycle and admission remain owned elsewhere.
- Other focused skills such as `code-review`, `simpler-code`, or `smarter-code` may add specialist evidence when applicable.

Do not copy a specialist's full process into this skill. Invoke the current specialist, pass it authoritative repository/KIS context, use its method, and return its result to the governing workflow.

If a specialist is unavailable, continue using the governing workflow and base engineering judgment unless that workflow explicitly requires the specialist. Record the gap rather than imitating an unavailable skill.
