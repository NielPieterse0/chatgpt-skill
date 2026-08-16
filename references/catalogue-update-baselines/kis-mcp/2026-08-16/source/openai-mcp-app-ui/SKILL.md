---
name: openai-mcp-app-ui
description: >
  Use when adding or changing interactive UI returned by an MCP server for ChatGPT
  or an OpenAI plugin: MCP Apps resources, `_meta.ui.resourceUri`, `ui/*` bridge
  messaging, forms, pickers, tables, maps, editors, UI state, CSP, testing, or
  ChatGPT `window.openai` extensions. Use openai-mcp-server for the underlying
  tools and server, and mcp-development for cross-host protocol review. Do not use
  when text or structured tool output is sufficient or for ordinary web frontend
  work unrelated to MCP Apps.
---

# OpenAI MCP App UI

## Purpose

Add the smallest useful interactive MCP Apps UI to a working MCP tool, using the
portable MCP Apps surface first and OpenAI-specific extensions only where they add
capability that the shared standard does not provide.

## Authority and source order

1. Follow repository or workspace authority.
2. Verify current official OpenAI MCP Apps/UI documentation for ChatGPT behavior.
3. Verify the current MCP Apps extension for portable bridge semantics.
4. Treat compatibility aliases and host globals as host extensions, not core MCP.
## Routing boundary

Use this skill only when custom interaction materially improves the user outcome.

Use `openai-mcp-server` first when the underlying operation, tool schema, auth, or
transport is not yet settled. Use `mcp-development` when the main problem is
cross-host portability or protocol interpretation.

Prefer plain structured/text tool output when the user only needs a compact answer.
Custom UI is justified for workflows such as searchable selection, visual comparison,
editing, maps/charts, previews, or stateful interaction that plain results handle
poorly.

## Default workflow

### 1. Make the underlying tool useful without UI

Define the tool's user action, input schema, server-side authorization, structured
result, and text fallback first. The UI augments the tool; it must not become the
only place where business logic, authorization, or durable truth exists.

### 2. Register a portable MCP Apps resource

Bind the tool to its UI resource using the current MCP Apps metadata shape, including
`_meta.ui.resourceUri` when supported. Register the UI resource separately and use
the current MCP Apps HTML media type/profile required by the target SDK.

Do not return HTML as ordinary tool data when the host expects a registered UI
resource. Keep tool data and UI template responsibilities separate.
### 3. Use the standard bridge before host extensions

Use the MCP Apps `ui/*` lifecycle and bridge methods for initialization, tool input
and result delivery, server-tool calls, user messages, model-context updates, and
host-context changes when the current extension supports them.

Feature-detect capabilities. Do not branch on a hard-coded product or host name when
capability negotiation can express the distinction.

### 4. Add `window.openai` only for OpenAI-only capability

For ChatGPT-specific features not covered by the shared MCP Apps surface, verify the
current OpenAI documentation and use the smallest required `window.openai` extension.
Examples can include OpenAI-specific modal, file, checkout, or widget-state behavior,
but availability is version-sensitive and must be checked before implementation.

Do not use a ChatGPT compatibility alias when a standard MCP Apps field or method is
the current preferred path.

### 5. Keep state ownership explicit

- durable business data belongs in the server or authoritative external system;
- ephemeral presentation state can remain inside the UI;
- conversation-relevant state should use the portable model-context path when fit;
- OpenAI-specific widget persistence is optional and must not become business truth.

Design reconnect, rerender, and repeated-tool-call behavior so the UI does not depend
on accidental iframe lifetime.
### 6. Keep presentation proportional to the task

Use the smallest presentation mode that supports the interaction. Prefer inline UI
for compact workflows and request larger presentation only when the task needs the
space. Keep each widget focused on one coherent interaction rather than building a
second application inside the conversation.

An OpenAI component library may be used when it materially improves consistency, but
it is optional. Do not make standard MCP Apps behavior depend on OpenAI-only visual
components unless the user explicitly accepts that host dependency.

### 7. Enforce CSP and data boundaries

Declare only the origins and resource access the UI actually needs. Prefer routing
sensitive or authenticated operations through server tools instead of exposing
credentials to iframe code. Treat tool results, URLs, HTML fragments, images, and
external content as untrusted data and escape or validate before rendering.

Do not rely on iframe isolation as authorization. Every consequential action called
from the UI must still pass the server's normal validation and permission checks.

### 8. Test portable fallback and ChatGPT behavior

Test the registered resource and bridge lifecycle independently, then test the actual
OpenAI target. Verify initial render, tool-result updates, user actions, server-tool
calls, state changes, theme/host context where used, CSP failures, resize or display
mode behavior, and graceful fallback when custom UI is unavailable.
Use representative prompts that should and should not select the widget-enabled tool.
A visually correct widget is not enough if the model chooses the wrong tool or the
same tool becomes unusable on hosts without the UI surface.

## OpenAI-specific gotchas

- ChatGPT supports the open MCP Apps model, but OpenAI-only extensions can evolve
  independently of the shared extension.
- `window.openai` is an extension surface, not the portable bridge contract.
- Compatibility aliases can outlive the preferred API; check current docs before
  using an older example.
- UI metadata does not authorize effects or protect secrets.
- Keep meaningful text or structured output when a non-UI host can still use the
  underlying tool.
- Prefer capability detection over product-name detection.
- Do not freeze plan availability, size limits, or submission rules into the skill;
  verify current OpenAI documentation when those facts matter.

## Validation

Before completion, verify:

- the underlying MCP tool works without custom UI where practical;
- custom UI has a user-outcome justification;
- the resource registration and bridge use the current MCP Apps contract;
- OpenAI-only APIs are isolated, feature-detected, and currently documented;
- state ownership, CSP, data exposure, and server-side authorization are explicit;
- representative interaction and fallback paths were exercised;
- current ChatGPT behavior was tested when the environment permits it;
- any untested host, submission, or live-runtime behavior is reported as a limit.

Do not claim cross-host portability solely because the UI renders in one OpenAI
surface; portable behavior must be supported by the shared MCP Apps contract.