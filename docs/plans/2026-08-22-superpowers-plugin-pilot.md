# Superpowers Plugin Pilot Plan

## Scope
Issue #88 governs the staged `superpowers` 6.2.0 bundle under `.work/niel-work/superpowers/6.2.0` as source evidence only. This change must not install, activate, execute, or runtime-expose the plugin, its helper scripts, bootstrap behavior, or bundled skills.

## Evidence decision
Treat the operator-provided staged bundle as `trusted-local` intake evidence. Bind it to the deterministic SHA-256 tree identity `a1cbc2e46d5c2709c5827fe28296a8dbcb972509e71cb3f2567295377d6f0430`, computed from sorted relative paths and file digests. The digest authenticates the staged bytes, not publisher origin. The bundle declares version 6.2.0, repository `obra/superpowers`, and MIT licensing; upstream authentication remains unobserved.

## Authority and adaptation
Repository `AGENTS.md`, KIS Work Management, repository verification/closeout, and canonical skill governance remain higher authority. Superpowers contains mandatory lifecycle rules, host-specific bootstrap/tool assumptions, executable helpers, external-mutation workflows, and optional visual-companion network telemetry. Record portable workflow value and overlap, but defer runtime evaluation until those conflicts are deliberately adapted and separately approved.

## Implementation
1. Add a `plugin` intake record linked to issue #88 and its live Work record.
2. Add one non-runtime portfolio record under `portfolio/plugins/superpowers/`.
3. Persist aggregate composition, authority, host-assumption, overlap, helper-script, and telemetry evidence.
4. Persist one static evidence record for each of the 14 bundled skills.
5. Cross-bind the intake record, portfolio record, bundle digest, composition, and per-entry evidence in tests.

## Completion
The pilot is complete when deterministic provenance/composition evidence is reviewable, all bundled skill entries are covered, validators pass, and the portfolio disposition remains `deferred` with no canonical `skills/` adoption, installation, activation, or runtime authority.
