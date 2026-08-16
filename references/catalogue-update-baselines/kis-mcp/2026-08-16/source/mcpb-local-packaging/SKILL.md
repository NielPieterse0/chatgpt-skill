---
name: mcpb-local-packaging
description: >
  Use when a user explicitly needs Anthropic MCPB packaging for a local stdio MCP
  server: create or validate an `.mcpb` bundle, manifest, bundled Node/Python
  runtime, install-time configuration, local filesystem/desktop/OS access, or
  Claude Desktop distribution. Do not use for ChatGPT or OpenAI plugin deployment,
  where current OpenAI products use remote MCP connections, or for a local stdio
  prototype that does not need MCPB distribution. Use openai-mcp-server for
  OpenAI-targeted servers and mcp-development for protocol design.
---

# MCPB Local Packaging

## Purpose

Package a local stdio MCP server for Anthropic MCPB distribution without confusing
MCPB packaging with the MCP protocol or with OpenAI's MCP deployment model.

## Authority and source order

1. Follow repository or workspace authority.
2. Verify the current Anthropic MCPB project, manifest schema, and host documentation
   before making version-sensitive packaging claims.
3. Verify core server behavior against the current MCP specification.
4. For OpenAI targets, use current official OpenAI documentation instead of treating
   MCPB as a ChatGPT installation mechanism.

## Routing boundary

Use this skill only when local packaging is itself part of the requested outcome.

Route to `openai-mcp-server` for ChatGPT, Codex, or OpenAI-plugin MCP servers.
Route to `mcp-development` for protocol architecture, interoperability, or review.
A plain local stdio prototype does not require MCPB unless the user needs the bundled
installation/distribution format.

## Default workflow

### 1. Confirm MCPB is justified

Use MCPB when the MCP server must run on the user's machine and the distribution
must bundle or control its runtime, dependencies, configuration, or desktop-local
access. Typical reasons include filesystem access, desktop-app integration, localhost
services, hardware, or OS APIs.

If the server only wraps a cloud API, prefer a remote MCP service unless the user has
a separate local-execution requirement.

### 2. Keep protocol logic packaging-neutral

The packaged server should remain a standard stdio MCP server. Keep tool logic,
protocol handlers, and authorization rules independent from the MCPB manifest and
bundle layout wherever practical.

### 3. Design the manifest from the current schema

Before editing `manifest.json`, read `references/manifest-schema.md` and verify that
its schema/version assumptions still match the current Anthropic MCPB source.

Define identity, version, server entry point, launch command, required environment,
install-time user configuration, and supported platforms explicitly. Do not invent
manifest permissions or sandbox guarantees that the current format does not provide.

### 4. Bundle runtime dependencies deliberately

Package the runtime and dependencies required by the target machines. Avoid relying
on the developer workstation's globally installed Node, Python, modules, or native
libraries. For native dependencies, test each supported target architecture/platform
rather than assuming one build is portable.

Do not add runtime installation steps to the user's first launch unless the current
MCPB distribution model explicitly requires and safely supports them.

### 5. Enforce local security in the server

Read `references/local-security.md` before exposing filesystem, process, localhost,
or OS capabilities.

The package format is not an authorization boundary. Canonicalize paths, constrain
roots, reject traversal and unsafe symlink/reparse behavior, allowlist subprocesses,
minimize inherited environment data, and re-check authorization at every protected
action. Use spec-native roots when the target host provides them and they fit the
use case.

### 6. Validate and pack with current tooling

Use the currently documented MCPB validation and packing commands rather than a
stale copied version. Validate the manifest before packing, then inspect the produced
archive to confirm required code, runtime files, dependencies, and assets are present
and no secrets or development-only files leaked into the bundle.

### 7. Test as a distribution artifact

Test the raw stdio server independently, then install the package in the intended
Anthropic host. Also test on a clean machine or environment without the developer
toolchain. Verify startup, configuration substitution, representative calls, failure
messages, local-security boundaries, upgrade behavior, and uninstall/rollback path.

## MCPB with interactive UI

MCPB can package an MCP server that also serves MCP Apps UI resources. Treat the UI
as a separate concern. If ChatGPT/OpenAI is also a target, use `openai-mcp-app-ui`
for the OpenAI-facing UI contract. For cross-host UI portability questions, use
`mcp-development` and verify each host's current implementation.

## Gotchas

- MCPB is packaging, not an MCP transport, auth model, or sandbox.
- Do not present MCPB as a first-class ChatGPT/OpenAI plugin deployment mechanism.
- Local execution increases filesystem, process, credential, and supply-chain risk.
- A package that works on the development machine may still be missing its runtime
  or native dependencies.
- Manifest schemas and CLI commands are version-sensitive; verify current sources.
- Install-time configuration does not replace server-side validation.

## Conditional references

- Read `references/manifest-schema.md` when creating, changing, validating, or
  reviewing an MCPB manifest or bundle layout.
- Read `references/local-security.md` whenever the package exposes local filesystem,
  process, desktop, localhost, OS, or credential-adjacent capabilities.

## Completion criteria

The task is complete only when MCPB is justified by a local distribution requirement;
the stdio server remains standards-correct; current manifest/tooling assumptions were
verified; local security is enforced in code rather than metadata; the bundle is
self-contained for its declared targets; packaging validation passes; and installation
or host testing is either successful or explicitly recorded as unavailable.