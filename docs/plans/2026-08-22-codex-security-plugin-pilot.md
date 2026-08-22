# Codex Security Plugin Pilot Plan

## Scope

Issue #87 governs the prepared local bundle at `.work/niel-work/codex-security/0.1.15` as source evidence only. This change must not install, activate, execute, or runtime-expose the plugin, its MCP server, apps, scripts, or skills.

## Evidence decision

Treat the user-prepared staged bundle as `trusted-local` intake evidence. Bind it to a deterministic SHA-256 tree identity computed from each sorted repository-relative path and the SHA-256 of that file's bytes. This is the immutable candidate identity for this pilot, not an asserted upstream Git commit.

Record the manifest-declared owner, version, canonical source URI, and proprietary license terms as claims observed in the staged bytes. The bundle digest authenticates those local bytes only; no upstream signature, release attestation, or authenticated acquisition record is present, so upstream source authentication remains unobserved and portfolio `source_status` remains `unverified`. Keep plugin portfolio acceptance separate from runtime installation and activation.

## Implementation

1. Add a `plugin` intake record for `codex-security`, linked to issue #87 and the live Work record.
2. Add one non-runtime portfolio record under `portfolio/plugins/codex-security/`.
3. Persist an aggregate static assessment and one evidence artifact for each bundled skill entry.
4. Cross-bind the intake record, portfolio record, bundle digest, composition, and per-entry evidence in tests.
5. Defer runtime evaluation because the bundle declares a Node MCP server, credential-bearing environment variables, external apps, process execution, network use, and external mutation surfaces.

## Completion

The pilot is complete when provenance/composition evidence is deterministic and reviewable, every bundled skill has an evidence artifact, repository validators pass, and both intake and portfolio state remain non-runtime with installation/activation disabled or unobserved. No canonical `skills/` entry is created by this change.
