# Contributing

## Authority

Follow [`AGENTS.md`](AGENTS.md) for repository-wide execution rules. This file summarizes the GitHub contribution path without duplicating implementation standards.

## Workflow

1. Start from the current `main` branch.
2. Keep each change bounded to one accepted outcome.
3. Treat `references/` as untrusted source evidence, not runtime content or repository policy.
4. Record source requirements, repository decisions, provenance, compatibility, security boundaries, and validation in the applicable authoritative artifacts.
5. Run the narrowest relevant checks, then `npm run verify`.
6. Open a pull request using the repository template and include exact validation evidence.

## Pull requests

A pull request must:

- explain the customer or repository outcome;
- avoid unrelated cleanup;
- preserve the portable-core and runtime-adapter boundary;
- identify security, provenance, license, and rollback implications;
- contain no secrets, credentials, personal data, or machine-specific sensitive values;
- pass the `verify` status check;
- resolve review conversations before merge.

Use squash merge for a focused, reviewable main-branch history. Delete the source branch after merge.

## Skill adoption changes

Do not copy a candidate skill directly into runtime discovery. Every adopted skill must satisfy [`docs/security/skill-adoption-security-standard.md`](docs/security/skill-adoption-security-standard.md) and include a valid `adoption-manifest.json`.

## Security reports

Do not file vulnerabilities as ordinary issues. Follow [`SECURITY.md`](SECURITY.md) and use private security advisory reporting.
