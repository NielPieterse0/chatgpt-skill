---
name: brainstorming
description: Use when a requested code, product, or workflow change still needs design, requirements clarification, trade-off analysis, or explicit agreement before implementation.
license: MIT
---

# Brainstorming Ideas Into Designs

Turn an idea into an agreed design before implementation. Preserve the upstream design-first discipline, but let repository authority define required artifacts, approvals, and delivery workflow.

## Scope

Use this skill when the shape of the solution is not yet agreed. Do not use it to reopen an already-approved design merely because implementation is difficult.

Classify the design need:

- **Spike:** answer a feasibility question; do not retain exploratory implementation as the solution.
- **Bounded change:** clarify behavior and interfaces with a compact design.
- **Architectural change:** compare viable approaches and record a durable design before planning.

## Workflow

1. Read repository authority and inspect the current system before proposing changes.
2. Identify the user outcome, constraints, non-goals, existing behavior, and decisions that are genuinely unresolved.
3. Ask only questions that can materially change the design. When interaction is required, prefer one focused question at a time.
4. For meaningful trade-offs, present 2-3 viable approaches, recommend one, and explain consequences rather than listing options without a decision.5. Present the proposed design at the depth the change requires: behavior, boundaries, data flow, interfaces, failure handling, security implications, migration or rollback where relevant, and verification strategy.
6. Obtain the approval required by the repository or user before implementation. Do not treat silence or continued discussion as approval.
7. For durable design work, store the approved result only in the repository-authorized specification location, then self-review it for contradictions, missing decisions, and invented assumptions.
8. Hand the approved design to `writing-plans` or the repository's planning controller.

## Guardrails

- "This is too simple for design" is not a reason to skip the gate; scale the design instead.
- Do not start production implementation while the design is still materially undecided.
- Do not smuggle design changes into a plan or implementation task. Return to this gate when a new architectural decision appears.
- Do not invent visual companions, browser services, telemetry, remote assets, or host-specific tools from the source bundle.
- In KIS-managed repositories, KIS and repository instructions own Work state, governed change identity, and mutation workflows. This skill supplies design method only.

## Completion

Brainstorming is complete when the intended outcome, boundaries, chosen approach, meaningful trade-offs, unresolved decisions, and required approval are explicit enough for planning without reconstructing hidden context.