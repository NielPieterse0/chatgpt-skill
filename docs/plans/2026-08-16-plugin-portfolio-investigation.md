# Plugin Portfolio Investigation Plan

## Authority and scope

GitHub issue #59 is the source specification. This change is investigation and methodology only: it may adopt repository-owned architecture/portfolio decisions, but it must not install, activate, register, or grant permissions to any plugin.

Existing authorities remain unchanged for skills, import isolation, security, evaluation, and runtime adapters. The plugin methodology must compose with them rather than duplicate them.

## Evidence basis

Use:

- repository authorities in `AGENTS.md` and the existing skill lifecycle/security/evaluation/adapter documents;
- the registered OpenAI plugin source (`OA-07`) for the product-level distinction between plugin bundles, skills, apps, app templates, installation, and app permissions;
- the currently exposed `plugin-eval` plugin skills as a bounded pilot observation only.

The current session can inspect `plugin-eval` skill instructions but cannot resolve a public Plugin Management release, an immutable upstream revision, or a local `plugin-eval` CLI executable. Those missing identities are pilot evidence and must not be filled by inference.

## Deliverables

1. Define explicit boundaries among plugin, skill, app/integration, app template, runtime adapter, and ordinary external dependency.
2. Define a non-runtime plugin portfolio record with provenance, immutable baseline, bundle contents, capabilities/permissions, evaluation, lifecycle, update, rollback, and target-support fields.
3. Define discovery-to-maintenance intake and update flows with import-isolate at the external-source boundary and installation/activation authority kept separate from portfolio acceptance.
4. Assess `plugin-eval` against the model, identify overlap/conflicts with the repository evaluation harness, and make one evidence-backed disposition.
5. Define dashboard/reporting requirements without changing current skill evaluation coverage semantics.
6. Record the current repository gaps and bounded follow-on implementation slices; do not create runtime scaffolding in this investigation.

## Acceptance

- Every requested #59 question has an explicit answer or documented evidence gap.
- The pilot has a source/provenance status, structure/capability assessment, value/overlap analysis, proposed wiring boundary, verification/evaluation plan, rollback path, update model, and disposition.
- The intake flow is auditable and prevents catalogue presence, portfolio acceptance, installation, app enablement, and activation from collapsing into one state.
- Future updates are defined as diffs from the last accepted immutable baseline.
- Documentation-only validation, `git diff --check`, and full repository verification pass before closeout.
