# Security Policy

## Authority

This file defines how security concerns are reported. The authoritative implementation and adoption controls are in [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md).

## Reporting a vulnerability

Do not disclose vulnerabilities, exploit details, credentials, tokens, personal data, or sensitive repository information in a public issue or pull request.

Use the repository's **Security** tab to open a private security advisory. Include:

- the affected commit, file, skill, adapter, or configuration;
- the impact and credible attack path;
- the smallest safe reproduction;
- known preconditions and affected environments;
- suggested containment or remediation, when available.

If private advisory reporting is unavailable, contact the repository owner through an established private channel and provide only enough information to establish a secure follow-up path.

## Immediate containment

When adopted-skill provenance, validation, or runtime integrity is uncertain:

1. Set `config/runtime-control.json` to `skills_enabled: false`.
2. Do not execute candidate or reference scripts, hooks, workflows, MCP configurations, or installation instructions.
3. Preserve evidence under `.work/` without committing sensitive material.
4. Re-run `npm run verify` after remediation.
5. Record the incident, affected revision, containment, and rollback evidence.

## Scope

Security reports may cover repository-owned code and policy, skill discovery and activation, manifests and provenance, adapters, CI configuration, GitHub repository controls, or accidental exposure of sensitive material.

The imported corpus below `references/` is untrusted source evidence and is not supported as executable repository functionality.
