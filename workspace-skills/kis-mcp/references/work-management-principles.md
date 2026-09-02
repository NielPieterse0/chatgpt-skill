# Work Management Principles

Load this reference only when governed work is being created, changed,
reconciled, claimed, deferred, held, released, or completed.

## Authority model

Work Management uses field-level authority.

- The source issue or pull request owns identity and repository-owned narrative
  according to the target repository's authority.
- The configured Project/work backend owns command fields such as lifecycle and
  execution direction when the repository delegates those fields to it.
- Git, GitHub, Actions, review, and other evidence sources remain authoritative
  only for the fields the repository assigns to them.
- Derived state remains derived; do not turn it into a second command source.

Never synchronize by copying Project-owned command metadata into issue prose.
That creates competing authorities instead of reconciliation.

## Safe operating pattern

1. Resolve the target repository/project explicitly.
2. Read the target repository's work-management/change-governance rules.
3. Search existing source records and bounded inventory before creating work.
4. If inventory is incomplete or truncated, preserve that limitation and search
   the authoritative source before concluding that no record exists.
5. Use the live Work Management contract/schema for current fields and actions.
6. Apply the mutation through the authority that owns the field.
7. Re-read the authoritative source after mutation.
8. Record only evidence actually established by the operation.

## Completion discipline

Do not equate implementation completion with work completion. Use the target
repository's current required evidence for verification, review, merge, docs,
approvals, holds, or other gates.

Do not freeze these runtime facts into this reference:

- Project IDs, field/view counts, record prefixes, or status option sets;
- exact transition maps or merge-readiness models;
- current workflow/operation names or operation counts;
- current commissioning state or known transient defects.

Discover those facts from the live contract, current project status, and target
repository authority.