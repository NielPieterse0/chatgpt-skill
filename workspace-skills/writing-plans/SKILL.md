---
name: writing-plans
description: Use when approved requirements or a design must be converted into a multi-step implementation plan before code changes begin.
license: MIT
---

# Writing Implementation Plans

Produce a plan another engineer or isolated agent can execute without reconstructing hidden context.

## Scope check

Read the approved requirements/design, repository authority, and relevant current code before planning. If material design decisions are still unresolved, return to `brainstorming`; do not hide design guesses inside implementation tasks.

## Plan contract

Start with the outcome, source requirements/specification, constraints, exclusions, verification expectations, and repository-authorized artifact location.

For each task, state:

- one coherent outcome;
- exact files, components, or interfaces when they are known;
- required behavior and acceptance conditions;
- test or verification steps that prove the task;
- dependencies on earlier tasks;
- documentation, migration, rollback, or cleanup obligations consumed by that task.

Use concrete paths, names, signatures, and commands only when repository evidence supports them. Do not use placeholders for facts that are already knowable from the repository.## Task sizing and order

Keep tasks small enough to verify and review independently, but do not split setup, tests, or documentation into artificial chores when they only make sense with the behavior they support.

Order tasks by dependency and risk. Mark genuinely independent work explicitly so an execution workflow can parallelize it safely when allowed.

## Global constraints

Record cross-cutting constraints once when every task must honor them: repository authority, scope limits, compatibility, security boundaries, style rules, or required specialist gates. Do not duplicate them into every task.

## Self-review

Before handoff, compare the complete plan with the source requirements and ask:

- Is every requirement mapped to work or explicitly out of scope?
- Did the plan introduce features the design never approved?
- Are names, paths, and interfaces consistent across tasks?
- Can each task be verified independently at the point it completes?
- Does task ordering respect real dependencies?
- Are unresolved decisions visible rather than silently invented?

## Execution handoff

Store the plan only in the repository-authorized location. Hand it to `executing-plans` or `subagent-driven-development` according to the chosen execution model. In KIS-managed repositories, KIS and repository instructions remain authoritative for Work state, isolation, mutation, review, verification, and delivery.