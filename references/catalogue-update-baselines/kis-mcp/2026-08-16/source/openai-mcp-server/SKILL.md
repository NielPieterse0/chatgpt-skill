---
name: openai-mcp-server
description: >
  Use when building or materially changing an MCP server intended for ChatGPT,
  Codex, or an OpenAI plugin: define tools, server instructions, Streamable HTTP,
  authorization, metadata, structured results, resources or prompts, and OpenAI
  developer-mode validation. Prefer mcp-development for protocol-centric,
  cross-host, compliance, or modernization work; openai-mcp-app-ui for custom
  interactive UI; and mcpb-local-packaging only for Anthropic MCPB distribution.
  Do not use for ordinary APIs or generic frontend work.
---

# OpenAI MCP Server

## Purpose

Build a standards-correct MCP server whose tool surface is optimized for reliable
selection and use in OpenAI products without turning OpenAI-specific behavior into
MCP protocol requirements.

## Authority and source order

1. Follow the governing repository or workspace instructions.
2. For OpenAI product behavior, verify the current official OpenAI developer docs.
3. For core protocol behavior, verify the current stable MCP specification and SDK.
4. Treat drafts, examples, compatibility aliases, and host extensions as separate
   evidence rather than normative MCP requirements.
## Routing boundary

Use this skill for straightforward OpenAI-targeted MCP server construction.

Route elsewhere when the dominant problem is:

- protocol interpretation, cross-host portability, version negotiation, or review
  of an existing integration → `mcp-development`;
- custom iframe UI, MCP Apps resources, or ChatGPT UI extensions →
  `openai-mcp-app-ui`;
- Anthropic `.mcpb` packaging for a local stdio server → `mcpb-local-packaging`.

Do not add UI or local packaging merely because those options exist.

## Default workflow

### 1. Establish the runtime boundary

Determine the upstream system, target OpenAI product, mutation risk, authentication
model, deployment boundary, expected user actions, and implementation stack.

For ChatGPT, design around the currently supported remote MCP connection model and
verify current OpenAI documentation before choosing a transport or tunnel. Do not
assume a local stdio server is directly installable in ChatGPT.

### 2. Design user-recognizable tools first

Start from user actions, not upstream endpoint names. Give each distinct action a
clear tool when that keeps selection precise. Use progressive discovery only when
a large operation catalogue would otherwise overwhelm the exposed tool surface.
For every exposed tool:

- use a concise action-oriented name and useful title;
- write a description that begins from when the model should use it;
- define required inputs explicitly with bounded schemas and enums where useful;
- define structured outputs when downstream reasoning benefits from them;
- mark read-only, destructive, and open-world annotations accurately;
- keep authorization enforcement in the server or upstream system, never metadata.

### 3. Write concise server instructions

Use server-level instructions only for guidance that applies across the whole MCP
surface. Put the highest-value routing or behavioral guidance first. Do not repeat
full tool descriptions or bury critical constraints in long prose.

### 4. Return model-friendly results

Prefer structured content for machine-usable data and concise text for human/model
summaries. Keep host-only metadata separate from ordinary model-visible content.
Never return credentials, bearer tokens, private configuration, or unnecessary
sensitive data in tool results.

Bound payload size, pagination, retries, concurrency, and error detail. Errors should
state what failed and what valid corrective action is available.

### 5. Add other MCP primitives only when ownership fits

Use resources for application-managed contextual data and prompts for reusable
user-selected prompt templates. Use optional protocol capabilities only when the
client negotiates them and the task materially benefits. Provide a fallback when a
required host may not support an optional capability.
### 6. Keep authorization at the effect boundary

Validate identity and permissions for every protected operation. Treat annotations,
confirmation UX, and tool descriptions as model-selection or user-control signals,
not security enforcement.

For remote authorization, follow the current MCP authorization specification plus
current OpenAI requirements. Do not transplant HTTP OAuth behavior into local stdio.

### 7. Add OpenAI plugin behavior deliberately

When the server is used in an OpenAI plugin, keep live data, actions, and auth in
the MCP server. Keep reusable workflow instructions in Agent Skills rather than
encoding a long procedural playbook into tool descriptions.

If the task involves importing Agent Skills from MCP, first verify the current
OpenAI Skills/MCP extension documentation. Treat that surface as version-sensitive;
do not infer support from the core MCP specification.

### 8. Add UI only after the plain tool works

A tool that will render custom UI should still return useful structured/text output
without the UI whenever practical. Once the underlying operation is correct, load
`openai-mcp-app-ui` for MCP Apps resources and ChatGPT-specific UI extensions.

### 9. Test selection and wire behavior

Run the repository's own checks, then exercise initialize, capability negotiation,
tools/list, representative tools/call behavior, error shapes, authorization, and
retry/idempotency behavior as applicable.
Use MCP Inspector or another protocol client for fast wire-level checks. Then test the
actual OpenAI target in its supported developer workflow. Use representative direct,
indirect, incomplete, and should-not-select prompts to validate tool metadata.

For public deployment, verify the current OpenAI submission requirements rather than
copying a development tunnel or private test setup into production guidance.

## OpenAI-specific gotchas

- OpenAI product behavior can change independently of the MCP specification.
- Tool annotations improve selection and confirmation UX; they do not authorize work.
- A server can be protocol-correct and still have poor tool selection because its
  names, descriptions, or schemas are ambiguous.
- Do not require historical `search`/`fetch` tool conventions unless the current
  OpenAI use case explicitly requires them.
- Refresh or reconnect the OpenAI developer connection when metadata changes if the
  product caches tool definitions.
- Do not branch on an assumed host name when negotiated capabilities provide the
  correct compatibility signal.

## Validation

Before completion, verify:

- the target product and deployment boundary are explicit;
- version-sensitive OpenAI behavior was checked against current official docs;
- tool names, descriptions, schemas, outputs, and annotations match user intent;
- protected effects enforce authorization independently of metadata;
- optional capabilities are negotiated or have a fallback;
- representative protocol calls and OpenAI selection prompts were exercised;
- any UI or packaging dependency is routed to the specialist skill rather than
  duplicated here.

Report unavailable live-auth, deployment, submission, or target-observability checks
as limitations rather than inferred passes.