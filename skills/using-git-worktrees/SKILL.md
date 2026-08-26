---
name: using-git-worktrees
description: Use when feature or plan work needs an isolated Git workspace, when verifying whether isolation already exists, or when selecting the repository-authorized worktree workflow before implementation.
license: MIT
---

# Using Git Worktrees

Use isolation to protect unrelated work and make change ownership explicit. Preserve the source skill's detect-first discipline without creating a second Git or KIS authority.

## Detect existing isolation first

Before creating anything, inspect repository evidence to determine whether the current checkout is already an isolated linked worktree, a detached managed workspace, a normal checkout, or a submodule. Do not infer isolation from the directory name alone.

If existing isolation is valid for the current change, reuse it. Record its branch or detached state rather than nesting another worktree.

## Select the repository-authorized path

1. Read repository instructions and determine whether the repository is KIS-managed.
2. For KIS-managed work, load `kis-mcp`, discover the current isolated-development or worktree capability, and use that governed workflow. Do not fall back to manual Git merely because it is familiar.
3. For non-KIS repositories, prefer a runtime-native worktree facility when the repository permits it; otherwise follow the repository's documented Git procedure and explicit user authorization.
4. If a repository-local worktree directory is used, prove it is excluded from normal source tracking before creating isolation.
5. Preserve branch naming, placement, cleanup, and ownership conventions defined by the repository or runtime.## Establish a clean baseline

After entering the authorized isolated workspace, run only the setup needed by the repository and then run its baseline verification before implementation. Do not install arbitrary or unpinned dependencies just because the upstream skill listed generic setup commands.

If the baseline fails, distinguish pre-existing failure from the requested change. Follow repository policy for whether work may proceed; do not hide the failure or later claim the branch started clean.

## Cleanup

Worktree cleanup belongs after the repository's integration or retention decision. In a KIS-managed repository, let the live KIS/github-delivery workflow prove that the workspace is clean, merged or otherwise eligible, and safe to remove.

## Red flags

- Creating another worktree before checking existing isolation.
- Treating a submodule as a linked worktree.
- Bypassing a native or KIS workflow with raw Git commands.
- Creating a project-local worktree under a tracked directory.
- Skipping baseline verification because the workspace is new.
- Removing isolation before landing or retention state is independently known.

## Boundaries

This skill supplies isolation selection and verification method. It does not authorize branch creation, Git publication, merging, destructive cleanup, or external mutation. Repository authority and live KIS schemas govern those effects.