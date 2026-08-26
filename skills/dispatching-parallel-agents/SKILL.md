---
name: dispatching-parallel-agents
description: Use when two or more tasks are independent, can be solved without shared mutable state, and the active runtime provides isolated agent delegation.
license: MIT
---

# Dispatching Parallel Agents

Use parallel agents to shorten independent investigation or work without mixing context, duplicating effort, or creating edit conflicts.

## Decide whether work is independent

Parallelize only when each task has a separate failure domain or deliverable and can finish without another task's intermediate result.

Keep work sequential when tasks:

- modify overlapping files or shared mutable state;
- depend on an earlier design or implementation decision;
- require one coherent end-to-end understanding;
- would compete for the same external or repository mutation authority.

## Workflow

1. Partition the work by independent problem domain, evidence source, or deliverable.
2. Give each agent one bounded objective, relevant context, explicit exclusions, expected evidence, and a clear return format.
3. Avoid passing the entire session history. Include only what that task needs to be correct.4. Dispatch concurrently only through agent-delegation capability actually exposed by the active runtime.
5. Review every return for scope, evidence, uncertainty, and unresolved findings before integrating it.
6. Resolve contradictory findings explicitly; do not average them into a false consensus.
7. Run combined verification after integration. Independent task success does not prove the combined result.

## Prompt contract

A good delegated task states the problem, exact scope, constraints, evidence to inspect, actions permitted, actions prohibited, and what the coordinator needs back. It does not prescribe a guessed solution when investigation is the task.

## Common mistakes

- **Too broad:** "Fix everything" creates overlapping ownership. Split by independent domain.
- **Too little context:** agents rediscover constraints or violate scope. Provide the authoritative inputs they need.
- **Parallel edits to shared state:** use `subagent-driven-development` or sequential execution instead.
- **Trusting agent success reports:** inspect returned evidence and verify the integrated state.

## Boundaries

Do not invent background execution, fixed model tiers, helper scripts, or unavailable subagent tools. Repository authority controls write scope and ownership. In KIS-managed repositories, KIS remains the authority for governed work, repository mutation, and integration; this skill only supplies the parallelization method.