# Workspace Skill Catalogue Publication

## Authority

This document owns publication from accepted `chatgpt-skill` repository state into the canonical Projects workspace catalogue at `C:\Projects\.agents\skills`.

Canonical skill content, security admission, evaluation, and runtime mapping remain owned by their existing authorities. This document governs only the post-merge delivery step.

## Required State

- `skills/<skill-name>/` in accepted `origin/main` is the publication source.
- `C:\Projects\.agents\skills\<skill-name>` is the workspace delivery destination.
- Repository branches, worktrees, uncommitted files, generated packages, and `references/` are never publication sources.
- The shared catalogue remains read-only for assessment and candidate discovery. The only routine write exception is this controlled post-merge publication path.
- Never edit a published workspace skill manually to reconcile drift. Resolve the divergence deliberately before publishing again.

## Publication Command

After a merge that adds or changes a canonical skill, refresh `origin/main`, then run:

```powershell
python scripts/sync_workspace_catalogue.py --repo . --source-ref origin/main
```

To repair or explicitly republish one accepted skill:

```powershell
python scripts/sync_workspace_catalogue.py --repo . --source-ref origin/main --skill <skill-name>
```

Use `--dry-run` before a stateful run when investigating drift.

## Safety Model

The synchronizer:

1. resolves the requested source commit and requires it to equal local `refs/remotes/origin/main`;
2. reads package bytes from the accepted Git object tree rather than the current working tree;
3. publishes only direct `skills/<skill-name>` packages containing both `SKILL.md` and `adoption-manifest.json`;
4. creates a missing destination safely;
5. treats an already identical destination as an idempotent no-op;
6. updates an existing destination only when it exactly matches the skill from the previous accepted main commit;
7. blocks on catalogue drift instead of overwriting unknown content;
8. blocks repository-side skill deletion instead of deleting the workspace catalogue automatically;
9. preflights all selected skills before making any write.

This makes repository main the publication authority without turning the workspace catalogue into an unrestricted write surface.

## Post-Merge Gate

A skill-changing issue or pull request is not complete at merge time. Closeout requires all of the following:

1. the accepted merge commit is present in `origin/main`;
2. repository verification for that exact commit succeeds;
3. the synchronizer succeeds for every skill added or changed by the accepted commit;
4. KIS or the active workspace skill surface can discover the synchronized skill at the expected content;
5. any publication conflict, deletion request, or unavailable discovery check is recorded as an explicit blocker rather than reported as complete.

For a newly adopted skill, failure to reach the workspace catalogue is a release failure, not a documentation follow-up.

## Local Git Hook

`.githooks/post-merge` is a local safety net for merges or pulls performed in a checkout of `main`. Configure it with:

```powershell
git config --local core.hooksPath .githooks
```

The hook does not replace the post-merge gate. GitHub-side merges happen remotely and therefore do not execute a local repository hook. Agents must still run the publication command during remote-merge closeout.

## Failure Handling

- **Branch-only source:** stop; refresh accepted main and retry.
- **Catalogue drift:** stop; compare the destination with current and previous accepted repository state. Do not force overwrite.
- **Skill deletion:** stop; retirement requires a separate explicit, reversible decision.
- **KIS discovery lag:** refresh or restart the runtime and recheck. If the package is present but still not discoverable, record the runtime defect separately.
- **Unavailable catalogue path:** treat publication as blocked. Do not close the skill work as complete.
