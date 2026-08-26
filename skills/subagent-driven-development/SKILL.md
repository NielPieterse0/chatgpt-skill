---
name: subagent-driven-development
description: Use when an implementation plan contains independently reviewable tasks that can be delegated to fresh isolated agents within the current execution session.
license: MIT
---

# Subagent-Driven Development

Execute a plan with fresh task context, explicit review gates, and one coordinating source of truth. Preserve the upstream implementer/reviewer loop without assuming a particular model tier, helper script, or plugin harness.

## Preconditions

Use this method only when:

- an approved plan exists;
- tasks have clear boundaries and dependencies;
- the runtime actually supports isolated agent delegation;
- the coordinator can inspect returned evidence and the integrated repository state.

For independent read-only investigations, prefer `dispatching-parallel-agents` instead.

## Task loop

1. Read the plan and repository authority. Identify the first incomplete task and its dependencies.
2. Dispatch one implementer with the complete task text, relevant interfaces, constraints, expected tests, and permitted scope. Do not make the implementer rediscover the plan.
3. Require the implementer to report changed artifacts, tests run, failures, assumptions, and any deviation from the task.
4. Inspect the returned implementation and evidence before moving on.5. Run a **requirements review**: does the task satisfy exactly what the plan/spec requires, with no missing requirement or scope creep?
6. Run a separate **quality review**: correctness, tests, maintainability, safety, and repository conventions.
7. If either review finds a material problem, send a bounded fix request back through an implementation agent, then repeat the affected review. Do not mark the task complete while blocking findings remain.
8. Record the completed task and evidence in a compact durable ledger, then advance to the next dependency-ready task.

Keep implementation tasks sequential when they can modify overlapping state. Fresh agents are a context-isolation technique, not permission for concurrent writes.

## Final review

After all tasks, run a whole-change requirements review, quality review, and required verification. Earlier per-task reviews do not prove cross-task integration.

## Common failures

- Giving an implementer only a short summary instead of the actual task contract.
- Letting the same success report substitute for independent requirements review and quality review.
- Redispatching completed tasks after context loss because no durable ledger was kept.
- Parallelizing implementations that touch the same files or contracts.
- Accepting "tests pass" without reading which tests and which revision were verified.

## Boundaries

Use only delegation surfaces provided by the active runtime. Do not require bundled helper scripts, fixed model tiers, background workers, or plugin prompt files. Repository authority owns write scope and task completion. In KIS-managed repositories, KIS retains Work Management, governed repository mutation, review/verification, and delivery authority.