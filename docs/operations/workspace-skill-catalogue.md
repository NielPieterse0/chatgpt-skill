# Workspace Skill Mirror and Canonical Catalogue

## Authority

This document owns synchronization between the tracked runtime mirror in this repository and the canonical Projects workspace catalogue at `C:\Projects\.agents\skills`.

The invariant is deliberately simple:

- `workspace-skills/` is committed on `main` and is the local runtime mirror.
- `C:\Projects\.agents\skills` must contain the same runtime skill bytes.
- `skills/` remains the repository-owned package source for adopted skills and may contain repository-only files such as `adoption-manifest.json`.
- For every repository-owned skill, its runtime projection in `workspace-skills/` must match `skills/<name>/` after repository-only files are removed.

A skill-changing pull request is incomplete if it updates `skills/` without the matching tracked runtime mirror change.

## Commands

Refresh repository-owned entries in the tracked mirror before committing a skill change:

```powershell
npm run sync-workspace-mirror
```

Publish the committed mirror to the canonical workspace catalogue:

```powershell
npm run sync-workspace-catalogue
```

Verify repository-owned mirror parity and, when the canonical Windows path is available, full mirror-to-catalogue parity:

```powershell
npm run verify-workspace-mirror
```

`npm run verify` includes the mirror verification gate. CI therefore rejects a skill change whose tracked runtime mirror was not updated.

## Automatic Local Synchronization

`.githooks/post-merge` and `.githooks/post-checkout` publish `workspace-skills/` whenever the active local branch is `main`.

Configure hooks once per checkout with:

```powershell
npm run setup-hooks
```

This means a local checkout of accepted `main` immediately reconciles the canonical workspace catalogue from tracked repository state. Remote GitHub merges do not need a separate remembered publication action; the next local main checkout or merge runs the synchronization automatically.

The publisher refuses untracked canonical-only skill directories rather than silently deleting them. Such drift must be reconciled into `workspace-skills/` deliberately.

## Safety and Ownership

`workspace-skills/` contains runtime payloads only. Repository governance metadata stays under `skills/`.

Do not manually edit `C:\Projects\.agents\skills` to make parity pass. Change the tracked mirror, or change the repository-owned package and refresh its mirror projection, then let the deterministic publisher update the canonical catalogue.
