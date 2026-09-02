# AI-Generated Code Security Audit Technical Depth

Load this reference when reviewing AI-generated, AI-assisted, scaffolded, or rapidly prototyped application code for security failure modes that are disproportionately common in generated code. Keep the audit read-only unless a separately governed implementation workflow authorizes fixes.

## Audit stance

Generated code is not insecure because AI wrote it. The useful prior is narrower: coding assistants often optimize for a working happy path and copy tutorial defaults, which can produce predictable security gaps. Verify each suspected gap from code and configuration rather than attributing risk to provenance alone.

For each finding establish:

- source location and affected artifact;
- attacker-controlled or exposed input/value;
- trust boundary or privilege assumption;
- sensitive sink or consequence;
- realistic exploit/precondition;
- confidence level;
- smallest safe remediation;
- verification/rescan method.

Prefer precision over volume. Heuristic findings should be labeled as such.

## Secret exposure patterns

Inspect client-reachable code, generated bundles/config, examples, fixtures, and environment-variable usage for:

- hardcoded API keys, access tokens, database credentials, private keys, signing secrets, webhook secrets, or service credentials;
- framework prefixes that intentionally expose variables to browser/mobile bundles, such as `NEXT_PUBLIC_`, `VITE_`, `PUBLIC_`, or `EXPO_PUBLIC_`;
- privileged service credentials imported into code reachable from a client bundle;
- secrets printed in logs, errors, generated output, screenshots, or test artifacts;
- secrets copied into prompts, source comments, example payloads, or committed local config.

Do not flag intentionally publishable identifiers/keys merely because they look key-like. Determine whether the provider documents the credential as public/publishable versus privileged.

A leaked secret is not remediated by deletion alone. The remediation must include revocation/rotation at the owning provider or system when the value may have been exposed. Never echo the raw secret in findings; report type, location, and a redacted fingerprint/preview where needed.

## Client/server boundary

Generated full-stack code commonly collapses client and server assumptions. Verify:

- privileged SDK initialization is server-only;
- server-only environment values cannot be bundled to clients;
- authorization checks occur on a trusted server boundary, not only in UI state;
- database admin/service credentials do not cross into browser/mobile code;
- server routes do not simply proxy user-supplied privileged operations without authorization;
- framework markers such as client components, edge/server routes, and build-time variable substitution are interpreted correctly.

## Supabase/Postgres-style row-level authorization

When the stack uses row-level security or equivalent database policy enforcement, treat “enabled” as a claim to verify.

Check for:

- public/app tables with no applicable RLS/policy when direct client access is possible;
- blanket policies such as unconditional allow expressions;
- policies that scope access to a client-editable role/metadata field rather than authenticated identity or trusted server claims;
- use of privileged service-role credentials in client-reachable paths, which can bypass row-level controls;
- storage/object policies that unintentionally make user files globally readable/writable;
- insert/update policies that validate visibility but not ownership of new/changed rows;
- server functions/edge functions that bypass the intended row policy without equivalent authorization.

Distinguish public anonymous keys intended for client use from privileged service credentials. The public key is not itself the authorization boundary; policy enforcement is.

## Client-editable authorization claims

Do not trust privilege data a client can modify directly or indirectly, including request-body roles, arbitrary headers, or user-editable profile metadata. Authorization should derive from server-controlled identity/claims or authoritative data. When a platform distinguishes user-editable metadata from server-controlled app/role metadata, verify the privileged path uses the latter.

## LLM prompt-injection and excessive-agency sinks

Trace untrusted request/file/tool content into model calls.

Higher-risk patterns include:

- user-controlled content concatenated into system/developer/instruction text;
- a single combined instruction string that erases the data/instruction boundary;
- untrusted content influencing tool/function names, arguments, destinations, or permission decisions without validation;
- tool-enabled model calls that consume untrusted content and can cause consequential actions;
- model output passed directly into SQL, shell, templates, URLs, file paths, or external mutations without validation/authorization;
- retrieved documents or tool output treated as trusted instructions.

A safer baseline is to keep untrusted content in a clearly lower-authority data/message channel, validate/normalize it for the downstream operation, and independently authorize consequential tool actions. This reduces but does not eliminate prompt-injection risk.

Do not flag every user-role message as a vulnerability. Prompt-injection analysis is contextual and often heuristic; report confidence honestly.

## Hallucinated and unsafe generated APIs

AI-assisted code can call APIs or use configuration that looks plausible but is nonexistent, deprecated, insecure, or semantically wrong. Check:

- SDK method/type existence against the installed version or authoritative docs;
- authentication/authorization defaults;
- crypto/randomness APIs and parameter usage;
- ORM/query-builder escaping semantics;
- framework server/client boundaries;
- error handling for calls the assistant assumed cannot fail;
- dangerous “temporary” bypasses left from scaffolding;
- sample/test credentials accidentally promoted into production paths.

Use documentation research when version correctness is uncertain.

## Silent-failure patterns

Generated code often catches broadly to keep demos working. Review for:

- empty catch blocks;
- default-success responses after failure;
- authorization errors converted into generic fallback data;
- failed persistence/events ignored;
- promise/task failures not awaited or observed;
- scanner/test failures suppressed in scripts or CI;
- permissive fallback when config/secret/policy is missing.

Security controls should fail safely, with diagnosable internal evidence and non-sensitive external errors.

## Dependency and supply-chain checks

Within the inspected repository, look for:

- unpinned or unexpectedly broad dependency changes introduced by generated code;
- package names suspiciously close to expected libraries;
- runtime installation/download commands embedded in application logic or generated scripts;
- unreviewed remote script execution;
- stale/abandoned dependencies used for security-sensitive functions;
- lockfile/source-integrity inconsistencies.

This Tier 0 skill does not authorize network lookups or installations. Use governed dependency/security tooling separately when available.

## Scan → fix → rescan lifecycle

The defensible audit loop is:

1. scan/inspect the bounded source state;
2. report evidence-backed findings worst-first;
3. bind findings to stable fingerprints such as rule + path + normalized sink/source context;
4. let the governed implementation workflow apply approved fixes;
5. rescan the exact changed artifact;
6. classify each finding as resolved, still present, or newly introduced;
7. separately verify secret rotation or other external remediation that source changes cannot prove.

Never report “fixed” from an intended patch alone.

## Finding format

For each material finding include:

- severity and confidence;
- file/symbol/line where stable;
- CWE or other taxonomy mapping when it genuinely fits;
- AI/LLM-specific taxonomy mapping where relevant and current;
- source → trust boundary → sink/exploit path;
- plain-language impact;
- remediation direction;
- verification/rescan requirement.

Taxonomy mapping supports triage; it does not prove exploitability or compliance.

## Failure modes to challenge

- assuming all generated code is suspect without inspecting behavior;
- flagging public/publishable keys as secrets;
- treating “RLS enabled” as equivalent to correctly scoped policies;
- authorization based on client-editable metadata;
- deleting a leaked credential without rotation;
- printing the secret while reporting it;
- flagging all LLM user input as prompt injection;
- ignoring tool-enabled/external-action consequences of an injection path;
- claiming scanner coverage equals compliance;
- marking remediation complete without rescan;
- using a remote scanner or external service without separate authority.

## Verification questions

- Can any privileged credential reach a client/build artifact or log?
- Is every client-accessible data set protected by an authoritative authorization boundary?
- Can a user alter any claim that privileged code trusts?
- Does untrusted content reach a high-authority model instruction or consequential tool path?
- Are generated SDK/API calls real for the installed version?
- Do security failures fail closed rather than quietly returning success?
- Are findings fingerprinted so rescan can distinguish resolved/still/new?
- Were exposed credentials rotated where source inspection indicates compromise?

## Specification-to-TDD composition

For a confirmed defect, trace security requirement → attacker/user-observable failure → security invariant → owning trust boundary → smallest remediation slice → lowest defensive test capable of reproducing the failure → RED → GREEN → REFACTOR → focused security regression/rescan → independent AppSec review where needed → fresh evidence → governing repository/KIS gate. The audit itself remains advisory and read-only.