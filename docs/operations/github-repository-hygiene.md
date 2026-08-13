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
| Projects | Disabled unless an accepted workflow requires them |
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
6. Confirm repository visibility, default branch, remote identity, and administrative access.
7. Confirm no stale pull requests, branches, failed workflow runs, or generated artifacts require action.
8. Confirm the runtime kill switch remains disabled unless an adopted skill has passed admission and explicit enablement.

## Exceptions

Document any unavailable GitHub setting, plan limitation, skipped check, or temporary bypass in the closeout report. Do not describe an unavailable control as implemented.
