# Plugin dashboard projection plan

## Scope

Issue #76 adds a read-only projection of validated `portfolio/plugins/*/plugin-record.json` records to the existing workspace dashboard. Plugin records remain a separate population from canonical skills, intake candidates, and runtime state.

## Design

- Reuse `scripts/plugin_portfolio.py` as the repository acceptance gate; do not create a second validator.
- Load plugin rows only when the complete portfolio validates. If validation fails, expose the portfolio source as invalid with bounded warnings and project no unvalidated records.
- Add plugin summary counts without changing `total_catalogue_count`, `repo_evaluated_count`, `evaluation_coverage`, or other skill mathematics.
- Project immutable source/version identity, lifecycle/provenance/evaluation/update state, components, capabilities, dependencies, targets/app-access observations, evidence paths, and provided-skill cross-links.
- Treat update-check age as derived display data only; preserve `null` when no check date is recorded.
- Expose plugin rows in JSON and HTML only. Do not add mutation, install, activation, app-authorization, or control-plane actions.

## Verification

Use temporary valid and invalid plugin fixtures to prove population separation, source failure behavior, target/app observability, update deltas, skill cross-links, deterministic JSON, and the read-only web surface. Then run the full repository verification gate.