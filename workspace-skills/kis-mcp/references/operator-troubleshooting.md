# Operator Troubleshooting

Load this reference only for KIS startup, connection, provider authentication,
commissioning, capability mismatch, or runtime/repository drift.

## Diagnose from live layers

Check the smallest evidence layer that answers the problem:

1. runtime health for whether KIS is running and its local policy/generated state;
2. project catalogue/status for explicit target identity and bindings;
3. provider status when provider readiness or connection matters;
4. workflow/capability discovery when an expected operation is unclear;
5. capability description and the live input schema before invoking unfamiliar
   operations;
6. target repository evidence when the question concerns repository governance,
   Git state, verification, review, or completion.

Do not treat these as interchangeable. In particular:

- readiness is not authentication;
- authentication is not commissioning;
- registration/mounting is not successful execution;
- a successful operation proves that operation, not every provider layer.

## Drift and disagreement

A running KIS instance may lag the checked-out source, and documentation may lag
either one. Prefer live capability/schema evidence for what the running instance
can do and repository authority for what the target permits or requires.

When catalogue metadata, provider boundary, repository authority, and live schema
conflict, do not widen interpretation to make the call succeed. Keep the conflict
explicit and stop the disputed action until current evidence resolves it.

## Keep transient facts out

Do not add provider versions/lists/counts, current commissioning states, project
identifiers, workflow names, operation counts, detected development tools,
implementation slice numbers, or known temporary defects here. Those facts should
come from the live runtime, repository docs, or issue tracking.