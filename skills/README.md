# Adopted Skills

This is the only runtime discovery root.

Only direct child directories matching `skills/*/SKILL.md` are eligible. Every adopted skill also requires a valid `adoption-manifest.json` and must pass [`scripts/skill_security.py`](../scripts/skill_security.py) under the authoritative [`Skill Adoption Security Standard`](../docs/security/skill-adoption-security-standard.md).

Do not place source snapshots, experiments, nested skills, hooks, remote MCP configuration, credentials, or runtime installers here. Use `references/` for untrusted source evidence and `.work/` for temporary work.
