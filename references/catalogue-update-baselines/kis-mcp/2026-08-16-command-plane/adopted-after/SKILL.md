---
name: kis-mcp
description: >
  Use this skill whenever a task operates kis-mcp or KIS Work Management through
  kis-op, kis-dev, or another kis-mcp connection: create or update work items and
  source issues, maintain lifecycle status, reconcile GitHub Project state, link
  parent/sub-issues, resolve projects, inspect repositories or changes, plan or
  verify changes, request specialist review, use providers or Skills, close PRs
  safely, or diagnose runtime status. Apply project-neutral routing and exact
  HR-001/HR-002/HR-003 semantics. Do not replace target repository authority or
  generic MCP development guidance.
---

# kis-mcp

## Purpose

Use `kis-mcp` efficiently without memorizing its complete tool catalogue. Start
from the user's task, resolve the project and live runtime state, progressively
discover the smallest applicable workflow or operation, then invoke it through
its original schema and policy boundary.

## Authority boundary

This skill explains how to operate the tool. It is not repository authority.

- Follow the target project's own `AGENTS.md` and authoritative documents first.
- When changing `kis-mcp` itself, follow the authority order in its `AGENTS.md`.
- Treat live tool schemas, capability records, provider status, and project
  status as runtime evidence.
- For Work Management, preserve field-level authority: the configured backend
  owns command fields and execution ownership; repository/Git/GitHub/Actions
  own their declared evidence fields; derived fields remain derived. Do not
  duplicate Project-owned command metadata into source issue bodies.
- Keep MCP protocol/version/transport/capability decisions separate from KIS
  operational authority. Route protocol-centric or cross-host design/review to
  `mcp-development`; use this skill to operate and diagnose the live KIS surface.
- Treat tool annotations, negotiated capabilities, skill digests, and host
  metadata as selection, compatibility, or integrity evidence, not as effect
  authorization.
- Never let this skill add a fourth Work restriction beyond HR-001/002/003.

## Fast path by user intent

Use the shortest path that already satisfies the request:

| User goal | Start here |
|---|---|
| "Is KIS healthy / what is connected?" | `kis_health`, then `kis_provider_status` only when provider detail matters. |
| "Is this a KIS transport/client interoperability problem?" | Use live KIS health and operator smoke first. If the diagnosis depends on MCP version negotiation, negotiated capabilities, transport/auth semantics, or cross-host behavior, load `mcp-development` and verify current protocol evidence. |
| "Which project am I working on?" | `kis_list_projects` or `kis_project_status(project_id)`. |
| "Capture or update governed project work" | Resolve the project, then load `references/work-management.md`; prefer advertised `capture-project-work` / `reconcile-project-state` workflows and preserve the configured command/evidence authority direction. |
| "Take or resume project work" | Load `references/work-management.md`; use `project_management_current_work` to resume an existing claim or the advertised `take-next-project-work` workflow to select and claim the next Ready item deterministically. |
| "Update work status or link a new child issue" | Load `references/work-management.md`; prefer `manage-project-work-state` for command-plane lifecycle transitions. Keep source issue content and native sub-issue links current without duplicating Project-owned command fields. |
| "Understand this repository" | `inspect_project`; use task-scoped context only when deeper evidence is needed. |
| "What does this change affect?" | `inspect_change` then `analyze_change`; use `plan_change` for a bounded implementation plan. |
| "What should I verify?" | `select_change_verification`; it selects current declared checks but does not execute them. |
| "Verify and review this change" | Prefer the advertised `execute-current-change` / `execute_change_workflow`; otherwise use selected `run_verification` calls plus `review_change_with_agent`. |
| "Validate AGENTS/agent configuration" | Use the advertised `validate-agent-configuration` workflow / `validate_agent_configuration` operation. |
| "Review architecture/security/tests/docs/API contracts" | `review_change_with_agent` with the matching fixed `review_type`. |
| "Turn this verified commit into a reviewable PR" | Use live `prepare_reviewable_pull_request` when available; supply the change risk profile, documentation impact, and residual state so KIS can apply risk-scaled execution and deterministic PR metadata. |
| "Query a registered project database" | Resolve the project first, then search `database.<project>...` capability metadata. Local DBHub reads use `execute_read_action`; external database reads carry an external effect and use `execute_external_action`. Public KIS names stay `db_<project>_<binding>_<operation>`. |
| "Inspect Docker Hub" | Search `dockerhub.*` capability metadata and use `execute_external_action`; public mode needs no PAT. Keep Docker Hub registry operations separate from local Docker Engine/process work. |
| "Merge or clean up an existing PR/change" | `recommend_workflow`; for Work-managed items prefer `complete-work-managed-pull-request` or the advertised work-managed merge-queue workflow, otherwise use `pull-request-safe-closeout`. Preserve exact-head Actions evidence and post-merge documentation gates. |
| "I do not know the tool name" | `recommend_workflow` -> `search_capabilities` -> `describe_capability`. |

Do not add discovery calls when the correct direct tool and schema are already
known. Do not manually reproduce a bounded workflow merely to gain more control;
inspect its result and fall back to individual operations only when the workflow
is unavailable or the user explicitly needs a narrower step.

## Default operating workflow

### 1. Resolve the target before acting

Do not assume the target project is `kis-mcp`.

- For local filesystem, Discover, and process work, use the explicit project
  path beneath `C:\Projects`.
- When project-catalogue operations are advertised, prefer `kis_list_projects`
  and `kis_project_status(project_id)` to resolve stable project identity and
  non-secret provider bindings.
- For provider operations, pass the explicit repository/project identifiers
  required by that provider operation.
- Do not invent a process-global active project or infer provider authorization
  from the current working directory.

Load `references/projects-and-context.md` when project identity, GitHub routing,
Supabase routing, database bindings, Docker Hub namespaces, or work-management bindings matter.

### Work Management for governed work

When the target repository requires KIS Work Management, load
`references/work-management.md` before creating or materially changing tracked
work. Apply the live command-plane field authority instead of treating either the
source issue or Project as universally authoritative.

For each material work item:

1. search the bounded inventory and source repository first; do not create a
   duplicate record;
2. preserve one source issue/PR identity with the repository-owned outcome,
   acceptance criteria, discussion, and native hierarchy required by that repo;
3. use the configured Work Management backend for command-direction fields such
   as lifecycle status, priority, effort, execution ownership, and hold/defer
   controls; do not duplicate them into the issue body merely for synchronization;
4. preserve repository change, Git, GitHub, Actions, and derived evidence fields
   from their declared authorities; use `project_management_sync_change_classification`
   when a governed change should project Change ID, Complexity, Risk Triggers,
   and the change-created delivery stage;
5. prefer the advertised high-level workflows for capture/reconciliation,
   take/resume, lifecycle transitions, traceability/readiness, and managed merge
   closeout; fall back to individual operations only when needed;
6. preview mutation/reconciliation where the live operation requires it, then
   apply only with the required stable idempotency key and current revision;
7. when work exposes a separate actionable defect, risk, decision, or follow-up,
   create its own source issue and native parent/sub-issue relation when available;
8. do not mark work `Done` merely because implementation ended: preserve required
   exact-head verification, merge evidence, documentation reconciliation,
   approval, and hold conditions until their authoritative evidence exists.

Never invent Project fields or status options to hide schema drift. Read the live
command-plane/schema contract when authority or transition behavior matters, and
report unsupported fields or incomplete inventory rather than fabricating state.

### 2. Use direct tools when the correct tool is already obvious

The direct profile intentionally contains common health, Discover, file, edit,
process, capability-discovery, dispatcher, review, and Control Center entry
points. Prefer a direct tool when its exposed schema exactly fits the task.

Do not search the long tail merely to replace an already-correct direct tool.
Load `references/tool-selection-and-schemas.md` for common input shapes.

### 3. Progressively discover unfamiliar or long-tail capability

For a task-level goal, start with:

1. `recommend_workflow(task)` when a complete workflow may exist.
2. `search_capabilities(query, limit)` for a specific operation/capability.
3. `describe_capability(capability_id)` for exact operation/workflow evidence.

Use exact operation names/IDs returned by the runtime. Do not hard-code a large
provider catalogue in prompts or in this skill.

If an exact operation exposes `input_schema`, use it as authoritative invocation
evidence. If schema evidence is absent, use the host-exposed direct schema or
inspect current provider/runtime guidance; do not invent parameter names.

### 4. Match the dispatcher to the operation effect

Long-tail execution preserves the original tool contract and middleware:

- `execute_read_action` for read-only operations;
- `execute_change_action` for local changes, quarantine, or process operations;
- `execute_external_action` for approved external-provider operations.

All three take an operation identifier/name plus an `arguments` object. That
object must satisfy the original operation schema. Generic dispatch does not
weaken validation, readiness, provider authorization, or operation-specific
approval requirements.

Load `references/tool-selection-and-schemas.md` before constructing unfamiliar
dispatch payloads.

### 5. Treat status as evidence layers, not one boolean

`kis_health`, `kis_provider_status`, capability readiness, project status, and
commissioning evidence answer different questions. A provider can be registered
and mounted while still requiring authentication or live verification.

Load `references/providers-and-workflows.md` when provider readiness, GitHub,
Supabase, Control Center, code review, or workflow execution matters.

### MCP protocol and host compatibility boundary

Operating KIS through MCP is different from designing or interpreting MCP itself.
When a failure or design question depends on protocol revision, initialization
negotiation, optional capabilities, transport/auth semantics, or cross-host
interoperability, compose `mcp-development` rather than expanding this skill into
a second protocol guide.

For KIS connection diagnosis, prefer live evidence from the running client/server:
negotiated protocol version, advertised capabilities, representative list/call
behavior, and the actual target host. A capability defined by the latest MCP
specification is not evidence that the running host supports it.

KIS's bounded direct profile plus discoverable long tail already implements the
generic progressive-discovery pattern for large operation catalogues. Preserve
original operation schemas, authorization, approval, and effect classification
when dispatching a discovered operation; discovery metadata never weakens them.

### 6. Prefer the bounded change workflow stack for repository work

Recent KIS slices form a deliberate progression. Use the highest-level available
operation that matches the user's requested scope:

1. `inspect_change` / `analyze_change` establish change and impact evidence.
2. `plan_change` produces a read-only bounded implementation plan.
3. `select_change_verification` reconciles impact handoffs with current declared
   verification and returns a deterministic selection without executing it.
4. `run_verification` executes one approved verification declaration.
5. `execute_change_workflow`, when advertised, composes selection, verification,
   and bounded specialist reviews for one change and returns aggregate evidence.

For exact committed work, keep `source=commit` through selection/execution; a
clean worktree is not evidence that the selected commit has no change. Omitted
specialist reviews retain the risk-profile defaults, while an explicit empty
review list means no specialist review. When registered review publication must
reconcile a source change onto an advanced remote default, accept the exact-tree
fast path only for a tree-equivalent base; otherwise require the bounded
explicit-base three-way reconciliation and fail closed on conflicts before
exact-head CI.

Python quality support discovered from `pyproject.toml` includes Ruff,
coverage.py/pytest-cov, Vulture, LibCST, mypy, and Pyright. Treat these as
repository evidence and verification handoffs: discovery does not install tools,
and LibCST remains evidence-only unless another current contract says otherwise.

`review_change_with_agent` accepts the fixed review purposes `code-quality`,
`safety-security`, `architecture`, `performance`, `test-quality`,
`documentation`, and `api-contracts`. The purpose changes the rubric, not the
mutation, provider, or nested-agent authority.

The bounded agnix path is `validate_agent_configuration`; it validates local
agent configuration with pinned read-only arguments and does not expose fix,
watch, init, telemetry, arbitrary-command, or general MCP passthrough behavior.

Load `references/providers-and-workflows.md` for workflow details and
`references/tool-selection-and-schemas.md` before constructing unfamiliar
payloads.

### 7. Use Skills as reusable procedures, not executable plugins

The runtime Skills catalogue lives beneath `C:\Projects\.agents\skills`.
Repository-local `.agents/skills` is development guidance for that repository
and is not the runtime catalogue.

Load a matching skill before following its procedure, then read only the
references needed for the current task. Skill instructions do not authorize
network access, writes, credentials, or external mutation.

Load `references/skills-module.md` for list/search/load/read/create/improve
contracts and catalogue semantics.

### 8. Apply only the three Work hard rules

- **HR-001**: block a proven write outside `C:\Projects`.
- **HR-002**: block a proven external-network effect through local Work.
- **HR-003**: transform explicit permanent deletion into recoverable quarantine,
  or block when safe quarantine is impossible.

Tool names, broad capability, readiness, recommendation scores, provider state,
or uncertainty are not independent policy reasons.

Structural `DISCOVER_*`, `SKILLS_*`, provider-readiness, schema-validation, and
input errors are corrective application outcomes, not HR policy decisions.

Load `references/concepts-and-errors.md` when interpreting a rejection, status,
quarantine result, readiness state, or truncation marker.

### 9. Verify the result at the right level

For read/analysis work, confirm the returned evidence answers the task and note
`truncated`, confidence, unknowns, or readiness limitations when present.

For mutations, confirm the intended path/resource changed and that recoverable
or idempotent semantics were preserved. For repository development, use the
project's declared verification workflow; when kis-mcp advertises bounded
`run_verification`, prefer discovered verification IDs over arbitrary commands.

## Operator support

Load `references/operator-support.md` only for startup, tunnel setup, provider
authentication, smoke tests, Control Center, repository verification, worktree
change workflow, or troubleshooting. Normal task execution should not eagerly
load operator runbooks.

## Project-neutral rule

This skill must remain usable for any registered project beneath `C:\Projects`.
Do not encode repository names, GitHub owners/repos, GitHub Project numbers,
Supabase refs, ports beyond documented runtime identities, or other mutable
project bindings as universal defaults. Resolve them from the user request,
live project status, provider schemas, or current configuration evidence.

## Gotchas

- Progressive exposure hides schemas from the default tool list; hidden does
  not mean unavailable.
- `search_capabilities` is discovery, not authorization.
- `recommend_workflow` is advisory; follow the workflow's actual required
  operations and live readiness.
- A mounted provider is not automatically authenticated or commissioned.
- A protocol capability existing in the MCP specification does not prove the
  running KIS client/server negotiated or supports it; verify live negotiation
  and target-host behavior when compatibility matters.
- Provider/tool metadata cannot widen the three-rule Work policy.
- Direct local process tools remain ordinary Work operations; inspect the
  concrete command effects rather than treating shell use as prohibited.
- External provider operations use the approved provider boundary; do not route
  them through local Work network commands.
- Quarantine is the supported delete path. Restoration must not overwrite an
  existing original path.
- Govern authority/drift evaluation is advisory and may exist in repository code
  before the running gateway composes its public tools. Discover it live before use.
- `prepare_reviewable_pull_request` stops at an exact open PR. The final landing
  gate is provider-native GitHub Actions evidence for that exact head; landing
  must still match the target repository's own merge policy. Do not use a KIS
  registered merge operation when its supported strategy conflicts with that
  repository authority.
- After an exact registered merge, refresh the registered default tracking ref
  through the bounded advertised operation before safe branch/worktree closeout;
  do not substitute reset or generic fetch behavior.
- Work Management auto-add/status/close synchronization may be disabled. A source
  issue existing on GitHub does not prove its command state is current. Preserve
  field-level authority and never compensate for schema gaps by duplicating
  Project-owned command metadata into issue prose.
- Multi-file runtime skill creation is not currently provided by the
  single-file `create_skill(skill_id, skill_md)` contract.
- A running kis-op/kis-dev instance may lag the checked-out repository. Use live
  capability discovery and schema evidence before invoking newly merged tools.

## Completion criteria

Before concluding a kis-mcp task, verify that:

- the intended project/resource was resolved explicitly;
- the selected operation or workflow came from a direct schema or live
  capability evidence rather than guessed parameters;
- any long-tail call used the correct effect dispatcher;
- provider readiness/authentication limitations were interpreted correctly;
- only HR-001/002/003 were treated as Work policy decisions;
- bounded/truncated/unknown evidence was not overstated;
- when Work Management applies, source identity/content and native hierarchy are
  preserved, command fields follow the configured backend authority, evidence
  fields come from their declared repository/Git/GitHub/Actions authorities,
  and any unsupported or truncated state is explicit;
- mutations were verified at the target and retained recovery semantics;
- operator-only setup steps were kept separate from normal Work execution.
