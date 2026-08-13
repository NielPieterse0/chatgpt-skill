# Workflow Draft Disposition

## Decision

- `develop-code`: **superseded/redundant**. Its eight portable files match both the current Projects workspace skill and the admitted canonical package on `main`; the canonical package additionally has its repository adoption manifest.
- `develop-docs`: **superseded/redundant**. Its nine portable files match both the current Projects workspace skill and the admitted canonical package on `main`; the canonical package additionally has its repository adoption manifest.
- `tdd-change-discipline`: **not admitted for this repository**. The current draft matches the Projects workspace skill, but its mandatory execution contract does not match this repository.

The ignored `.work/draft-skills/` copies remain inert evidence. This disposition does not change the Projects workspace skill library or runtime state.

## Evidence

Normalized portable inventory hashes:

- `develop-code`: `463e9b5c023c963282367b57e23a599def9e9d0033f1dd9aa8c5f8cd23fced21`
- `develop-docs`: `3817eddf370738acac70bbf381ae3e0062b3ac69e093b40b6be3c9275606b011`
- `tdd-change-discipline`: `80593b08314b9735611cd2c97314d702ccbc11836d815b425a189e586b64ba42`

KIS structural evaluation of the current workspace `tdd-change-discipline` skill reported four supported files, 13,122 bytes, and entrypoint SHA-256 `062aacdee0230ffa91e7a778dc62add66fb3fdc07a2b64f5672ae809926bd9b9`.

The current TDD draft requires `python scripts/verify.py`, `governance/quality-gates.json`, `governance/principles.json`, `docs/adr/`, `codex/<scope>-<slug>` branches, and Codex-specific metadata. None of the four required repository paths exists here. This repository uses `npm run verify` plus KIS Work Management and registered isolated worktrees. Admitting the draft unchanged would create conflicting completion and branch rules.

Any future repository-specific TDD skill must be treated as a new adapted candidate against the actual KIS/npm contract and pass the normal admission/evaluation process.

## Runtime

Runtime remains globally disabled. `develop-code` and `develop-docs` remain the canonical admitted workflow skills, and `tdd-change-discipline` remains outside canonical `skills/`.
