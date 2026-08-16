# Skills over MCP Catalogue Projection

## Scope

Issue #90 extends the #50 single-skill compatibility projector to the full active canonical workspace catalogue. This slice remains read-only and does not register an MCP server, activate or execute a skill, grant permissions, or create a second mutable catalogue.

Canonical source:

- `C:\Projects\.agents\skills`
- active membership/frontmatter authority is reused from `skill_catalog_dashboard.catalog.discover_catalog`
- each projected package reuses `scripts/skills_over_mcp_compat.py` identity and digest checks

## Command

```powershell
python scripts/skills_over_mcp_catalogue.py `
  --catalog-root 'C:\Projects\.agents\skills' `
  --source-snapshot-id a37081f574386b25 `
  --output '.work\mcp-catalogue\projection-live.json'
```

The KIS snapshot ID is optional runtime provenance. It is not used to calculate the deterministic content snapshot.

## Live result — 2026-08-16

- KIS `list_skills`: 38 active skills, runtime snapshot `a37081f574386b25`.
- Catalogue projection: 38 skills, 114 resources.
- Content snapshot: `2e516e2554be0fe4f4c15393fa4e417ddc40003f2a03ec1f89fd67a9fe31276c`.
- Two runs without catalogue changes produced byte-identical JSON; file SHA-256 was `822404982fa19869bf1abdc9ffe801d58d0e1bd5f9f57358899b28dd33016a3e`.
- The live output carrying KIS provenance has file SHA-256 `c880e5f5a4ba3e88426555f5b0b553fef269702d690cef7edbe518eecff4fd38` while retaining the same content snapshot.
- The serving manifest contains no local absolute catalogue path.

Projected resource classes:

| Class | Resources |
|---|---:|
| `SKILL.md` | 38 |
| `references/` | 40 |
| `assets/` | 15 |
| `agents/` | 7 |
| `scripts/` | 4 |
| other package-root files | 10 |

Every resource retains the exact source bytes and is represented as `skill://<skill-id>/<relative-path>` with a `sha256:<digest>` identity.
## Fail-closed behavior

The batch projector rejects the whole projection rather than silently omitting a package when catalogue discovery is incomplete, a package is structurally invalid, an identity/hash check fails, a linked or Windows reparse/junction path is present, or resource URIs collide case-insensitively.

The full-resource snapshot is calculated from sorted skill identity plus every projected URI/digest pair. Changes to supporting resources therefore change the content snapshot even when `SKILL.md` is unchanged.

## Automated verification

```powershell
python -m unittest tests.test_skills_over_mcp_catalogue tests.test_skills_over_mcp_compat -v
```

Focused result: **18 passed; 2 existing Windows symlink tests skipped**. The new Windows junction test passed and the existing #50 compatibility tests remained green.

Fresh full `npm run verify` result after the final fail-closed review fix: **142 tests passed; 3 Windows-specific skips**, followed by passing project-contract, compliance, catalogue-evaluation, skill-security validation, and catalog generation; overall exit code 0.

## Boundary for #91

This output is a deterministic transport projection/index only. Serving `skills/list`, `skills/get`, resources, host registration, activation, permissions, telemetry attribution, and execution remain outside #90 and belong to later programme slices or explicit KIS handoffs.
