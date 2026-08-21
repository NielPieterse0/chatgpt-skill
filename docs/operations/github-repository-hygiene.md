# GitHub Repository Hygiene

## Authority

This document defines the accepted GitHub repository operating state. `AGENTS.md` governs how work is performed; repository security implementation remains governed by `docs/security/skill-adoption-security-standard.md`.

## Repository state

| Control | Required state |
| --- | --- |
| Visibility | Private |
| Default branch | `main` |
| Repository owner | `NielPieterse0` |
| Local remote | `https://github.com/NielPieterse0/chatgpt-skill.git` |
| Merge strategy | Squash merge only |
| Source branches | Delete after merge |
| Wiki | Disabled |
| Work Project | User Project `NielPieterse0/1` required as the KIS Work Management projection for repository issues |
| Issues | Enabled for defects and skill candidates |
| Vulnerabilities | Private security advisories; never ordinary issues |
| Actions token | Read-only by default; workflow permissions narrowed further in each workflow |

## Main-branch controls

`main` should enforce the following when the GitHub plan and repository settings support them:

- changes arrive through pull requests;
- the `verify` status check passes before merge;
- review conversations are resolved;
- force pushes and branch deletion are blocked;
- linear history is required;
- administrators follow the same rules, with emergency bypass used only for incident containment.

For a single-owner repository, required approving review count may remain zero until another accountable reviewer is assigned. This preserves operability while still enforcing pull-request and CI evidence.

## Repository-owned GitHub files

- `.github/workflows/verify.yml`: required repository verification on pushes and pull requests.
- `.github/CODEOWNERS`: ownership for repository and security-critical paths.
- `.github/pull_request_template.md`: scope, security, provenance, and validation evidence.
- `.github/ISSUE_TEMPLATE/`: structured defect and skill-candidate intake.
- `.github/dependabot.yml`: weekly GitHub Actions update proposals.
- `SECURITY.md`: private vulnerability reporting and immediate containment.
- `CONTRIBUTING.md`: contribution and merge workflow.

## Closeout checklist

1. Fetch and prune `origin`.
2. Confirm the working tree is clean and `main` matches `origin/main`.
3. Run `npm run verify`.
4. Run `git diff --check`.
5. Confirm the `Verify` workflow succeeded for the accepted commit.
6. Reconcile all open `NielPieterse0/chatgpt-skill` issues into Work Project `NielPieterse0/1`, verify the current KIS metadata contract, and block closeout on missing items, stale dependencies, or metadata drift. Retain closed issues in the Project as history.
7. When the accepted commit adds or changes `skills/*`, synchronize those merged packages to the canonical workspace catalogue and verify discovery according to [`workspace-skill-catalogue.md`](workspace-skill-catalogue.md).
8. Confirm repository visibility, default branch, remote identity, and administrative access.
9. Confirm no stale pull requests, branches, failed workflow runs, or generated artifacts require action.
10. Confirm the runtime kill switch remains disabled unless an adopted skill has passed admission and explicit enablement.

## Exceptions

Document any unavailable GitHub setting, plan limitation, skipped check, or temporary bypass in the closeout report. Do not describe an unavailable control as implemented.

Current live governance verification and provider limitations are recorded in [`github-governance-status.md`](github-governance-status.md). That status record must never be used to weaken the required state above.
