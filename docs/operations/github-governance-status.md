# GitHub Governance Status

## Authority and Purpose

[`github-repository-hygiene.md`](github-repository-hygiene.md) remains the repository-owned policy. This file records the observed provider state and any external enforcement limitation; it does not weaken or replace that policy.

## Verified State — 2026-08-14

Repository: `NielPieterse0/chatgpt-skill`

Observed through the authenticated GitHub integration:

- visibility: private;
- default branch: `main`;
- issues: enabled;
- wiki: disabled;
- squash merge: enabled;
- merge commits: **enabled — noncompliant**;
- rebase merge: **enabled — noncompliant**;
- delete branch on merge: **disabled — noncompliant**;
- automatic merge: disabled;
- repository Projects feature: enabled; shared Work Management Project usage is separately accepted by the repository contract.

The integration returned `403 Resource not accessible by integration` for the `main` branch-protection endpoint. Therefore required-pull-request enforcement, required `verify` status checks, conversation resolution, linear-history enforcement, force-push/deletion restrictions, and administrator enforcement could not be read or changed through the connected provider in this session.

## Mutation Boundary

The registered KIS operation `kis_github_configure_registered_repository` is **not permitted for this repository policy**. Its implementation enforces merge-commit-only landing (`allow_merge_commit=true`) and disables automatic branch cleanup, which conflicts with the repository-owned squash-only policy. Do not invoke it to close this governance gap.

The connected GitHub capability surface available to this project exposes repository settings as reads but does not expose a bounded repository-settings or branch-protection mutation matching this policy. Local `gh` is intentionally unauthenticated outside KIS-managed state, and no credential bypass or unrestricted command path is authorized.

## Required External Resolution

Change 007 is externally blocked until one of these bounded capabilities becomes available:

1. a GitHub connector operation that can set repository merge flags and branch protection/rulesets; or
2. a revised KIS registered-repository governance operation whose declared policy matches this repository.

When the capability exists, apply and re-read these exact controls:

- `allow_squash_merge=true`;
- `allow_merge_commit=false`;
- `allow_rebase_merge=false`;
- source branches deleted after merge where supported;
- `main` changes require pull requests;
- required status check: `verify`;
- review conversations resolved;
- required approving reviews: `0` while this remains a single-owner repository;
- linear history required;
- force pushes disabled;
- branch deletion disabled;
- administrators subject to the same rules except explicit incident-containment bypass.

Do not mark these controls implemented until the live GitHub state is re-read and verified.

## Disposition

**BLOCKED-EXTERNAL / CLOSED AS PROVIDER LIMITATION.** Repository policy is unchanged. No incompatible or weaker mutation was applied. Reopen governance enforcement when a bounded compatible provider operation becomes available.
