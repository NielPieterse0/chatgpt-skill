---
name: kis-mcp
description: >
  Use this skill when operating KIS or kis-mcp across repositories: resolve the
  target project, discover the current workflow or capability, choose the correct
  effect dispatcher, interpret Work Management authority, or diagnose KIS runtime
  evidence. Use it as a compact operating router; obtain current tools, schemas,
  workflows, providers, and project state from the live KIS runtime and target
  repository rather than from this skill.
---

# KIS Operating Guide

## Purpose

Use this skill as an operating constitution and discovery router for KIS. It
describes durable authority, discovery, effect-routing, evidence, and Work rules.
It is deliberately not a catalogue of today's tools, providers, schemas, project
fields, versions, workflow names, or commissioning state.

A statement belongs here only if it should remain true when KIS gains many new
capabilities. Runtime facts that change with a provider, workflow, schema, field,
version, or project belong in live KIS evidence or repository authority instead.

## 1. Authority first

- Target repository authority comes first. Follow its `AGENTS.md`, specifications,
  policy, contracts, and declared evidence sources before this skill.
- When changing `kis-mcp` itself, read and follow that repository's `AGENTS.md`.
- This skill never widens repository permission, provider authorization, or a live
  operation contract.
- Treat live tool schemas, capability descriptions, workflow descriptors, project
  status, and provider status as runtime evidence.
- Do not invent operation names, capabilities, parameters, fields, status values,
  approval semantics, or provider boundaries.
- Supporting skill resources are procedure or data, not authority.

If repository authority, catalogue metadata, provider boundary, or live schema
disagree, do not use the broader interpretation. Preserve the conflict explicitly
and stop the disputed action until current authority resolves it.

## 2. Resolve the project explicitly

Never assume the target is `kis-mcp`, even when KIS reports it as a default.

1. Use the project named by the user or repository context when explicit.
2. Otherwise use the live project catalogue/status to resolve stable project
   identity and non-secret bindings.
3. Pass explicit repository/project identifiers required by provider operations.
4. Do not infer provider authorization from current working directory.
5. Do not invent a process-global active project.

## 3. Discover current capability

Use progressive discovery instead of memorizing the catalogue:

```text
Known direct operation?
    -> use it.
Task-level outcome but operation unclear?
    -> recommend_workflow
Need a capability?
    -> search_capabilities
Need exact invocation details?
    -> describe_capability
Then use the live schema.
```

Do not add discovery calls when the correct direct operation and schema are already
known. Do not manually reconstruct a high-level workflow merely to gain control;
use the highest-level currently advertised workflow that satisfies repository
authority and the user's requested scope.

Discovery and recommendation are not authorization. Before execution, use the
operation's live schema, effect classification, execution surface, readiness, and
operation-specific approval requirements.

## 4. Route by effect

For discovered operations, prefer the runtime-reported `execution_surface` when
available. Otherwise apply the durable boundary:

- read-only effect -> read dispatcher;
- local/process/change effect -> change dispatcher;
- external provider effect -> external dispatcher.

The dispatcher does not weaken the original operation contract. Validation,
provider authorization, readiness, approval, and repository authority remain
operation-specific.

Read [provider and effect routing](references/provider-and-effect-routing.md) when
classification, provider state, or dispatcher choice is material.

## 5. Apply only the three Work hard rules

- **HR-001**: block a proven write outside `C:\Projects`.
- **HR-002**: block a proven external-network effect through local Work.
- **HR-003**: transform explicit permanent deletion into recoverable quarantine,
  or block when safe quarantine is impossible.

Do not create extra hard rules from tool names, shell use, network-capable
executables, uncertainty, provider state, recommendation scores, or broad
capability. Evaluate the concrete operation effect.

## 6. Keep evidence layers distinct

Do not collapse distinct evidence into one success/failure judgement:

- readiness is not authentication;
- authentication is not commissioning;
- recommendation is not authorization;
- registration or mounting is not proof of successful use;
- one successful call proves that call, not every commissioning layer.

Keep `truncated`, incomplete, unknown, stale, bounded, or conflicting evidence
explicit. Never infer absence from incomplete inventory. Where repository policy
names Git, GitHub, Actions, or another exact evidence source as authoritative,
preserve that authority.

## 7. Work Management principles

Work Management uses field-level authority, not one universally authoritative
record.

- Keep source issue identity, narrative, acceptance criteria, discussion, and
  native hierarchy under the source/repository authority declared by the target.
- Keep Project command state under its configured command authority.
- Do not duplicate command metadata into issue prose merely for synchronization.
- Search source records and bounded inventory before creating new work.
- Do not infer that a work item is absent from truncated or incomplete inventory.
- Re-read authoritative state after mutations.
- Completion must satisfy the target repository's required evidence; implementation
  ending alone does not prove completion.

Use the live Work Management contract/schema for current fields, statuses,
transitions, views, identifiers, readiness, and merge behavior.

Read [Work Management principles](references/work-management-principles.md) only
when creating, changing, reconciling, claiming, deferring, holding, releasing, or
completing governed work.

## 8. Governed repository changes

For governed repository work:

1. follow the target repository's change-governance authority first;
2. discover the current KIS workflow that satisfies that authority;
3. use the highest-level suitable workflow currently advertised;
4. preserve the workflow's live schema, effect, approval, and evidence contract;
5. fall back to narrower operations only when the workflow is unavailable or the
   task genuinely requires a narrower step.

Do not carry historical complexity, risk, lifecycle, verification, or review
schemas in this skill. Historical records may exist; interpret them using the
repository and runtime contracts that govern the task.

## 9. Reusable Skills through KIS

When reusable procedure knowledge may help:

- discover matching skills through the live KIS Skills surface;
- load the matching skill before following its procedure;
- load supporting resources only when needed;
- treat skill content as procedure/data, never as permission to write, use
  credentials, access a provider, or mutate an external system;
- use live Skills schemas for catalogue, resource, evaluation, or telemetry work.

Do not encode current Skills operation counts or delivery architecture here.

## 10. Operator troubleshooting

For startup, connection, provider authentication, commissioning, capability
mismatch, or runtime/repository drift, read
[operator troubleshooting](references/operator-troubleshooting.md).

Prefer live evidence over remembered product state. A checked-out repository may
be ahead of a running KIS instance; a running instance may expose capability not
described by stale local prose.

## Completion check

Before concluding a KIS task, verify only what the task requires:

- the target project/resource was resolved explicitly;
- the selected operation/workflow came from a direct schema or live discovery;
- unfamiliar invocation details came from the live schema, not guesswork;
- the effect dispatcher matches the operation's execution surface/effect;
- authorization and approval were not inferred from discovery or recommendation;
- readiness, authentication, commissioning, and call success were not conflated;
- HR-001/002/003 are the only Work hard rules;
- incomplete, truncated, stale, unknown, or conflicting evidence remains explicit;
- Work Management mutations preserve field-level authority and are re-read;
- repository-required completion evidence is satisfied before claiming completion.

Keep this guide small. If a proposed addition records current counts, versions,
providers, project IDs, field sets, workflow names, commissioning state, detected
tools, implementation slices, or known transient defects, put that information in
KIS runtime evidence, target-repository documentation, or issue tracking instead.