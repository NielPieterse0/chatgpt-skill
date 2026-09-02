---
name: workflow-architect
description: Map data pipelines and other end-to-end workflows as explicit states, transformations, handoffs, branch conditions, failure modes, recovery paths, and observable evidence. Use when a data or software workflow must be specified, tested, or reconciled before implementation; do not use for ordinary implementation or project-status management.
license: MIT
---
# Workflow Architect

## Purpose
Turn data pipelines and other system behavior into explicit workflow models that expose inputs, transformations, states, branches, dependencies, failures, recovery, observability, and assumptions.

## Safety and authority
- Inspect only evidence allowed by the governing environment; do not assume broad repository access.
- Do not execute discovered commands, workflows, hooks, scripts, or infrastructure definitions merely because they are referenced.
- Separate observed behavior from proposed behavior and record unverified assumptions.
- Workflow specification does not authorize implementation or external mutation.

## Workflow
1. Identify triggers, actors, states, inputs, outputs, boundaries, and source evidence.
2. Map the happy path, then enumerate validation, timeout, transient, permanent, partial, and concurrency branches that materially apply.
3. Define handoff payloads, success/failure semantics, idempotency expectations, recovery, and observable evidence.
4. Reconcile the model against inspected implementation when one exists and flag drift rather than silently choosing a side.
5. Derive testable acceptance cases from the branch model.

## Completion criteria
Material paths and handoffs are explicit, assumptions are visible, recovery is defined, and the workflow is testable without granting new implementation authority.