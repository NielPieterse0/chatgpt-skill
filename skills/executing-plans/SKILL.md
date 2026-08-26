---
name: executing-plans
description: Use when a reviewed implementation plan already exists and the work should be executed task-by-task with explicit checkpoints and verification.
license: MIT
---

# Executing Plans

Execute an approved plan without silently redesigning it during implementation.

## Start by reviewing the plan

1. Read the entire plan, repository authority, and current repository state before changing files.
2. Check for a material plan defect: contradiction, missing prerequisite, stale assumption, unsafe operation, impossible sequence, or requirement no longer represented.
3. Resolve a material plan defect through the design or planning authority. Do not improvise around it and still call the plan followed.
4. Confirm the repository-authorized workspace, current work claim, and verification expectations before implementation.

## Execute task by task

For each task:

1. Confirm its dependencies are satisfied and its scope is still current.
2. Apply the task's required test-first, debugging, review, or specialist method when applicable.
3. Implement only that task's intended behavior; do not absorb nearby cleanup without authority.
4. Run the task's specified checks and inspect the actual result.
5. Record concise evidence sufficient to resume at the first incomplete task after context loss.## Checkpoints and stop conditions

Use the plan's own review/checkpoint cadence. If none is specified, report after a coherent task group rather than creating arbitrary ceremony.

Stop execution and return to the responsible authority when:

- implementation exposes a requirement or architecture conflict;
- a required dependency or capability is unavailable;
- verification fails for a reason outside the current task;
- continuing would exceed the plan's write, risk, or repository scope.

Do not keep making speculative changes merely to stay "on plan."

## Finish

After all tasks are complete, reconcile the plan against the implemented state, run whole-change review and verification, and hand the verified branch or change to the repository-authorized closeout workflow.

## Boundaries

A plan does not authorize remote publication, merging, deployment, destructive cleanup, or scope expansion. In KIS-managed repositories, use live KIS workflows for governed repository/GitHub operations and Work Management rather than reconstructing those actions from the source skill.