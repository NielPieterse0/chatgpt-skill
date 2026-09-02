---
name: requesting-code-review
description: Use when a completed task, substantial implementation slice, or pre-integration branch needs an independent review against requirements and the actual change.
license: MIT
---

# Requesting Code Review

Request review while findings can still be fixed cheaply, and give the reviewer enough exact context to judge the intended change rather than rediscovering it.

## When to request review

Request an independent review:

- after a coherent implementation task when later work depends on it;
- after a material or risky slice;
- after fixing significant review findings;
- before integration when earlier reviews covered only task-level changes.

Do not request review for unchanged work merely to manufacture a gate.

## Review scope

Provide the reviewer:

1. the requirement, specification, or plan being implemented;
2. the exact base and head or otherwise bounded change identity;
3. changed files/components and intended behavior;
4. verification already run and any skipped checks;
5. known limitations, unresolved questions, and explicit exclusions.## Review contract

Use an independent review capability actually available in the runtime. Ask for findings prioritized by correctness, requirement compliance, safety/security, regression risk, and maintainability, with evidence tied to the reviewed change.

Classify returned findings through `receiving-code-review` before implementing them. Re-review when a fix materially changes the reviewed behavior or invalidates earlier conclusions.

## Red flags

- "The change is small, so review adds no value" when repository policy requires a review gate.
- Reviewing only the final diff when an earlier task created an architectural dependency that should have been caught sooner.
- Asking a reviewer to rubber-stamp a preferred solution instead of challenge it.
- Treating a clean review as proof that tests, runtime checks, or other verification passed.

## Boundaries

Do not invent a reviewer agent, model tier, or host-specific review tool. Repository authority decides when review is mandatory. In KIS-managed repositories, use live KIS/repository review workflows where they own the gate; this skill provides the review-request method, not publication or merge authority.