# Adopted Skills

This is the only runtime discovery root.

Only direct child directories matching `skills/*/SKILL.md` are eligible. Every adopted skill also requires a valid `adoption-manifest.json` and must pass [`scripts/skill_security.py`](../scripts/skill_security.py) under the authoritative [`Skill Adoption Security Standard`](../docs/security/skill-adoption-security-standard.md).

Canonical contents follow the [`Skill Package Standard`](../docs/standards/skill-package-standard.md). Trigger, output, efficiency, abuse, compatibility, and human-review evidence follow the [`Skill Evaluation Standard`](../docs/testing/skill-evaluation-standard.md) and remain outside runtime packages.

Do not place source snapshots, experiments, nested skills, target-specific metadata, hooks, remote MCP configuration, credentials, runtime installers, evals, or generated evidence here. Use `references/` for untrusted source evidence, runtime adapters for target overlays, tests for accepted eval definitions, and `.work/` for temporary or generated work.
