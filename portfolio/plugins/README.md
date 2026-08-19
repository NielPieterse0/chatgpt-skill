# Plugin portfolio records

This is a **non-runtime, non-discovery** repository surface for governed plugin portfolio records.

Each recorded plugin uses exactly one path:

`portfolio/plugins/<plugin-id>/plugin-record.json`

The record owns plugin-bundle identity, composition, provenance, lifecycle state, target observations, evaluation evidence, update baseline, and rollback metadata. It does not install, enable, activate, connect, or execute a plugin or app.

Validate all records with:

```powershell
python scripts/plugin_portfolio.py validate --repo .
```

`schemas/plugin-portfolio-record.schema.json` defines the portable structural shape. `scripts/plugin_portfolio.py` is the authoritative repository acceptance gate and additionally enforces semantic constraints that JSON Schema does not express cleanly: unique dependency/target/app identities, safe repository-relative paths, link/junction rejection, provenance handoff binding, verified-source completeness, accepted evaluation/review/update/rollback gates, and target activation consistency.

External web/GitHub acquisition remains owned by `import-isolate`; a finalized handoff is required before an `import-isolate` source can be recorded as verified. Per `docs/architecture/import-isolate-handoff.md`, this repository records and validates the received finalized handoff identity (`case_id`, artifact name, and artifact SHA-256); the upstream inspection/review evidence and process remain authoritative in `import-isolate` and are intentionally not duplicated here. `handoff_pending` remains a valid pre-verification state.

Portfolio acceptance remains separate from target installation, activation, and app-access authority.
