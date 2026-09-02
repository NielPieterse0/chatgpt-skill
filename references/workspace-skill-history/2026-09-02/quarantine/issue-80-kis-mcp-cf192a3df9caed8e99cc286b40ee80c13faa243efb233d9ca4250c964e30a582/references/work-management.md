# Work Management

## Load when

Read this reference whenever a governed project uses KIS Work Management and the
task creates, updates, reconciles, reviews, blocks, links, verifies, documents,
or completes tracked work.

Use it for source issues/pull requests, shared Project projection, lifecycle
status, sub-issue hierarchy, traceability, and documentation closeout. Do not
load it for ordinary untracked file reads or one-off local actions that create no
durable work item.

## Authority model

Work Management uses **field-level authority**. It is neither a universal mirror
of repository state nor a replacement for repository authority.

Use these layers:

1. the target repository's `AGENTS.md` and authoritative documents govern
   repository content, implementation process, and acceptance criteria;
2. the source issue/PR preserves GitHub identity, outcome, acceptance criteria,
   discussion, and native hierarchy required by that repository;
3. the configured Work Management backend is authoritative for command-direction
   Project fields, lifecycle state, execution ownership, and provider-native
   Project revisions;
4. repository change records, Git, GitHub, and GitHub Actions remain authoritative
   for their declared evidence fields;
5. derived KIS views such as board projections and delivery-stage calculations
   are operational evidence, not a new persistence authority.

Do not copy a command field into an issue body just to create a second source of
truth. Do not overwrite repository/Git/GitHub/Actions evidence from a stale
Project value. When the direction is uncertain, inspect the live
`project_management_contract`, command-plane settings/schema, and operation
metadata before mutating anything.

## Field authority directions

Current command-plane settings classify fields by direction. Treat the live
contract as authoritative if this list changes.

| Direction | Current field families | Authority |
|---|---|---|
| `command` | Status, Record Type, Priority, Effort, Execution Owner, Review Trigger, Target Date, Iteration, Origin, Disposition, Severity, Confidence, Source Review, External Link | Work Management backend |
| `handoff` | Documentation Impact, Module | `work_management_then_repository_change`: Work Management first, then repository change when the handoff is established |
| `evidence` | Change ID, Complexity, Risk Triggers | Repository change record |
| `evidence` | Authority Revision | Git |
| `evidence` | Verification | GitHub Actions |
| `evidence` | Created, Blocked By, Repository | GitHub |
| `evidence` | Project ID, Delivery Stage | Derived |

This split matters more than the physical surface holding a value. Preserve the
configured authority/direction even when a provider exposes the same concept in
multiple places.

## Intake, resume, and next-work routine

For material work when the target repository requires Work Management:

1. Resolve the stable KIS `project_id` and exact source repository.
2. Search the source repository and bounded Work inventory for an existing issue
   representing the same outcome. Do not duplicate it; do not infer absence from
   a truncated inventory.
3. Keep the source issue concise and repository-owned. Include the required
   outcome/acceptance content and other repository-required narrative, but do not
   duplicate Work Management command fields into the issue body.
4. Prefer the advertised `capture-project-work` workflow for new intake or
   `reconcile-project-state` for drift. Inspect live schema/options before writing
   command fields.
5. To resume work already claimed by an execution owner, use
   `project_management_current_work`; it must not reacquire or rewrite the claim.
6. To select and claim the next eligible item, prefer `take-next-project-work` /
   `project_management_take_next_work`. Let the live command plane enforce Ready
   eligibility, dependency/readiness gates, deterministic ranking, and claim
   conflict handling rather than reproducing queue logic manually.
7. After a local governed change exists, use
   `project_management_sync_change_classification` to project its authoritative
   Change ID, Complexity, Risk Triggers, and change-created delivery stage.
8. Re-read the exact item after mutation and verify source identity, revision,
   lifecycle state, and execution ownership from the configured backend.

For manual reconciliation fallback, preview first and apply only with a stable
idempotency key plus current observed revision/evidence.

## Project schema and compatibility

Do not hard-code a historical field/view count or assume the Project schema is
commissioned merely because operations are mounted.

Before writing Project fields:

- use `project_management_schema_status` / `project_management_schema_plan` and
  current inventory evidence when schema state matters;
- use only field names, option values, transitions, and authority directions the
  live command plane currently declares;
- keep command fields in Work Management, handoff fields in their declared
  transition, and evidence fields sourced from their external authority;
- report schema/view drift explicitly;
- never bypass a provider gap with unrestricted GraphQL, guessed field IDs, or
  invented status options.

If schema status is unavailable or mismatched for the resolved managed project,
continue only with directly observed fields/operations whose authority and
revision are explicit, and report the missing schema evidence. Never substitute
another project's schema identity as a workaround.

Do not manually map legacy status labels into the current lifecycle unless the
live contract explicitly supplies that mapping. Prefer
`project_management_transition_work` and the dedicated hold/defer/release/complete
operations so transition legality and required command metadata are enforced by
KIS rather than copied into prompt logic.

## Reconciliation contract

The task-level operation uses this shape:

```json
{
  "project_id": "<project-id>",
  "desired": [
    {
      "record_id": "SPEC-009",
      "fields": {"Status": "<live-supported-status>"},
      "expected_revision": "<observed-revision-if-required>",
      "source_repository": "<owner>/<repo>",
      "source_number": 13,
      "source_kind": "issue"
    }
  ],
  "observed": [],
  "supported_fields": ["Status"],
  "apply": false
}
```

Rules:

- `record_id` uses a stable upper-case prefix and number.
- `source_repository`, `source_number`, and `source_kind` are supplied together.
- `source_kind` is `issue` or `pull_request`.
- `supported_fields` comes from current provider/schema evidence, not the desired
  manifest alone.
- for existing items, derive `observed`, `external_id`, fields, and revision from
  current inventory rather than fabricating them;
- preview first; do not skip directly to apply;
- apply requires a non-empty idempotency key; reuse a key only for the exact same
  command payload. If a conflict forces you to refresh observed revision/evidence
  and rebuild the command, use a new key for that revised command even when the
  business intent is unchanged;
- treat conflict, inaccessible, unsupported, orphaned, or truncated outcomes as
  evidence requiring correction, not permission to overwrite.

## Lifecycle and command-state maintenance

Keep Work Management current at meaningful transitions, not after every tool
call. Prefer the advertised `manage-project-work-state` workflow and its bounded
operations over manually reconstructing lifecycle rules.

Use the live command plane to choose legal transitions. In particular:

- `project_management_transition_work` handles ordinary declared state changes;
- `project_management_hold_work` and `project_management_defer_work` enforce the
  required review-trigger metadata;
- `project_management_release_work` returns held/deferred work according to the
  current transition contract;
- `project_management_complete_work` is the guarded terminal transition and must
  not bypass verification, merge, documentation, approval, or hold evidence.

Status and disposition are Work Management command fields. Verification is
GitHub Actions evidence and must not be manually rewritten to make a transition
pass. Source issue comments may record concise progress, blockers, and next
steps, but comments are history/evidence rather than lifecycle authority.

After each material command mutation, re-read the exact Project item and confirm
its current revision, lifecycle state, execution owner, and relevant command
metadata. If the result conflicts, truncates, or cannot prove the intended state,
stop rather than overwriting newer evidence.

## Child issues and newly discovered work

Do not bury an independently actionable defect, finding, risk, decision,
assumption, or follow-up inside a parent comment.

When new bounded work appears:

1. search for an existing source issue first;
2. create or update the child with its repository-required outcome, acceptance
   criteria, and context, without copying Project-owned command fields into the
   issue body;
3. identify the parent in the child body when repository convention requires it;
4. use `github_sub_issue_write` to create the native parent/sub-issue relation
   when the provider exposes it;
5. capture/reconcile the child through Work Management with its own stable source
   identity, then set command fields through the configured backend;
6. add concise parent history only when it helps explain why the work was split;
7. preserve the parent's lifecycle based on its own acceptance criteria; child
   creation or completion does not implicitly change the parent command state.

Use native hierarchy rather than only textual `Parent: #N` when available. If a
native relation cannot be written, retain the textual relation and report the
provider limitation explicitly.

## Review, verification, and closeout

For change-backed work, preserve the authority of each layer rather than forcing
all state into one surface.

- Prefer the advertised `verify-change-traceability` workflow /
  `project_management_verify_traceability` at the lifecycle stage required by
  the repository.
- Before a managed PR lands, use `project_management_merge_readiness` with the
  exact PR/head evidence. Provider-native exact-head GitHub Actions remains the
  verification authority and landing gate when required.
- For one Work-managed PR, prefer `complete-work-managed-pull-request`; for a
  queued landing, prefer the advertised `complete-work-managed-merge-queue`.
  These compose command-state readiness with exact-head/queue evidence rather
  than weakening either authority.
- Classify Documentation Impact during intake. After landing, use
  `project_management_documentation_reconcile` when documentation is required
  and keep completion gated until the exact `post_merge_complete` evidence exists.
- Use `project_management_complete_work` only after the live completion gate says
  terminal transition is valid. Closing the GitHub issue is not, by itself,
  evidence that the Work Management item is Done, and setting Done must not
  fabricate Actions or documentation evidence.

## Status-update content

A useful progress comment is brief and evidence-based:

```text
Status update — Verification

Completed:
- <bounded implemented/reviewed outcome>

Evidence:
- <exact test, revision, provider result, or link>

Open:
- <blocker/risk/child issue, or "none">

Next:
- <next lifecycle action>
```

Do not paste large logs into status comments. Link or summarize exact evidence.

## Gotchas

- GitHub issue custom fields and GitHub Project fields are separate surfaces;
  discover each schema before writing it.
- `project_management_inventory` is shared-portfolio evidence even when queried
  through one managed KIS project; filter/identify records by source repository
  and stable source identity.
- Disabled auto-add/close/merge synchronization means an issue existing on GitHub
  does not prove it is projected or current in Work Management.
- A successful reconciliation preview is not an applied mutation.
- Work Management Status is command authority; GitHub issue state/history remains
  source identity and narrative history. Do not make either one impersonate the
  other's authority.
- Rich desired fields may remain unprovisioned; never convert that gap into fake
  success or duplicate command metadata into issue prose.
- Reconciliation idempotency protects retries, not stale assumptions. Refresh
  observed evidence before a materially different update.
