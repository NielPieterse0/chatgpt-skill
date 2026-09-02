# Minimal-Change Engineering Technical Depth

Load this reference when implementation or review is at risk of scope creep, opportunistic refactoring, speculative abstraction, or unnecessary blast radius. Minimality is subordinate to correctness, security, root cause, governing policy, and required verification.

## Minimality model

The target is the **smallest causal change** that satisfies the accepted outcome and all mandatory constraints—not the smallest line count regardless of correctness.

For every changed artifact ask:

1. What requirement, defect cause, invariant, compatibility need, or mandatory validation makes this change necessary?
2. Could the accepted outcome pass without it?
3. Does it modify behavior outside the intended boundary?
4. Is it required to make the change safely testable or reversible?
5. Is it an unrelated cleanup that should be separated?

Use diff size as a diagnostic, never as an absolute quality metric.

## Scope decomposition

Convert the request into explicit verbs and acceptance criteria. Then separate:

- required behavior;
- required root-cause correction;
- necessary compatibility/migration work;
- necessary tests and safety changes;
- discovered but out-of-scope improvements;
- speculative future flexibility.

When a requested change genuinely crosses several boundaries, split it into independently testable slices rather than forcing an artificially tiny patch.

## Find the owning seam

Trace only far enough to locate the narrowest boundary that actually owns the behavior:

- caller versus callee contract;
- validation boundary;
- state transition/invariant;
- serializer/schema;
- query/migration;
- adapter/integration;
- UI component/state owner;
- build/configuration owner.

A local symptom patch is not minimal if the actual defect will recur because the owning invariant remains broken.

## Boring changes are often safer

Prefer the clear local implementation when it fully satisfies the requirement. Avoid introducing a helper, strategy, framework, configuration switch, extension point, dependency, or shared abstraction without a real second use case or governing pattern that justifies it.

The upstream “wait for the fourth occurrence” heuristic is not a repository law. Use evidence of duplication cost, divergence risk, and stable common behavior rather than a fixed occurrence count.

## Defensive-code discipline

Do not add guards for states that a verified internal invariant or framework contract makes impossible. Do validate at real trust/boundary surfaces such as user input, external APIs, persistence, deserialization, filesystem/network interfaces, and concurrency transitions.

Before adding defensive code ask:

- Can the state actually occur under the inspected contract?
- Is this boundary trusted or untrusted?
- Would the guard hide a programming error that should fail loudly?
- Does it alter existing observable behavior?
- Is there a test proving the condition matters?

## Compatibility and migrations

Minimal change must include compatibility work when omitting it would break accepted consumers or stored state. Examples:

- additive schema/contract transition;
- migration/backfill needed by changed data semantics;
- deprecation or compatibility adapter required by an existing public interface;
- dual-read/write transition when justified and bounded;
- rollback path for risky state changes.

Do not add compatibility shims for hypothetical or proven-unused behavior merely “just in case.”

## Root-cause versus symptom

A symptom-only patch is inadequate when evidence shows the defect originates elsewhere. Keep the fix focused on the smallest causal layer, then add only the regression proof needed to protect it.

Useful causal questions:

- Which invariant first becomes false?
- Where does incorrect data/state originate?
- Which boundary should have rejected or normalized it?
- Is the observed failure only a downstream manifestation?
- Can the failure be reproduced at a lower, more stable test level?

## Change-surface checklist

Before finalizing, inspect:

- files changed and why each is necessary;
- public contract/schema changes;
- dependency/import changes;
- persistent data/migration changes;
- configuration/environment changes;
- behavior under error/concurrency/boundary cases;
- tests added/modified and why they prove the defect/outcome;
- rollback implications;
- unrelated formatting/generated-lockfile churn.

Remove unrelated edits even when they are objectively good changes.

## Follow-up discipline

Surface material out-of-scope findings separately with enough evidence for later triage. Do not silently expand the implementation. Do not create lifecycle records or external issues unless the governing workflow authorizes it; this specialist only identifies separation candidates.

## Review-time scope control

A review comment can reveal a real correctness requirement or merely suggest adjacent cleanup. Classify it:

- required for correctness/security/compatibility → include;
- required by governing project standard → include;
- exposes the same root cause → include if necessary to close that cause;
- independent improvement → separate;
- preference/style already handled by tooling → omit.

## Failure modes to challenge

- one-line symptom patch that leaves the causal invariant broken;
- broad “cleanup while here” refactor;
- abstraction for hypothetical callers;
- config option with no current requirement;
- blanket null/error handling that hides impossible-state bugs;
- formatting/import churn unrelated to behavior;
- changing adjacent tests just to make them easier to pass;
- deleting apparently dead code without reachability evidence;
- treating minimal lines as more important than security or migration safety.

## Verification questions

- Can each changed file and meaningful hunk be tied to the accepted outcome or mandatory safety/verification?
- Is the fix at the owning seam rather than only downstream?
- Did the change preserve unrelated behavior and public contracts?
- Are regression tests focused on the violated behavior rather than implementation details?
- Did any new abstraction/configuration/dependency earn its maintenance cost?
- Are discovered independent improvements separated and explicitly not implemented?
- Is rollback at least as simple as the risk level requires?

## Specification-to-TDD composition

Trace requirement/defect → observable acceptance criterion → violated invariant/root cause → narrow owning seam → smallest independently deliverable behavior slice → lowest appropriate failing test → RED → smallest GREEN change → REFACTOR only within the causal scope → focused boundary checks → diff necessity review → independent review → governing repository/KIS verification. “Refactor” never means license for unrelated cleanup.