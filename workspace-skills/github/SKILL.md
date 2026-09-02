---
name: github
description: Use this skill for general GitHub repository, issue, and pull-request orientation or when a GitHub request must be routed to the correct governed workflow. Resolve repository and KIS context, perform bounded triage, and route existing-PR repair to github-pr-maintenance or publication/landing/closeout to github-delivery. Do not use it as a substitute for code implementation, code review, PR maintenance, or delivery once the narrower outcome is clear.
---

# GitHub

Use this skill as the project-neutral entrypoint for GitHub work. Resolve context and authority, gather only enough GitHub evidence to classify the task, then keep general triage here or hand the work to the narrow specialist that owns the outcome.

## Authority and safety

- Follow the target repository's `AGENTS.md`, source issue/change record, Git state, and repository policy before making GitHub workflow decisions.
- For KIS-managed repositories, resolve the registered project and current Work Management command-plane state before durable workflow mutation. Use the live authority map rather than assuming which fields are Project-owned.
- Treat repository/Git/GitHub/Actions evidence as implementation and delivery truth; do not rewrite it to match stale Project state.
- Use the live KIS/provider capability catalogue rather than copied tool schemas. Capability discovery is not authorization.
- Do not bypass a missing governed capability with raw `gh`, unrestricted GraphQL, arbitrary network commands, force/admin operations, or direct default-branch mutation.
- Do not invent a KIS requirement for an unregistered repository or a simple read-only GitHub question.

## Resolve the target

Prefer explicit user context: repository, URL, issue number, PR number, branch, or local checkout. When the request refers to "this repo", "this PR", or "this branch", resolve the local repository identity and current Git state before assuming the GitHub target.

For a registered KIS project, use live project/provider evidence for mutable bindings. Do not hard-code repository owners, project numbers, default branches, or provider-operation parameters into the skill.

If the target remains materially ambiguous after available context is inspected, request only the missing repository or item identity.

## Classify the intent

Choose exactly one primary path:

### General GitHub triage — stay here

Use this skill directly for bounded tasks such as:

- summarize repository, issue, or PR state;
- inspect recent/open issues or pull requests;
- read PR metadata, files, reviews, checks, comments, labels, or reactions;
- identify which GitHub item needs attention;
- perform an explicitly authorized lightweight issue/PR metadata action that does not own the repository delivery lifecycle.

Prefer structured provider reads/writes exposed through the current approved KIS provider boundary. Keep the result concise and evidence-linked.

### Existing PR needs repair — route to `github-pr-maintenance`

Route immediately when the outcome is to inspect or address:

- unresolved or disputed review feedback;
- requested changes or inline review threads;
- failing GitHub Actions checks;
- stale-head or base-drift problems;
- merge conflicts on an existing PR;
- verification needed to return an existing PR toward readiness.

Do not duplicate that skill's thread triage, exact-head CI classification, code-fix, conflict, or verification loop here.

### Work must be published or landed — route to `github-delivery`

Route when the requested outcome includes any material portion of:

- turning verified local work into a reviewable PR;
- registered publication or PR creation;
- shepherding a governed PR to merge readiness;
- choosing ordinary managed merge versus merge queue;
- landing the exact approved work;
- post-merge Work Management/documentation reconciliation;
- remote branch or worktree cleanup after verified landing.

Do not create a parallel push, PR creation, merge, queue, watcher, or cleanup workflow in this umbrella.

### Code-focused work — use the generic specialist

Use `code-work` when the primary outcome is to implement/change code without a GitHub delivery lifecycle. Use `code-review` or `code-verification` when the primary outcome is read-only code findings or verification. GitHub context may supply the change boundary without making this umbrella the owner of the code workflow.

## KIS workflow discovery

For an end-to-end governed outcome, prefer the highest-level live KIS workflow that matches the request. Use workflow recommendation/capability search only when the correct direct operation is not already known. Inspect the selected workflow's required steps, readiness, effects, and exact input schema before invoking it.

If the running KIS instance lags repository source, follow the live runtime contract and report the gap. Do not assume a workflow exists merely because it is documented or in-flight.

## Write discipline

For a bounded GitHub write that stays in general triage:

1. identify the exact repository/item and intended mutation;
2. confirm it is authorized by the request and repository policy;
3. use an approved provider operation with its current schema;
4. verify the returned GitHub state.

When the write changes implementation, publication, readiness, landing, or cleanup state, route to the responsible specialist/KIS workflow instead.

## Output

Report:

- resolved repository and GitHub item;
- authoritative/current state inspected;
- the primary intent classification;
- the specialist/workflow selected when routed;
- any action actually performed and its verified result;
- concrete blocker or capability gap when the governed path cannot continue.

Do not continue broad GitHub triage after a narrower specialist owns the outcome.