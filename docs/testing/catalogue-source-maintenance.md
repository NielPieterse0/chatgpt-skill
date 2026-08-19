# Catalogue Source Maintenance

Issue #83 adds a read-only review trigger for repository-sourced and snapshot-sourced catalogue skills. It does not synchronize source content into the canonical workspace and it does not mutate source repositories.

## Authority

- Repository adoption manifests preserve original provenance and adopted repository content identity.
- `config/catalogue-source-maintenance/*.json` records the latest reviewed source/workspace baseline after a delta is explicitly classified.
- `C:\Projects\.agents\skills` remains the canonical workspace catalogue.
- Source repositories are observations only after adoption; source changes never overwrite accepted local content automatically.

## Run a comparison

```powershell
python scripts/catalogue_source_delta.py `
  --repo . `
  --catalog-root 'C:\Projects\.agents\skills' `
  --source-repo 'https://github.com/example/upstream-skill-source.git=C:\path\to\source-checkout' `
  --output '.work\source-delta\report.json'
```

Use an explicit `--source-repo URL=PATH` mapping for each locally available source repository. The command reads the current local Git `HEAD`; it does not fetch, pull, checkout, reset, or otherwise mutate the source repository.

Run this check when a mapped source repository revision advances, when a source skill snapshot changes, or before a planned adopted-skill refresh.

## Review semantics

For adoption manifests, the report distinguishes source revision state from current workspace identity. A source package can be removed while an accepted local successor remains valid. Workspace divergence from a historical adoption manifest is therefore review evidence, not an automatic defect or sync instruction.

For `config/catalogue-skill-updates/*.json`, machine-readable source snapshots are compared against the current canonical source-skill packages. A changed snapshot triggers review even when the target adopted skill itself has not changed.

Every material delta must be classified as `adopt`, `adapt`, `defer`, `not-applicable`, or `preserve-local`. Recheck portability, trigger overlap, progressive disclosure, security, references/scripts, and relevant behavioral evidence before accepting a target-content change.

After review, record the accepted next baseline in `config/catalogue-source-maintenance/`. The next run uses that reviewed source revision/workspace hash or source-snapshot hash; already-classified changes therefore stop alerting until new evidence appears.

## 2026-08-16 review

The first live comparison found three review triggers:

- `develop-code`: KIS removed `.agents/skills/develop-code` at `a5bf3bdd779fb5f998ae6cf1f8741db58dabe3b8`; disposition `preserve-local`.
- `develop-docs`: KIS removed `.agents/skills/develop-docs` at `52afc899175cd5cafe1928b0cd67e28bee5f30e4`; disposition `preserve-local`.
- `kis-mcp` source baseline: `mcpb-local-packaging` gained `references/local-security.md` and `references/manifest-schema.md`; disposition `not-applicable` to the KIS operational skill.

The `develop-code` and `develop-docs` workspace packages are accepted successors from issue #40, which remediated and restored those packages to the canonical workspace. KIS's later removal of its repository-local skill catalogue does not revoke that accepted state.

The recorded next baseline is `config/catalogue-source-maintenance/2026-08-16.json`. Immediately rerunning the comparison against KIS revision `9adf1ca26a6a96a173605a7e5dd5c11216d6ec0e` and the current workspace produced:

- adoption-manifest baselines: 2 tracked;
- catalogue-refresh baselines: 1 tracked;
- review due: 0;
- not observable: 0.

No automatic sync, source mutation, workspace mutation, or KIS catalogue refresh was performed by this maintenance review.
