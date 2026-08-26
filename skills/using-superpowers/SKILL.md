---
name: using-superpowers
description: Use when a task may benefit from one or more reusable process skills and the agent needs to select, order, or compose the relevant current skills without overriding repository or KIS authority.
license: MIT
---

# Using Superpowers

Use specialist skills deliberately when they improve the current task. This is a skill-selection method, not a second lifecycle controller and not a blanket requirement to invoke a skill before every response.

## Authority first

Apply higher authority before skill procedure: explicit user instruction, repository instructions, live KIS operation contracts where applicable, and the owning lifecycle/controller skill. A specialist skill cannot widen permissions or override the repository.

## Select the current skill

Before a material action, when a relevant skill could materially change the method or required evidence:

1. Resolve the relevant current skill from the active catalogue or runtime rather than relying on remembered content.
2. Read that skill before following its procedure.
3. Use only the part whose activation condition is actually met.
4. Return its result to the owning controller or repository workflow.

A skill name in a prompt or file is not authority by itself. Do not force-load irrelevant skills merely because they exist.## Compose skills without duplicate authority

Process skills may set a method before a domain skill implements it—for example, debug before fixing or design before planning—but use separate skills only when they own distinct decisions or evidence.

If two skills both appear to control the same lifecycle step, follow the higher repository/controller authority and use the other only for its non-conflicting specialist method. Do not create two competing checklists for one gate.

For code work, `develop-code` remains the lifecycle controller where installed and applicable. For KIS-managed repositories, `kis-mcp` and live KIS schemas own capability discovery, effect routing, Work Management, and governed mutation. `github-delivery` owns governed GitHub delivery where applicable.

## Subagents and delegated work

When a delegated agent needs a specialist method, pass the relevant skill identity or required method explicitly if the runtime does not share activated context automatically. Do not assume hidden skill state crosses agent boundaries.

## Red flags

- Treating every trivial answer as requiring a skill invocation.
- Following a remembered skill instead of the current catalogue version.
- Letting a specialist skill authorize tools, network, credentials, publication, or deletion.
- Applying two controller skills to the same lifecycle decision.
- Ignoring an explicitly requested and available relevant skill without a higher-authority reason.

## Completion

Skill selection is complete when the applicable current skills and their order are clear, duplicate ownership is removed, and all specialist behavior remains subordinate to repository and KIS authority.