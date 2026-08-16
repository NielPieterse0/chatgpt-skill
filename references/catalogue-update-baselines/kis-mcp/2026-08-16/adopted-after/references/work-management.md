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

Work Management is an operational projection, not repository authority.

Use this order:

1. the target repository's `AGENTS.md` and authoritative documents;
2. the repository-owned source issue/PR/change record and Git/GitHub evidence;
3. KIS Work Management Project state as the synchronized operational view.

Never rewrite repository truth to match a stale Project value. Reconcile the
projection from current repository evidence instead.

## Intake routine

For material work, do this before implementation when the target repository
requires Work Management:

1. Resolve the stable KIS `project_id` and repository identity.
2. Search the source repository and `project_management_inventory` for an
   existing issue/PR representing the same bounded outcome. Do not duplicate it.
3. If Project fields or statuses matter, run `project_management_schema_status`
   or inspect current inventory/schema evidence before choosing field values.
4. Create or update the authoritative source issue/PR with a complete canonical
   Work Management block using every applicable field below.
5. Attach the source identity to a stable KIS record ID such as `SPEC-009`,
   `TASK-012`, `DEFECT-004`, or another repository-approved prefix/number.
6. Build reconciliation input from the complete bounded inventory. Preview with
   `project_management_reconcile(..., apply=false)`.
7. Review every outcome. Apply only the intended actions with `apply=true`, a
   non-empty stable idempotency key, and current observed revision/evidence.
8. Re-read inventory after mutation and confirm the exact source item/status is
   projected once.

An absent record may be represented by an empty `observed` entry only after a
complete bounded inventory proves it is absent. Do not infer absence from a
truncated result.

## Complete source record

The repository-owned source issue/PR must carry the canonical work metadata even
when the live Project cannot yet represent all of it. Fill every applicable
field; do not leave meaningful values implicit in prose.

| Field | Use |
|---|---|
| `Status` | Current canonical lifecycle state. Required for governed work. |
| `Record Type` | Idea, Task, Specification Slice, Review Run, Finding, Decision, Assumption, Risk, Approval, Hold, Research, Defect, or Security Finding. Required. |
| `Priority` | Critical, High, Medium, or Low. Required. |
| `Project ID` | Stable KIS project ID. Required. |
| `Repository` | Repository owning the source record and lifecycle. Required. |
| `Module` | Fill when a durable product/module boundary is known. |
| `Change ID` | Fill for governed implementation/specification slices or another repository change identity. |
| `Origin` | Operator, Review, Verification, Implementation, or Research. Required. |
| `Disposition` | Open, Accepted, Rejected, Superseded, Mitigated, or Deferred. Required when the record has a disposition. |
| `Verification` | Not Run, Pending, Passed, Failed, or Blocked. Required for work requiring verification. |
| `Severity` | Fill for defects, risks, findings, and security findings where severity is meaningful. |
| `Confidence` | Fill for evaluative findings, assumptions, research conclusions, or other uncertain evidence. |
| `Review Trigger` | Required for a Hold/Deferred item and useful whenever a future condition determines re-review. |
| `Target Date` | Fill only when a real deadline or planned target exists. |
| `Iteration` | Fill only when an iteration/cadence is actually configured. |
| `Source Review` | Link or identify the review/research evidence that originated the record when applicable. |
| `Authority Revision` | Record the exact source/authority revision when the work depends on revision-specific evidence. |
| `External Link` | Add a relevant external artifact only when it materially belongs to the record. |

Do not manufacture placeholder Project values merely to make every cell nonempty.
For an inapplicable optional field, omit it or mark it explicitly in the source
record when that distinction helps reviewers. Never claim an unsupported Project
field was populated.

## Project schema and compatibility

The repository-owned desired Work Management schema currently defines 18 fields
and 12 named views. The live Project may lag that target.

Before writing Project fields:

- use live schema/inventory evidence as the invocation contract;
- use only field names and option values the provider can currently observe and
  update;
- keep missing canonical values in the source issue/PR/change record;
- report schema/view drift explicitly;
- never bypass a provider gap with unrestricted GraphQL, guessed field IDs, or
  invented status options.

If `project_management_schema_status` rejects a managed project because the
shared schema manifest is bound to a different managed-project identity, treat
that as a Work Management contract defect. Do not hard-code the schema owner's
project ID as a universal workaround. Continue only with directly observed
inventory/field evidence for that project and record the missing schema-status
evidence until the live contract is corrected.

A legacy Project `Status` such as `Todo`, `In Progress`, or `Done` is not the
canonical lifecycle model. Use a legacy value only when its mapping is
unambiguous for the current state. Keep nuanced states such as review,
verification, documentation, blocked, hold, deferred, rejected, or superseded in
the authoritative source record when the Project cannot represent them exactly.

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

## Lifecycle status maintenance

Keep Work Management current throughout the task. Update at meaningful state
transitions, not after every microscopic tool call.

Typical transitions:

- intake/approved execution -> `Active`;
- substantive review -> `Review`;
- running or awaiting required checks -> `Verification`;
- required post-implementation documentation reconciliation -> `Documentation`;
- concrete delivery blocker -> `Blocked`;
- operator/authority pause -> `On Hold` with a review trigger;
- intentionally postponed work -> `Deferred` with disposition/review trigger;
- verified and fully reconciled completion -> `Done`.

At each transition:

1. update the canonical status/verification/disposition fields in the source
   record when they changed;
2. add a concise source-record status comment containing completed evidence,
   blockers/risks, and the next action when that history is useful;
3. reconcile every currently supported Project field through preview then
   idempotent apply;
4. re-read the projected item and confirm it matches the intended supported
   state.

Do not set `Done` while required verification is failed/pending, required
post-merge documentation is incomplete, approval is outstanding, or an explicit
operator hold says the record must remain open.

## Child issues and newly discovered work

Do not bury an independently actionable defect, finding, risk, decision,
assumption, or follow-up inside a parent comment.

When new bounded work appears:

1. search for an existing source record first;
2. create or update the child with the same complete applicable metadata
   discipline as the parent;
3. identify the parent in the child body;
4. use `github_sub_issue_write` to create the native parent/sub-issue relation
   when the provider exposes it;
5. add a parent status update naming the linked child and why it was separated;
6. reconcile the child into Work Management using its own stable record ID;
7. preserve the parent's status based on its own acceptance criteria; do not
   silently make child completion equivalent to parent completion.

Use native hierarchy rather than only textual `Parent: #N` when available. If a
native relation cannot be written, retain the textual relation and report the
provider limitation explicitly.

## Review, verification, and closeout

For change-backed work, keep source issue, change record, PR, verification, and
Project state synchronized without making the Project authoritative.

- Use `project_management_verify_traceability` at the lifecycle stage required
  by the repository.
- Before a managed PR lands, use `project_management_merge_readiness` with the
  exact PR/head evidence. Provider-native exact-head CI remains the landing gate
  when the workflow requires it.
- Classify documentation impact during intake, not after merge.
- When documentation reconciliation is required after merge, use
  `project_management_documentation_reconcile` to create the due milestone and
  keep the record in `Documentation` until `post_merge_complete` is recorded at
  an exact completion revision.
- Close the source issue and move the Project record to its final supported state
  only after all required verification, documentation, approval, and hold
  conditions are satisfied.

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
- A Project status update does not replace the source issue status/history.
- Rich desired fields may remain unprovisioned; never convert that gap into fake
  success.
- Reconciliation idempotency protects retries, not stale assumptions. Refresh
  observed evidence before a materially different update.
