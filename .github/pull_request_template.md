## Purpose

Describe the customer or repository outcome this change delivers.

## Scope and authority

- [ ] The change is limited to the requested outcome.
- [ ] The applicable `AGENTS.md` and authoritative owner documents were read before editing.
- [ ] Source-derived requirements, live product verification, repository decisions, and unresolved assumptions are separated.
- [ ] Runtime-specific behavior remains behind the applicable adapter boundary.
- [ ] Each governed fact has one authoritative repository owner.

## Skill package and runtime

- [ ] Canonical skill contents follow `docs/standards/skill-package-standard.md`.
- [ ] OpenAI or other target metadata is isolated to the responsible adapter or generated package.
- [ ] Evals, governance records, generated evidence, and temporary files are excluded from runtime packages.
- [ ] No content below `references/` or `.work/` is made runtime-discoverable.

## Security and provenance

- [ ] New or changed adopted skills include valid provenance, license review, content hash, capability tier, scopes, approval, and rollback evidence.
- [ ] No credentials, secrets, personal data, unpinned runtime installation, lifecycle hooks, remote MCP, or unsupported external mutation were introduced.
- [ ] The runtime kill switch remains disabled unless the complete enablement gate is evidenced and approved.

## Evaluation evidence

- [ ] The baseline or previous accepted version is identified.
- [ ] Trigger positives, near-miss negatives, conflicts, and injection cases are covered when activation behavior changed.
- [ ] Output assertions, abuse cases, compatibility evidence, efficiency signals, and human review are recorded when applicable.
- [ ] Critical failures, unavailable metrics, residual risks, and stop criteria are explicit.

List the exact commands run and their results.

```text
npm run verify
```

## Review notes

Record remaining risks, skipped checks, assumptions, and follow-up work. Use `None` when there are none.
