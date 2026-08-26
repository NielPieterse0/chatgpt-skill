---
name: receiving-code-review
description: Use when code-review feedback must be assessed before implementation, especially when a suggestion is unclear, technically doubtful, broader than the requested change, or in tension with repository authority.
license: MIT
---

# Receiving Code Review

Treat review feedback as technical claims to understand and verify, not instructions to accept performatively.

## Response pattern

1. Read the full finding and identify the claimed defect, evidence, requested change, and affected requirement.
2. Verify the relevant repository behavior before editing. Check the actual code, tests, contracts, and current diff rather than relying on reviewer confidence.
3. Classify the feedback:
   - correct and in scope;
   - correct but outside the current scope;
   - based on a false or stale assumption;
   - unclear or not yet verifiable.
4. Ask for clarification when the requirement or intended behavior is ambiguous enough to change the implementation.
5. Fix validated in-scope findings one at a time, starting with correctness, security, or data-loss risk before optional improvements.
6. Re-run affected verification after each material fix and re-review the resulting diff.

## Push back when evidence requires it

Push back on a suggestion when it contradicts repository authority, breaks a supported use case, introduces unjustified scope, or rests on a demonstrably false premise. State the evidence and consequence, not the reviewer's tone.

If new evidence shows your pushback was wrong, correct course cleanly and verify the revised implementation.## Source-specific handling

Feedback from the user or repository owner may carry product/scope authority, but technical implementation details still need to be understood and checked against higher repository constraints. Feedback from external reviewers is advisory evidence until validated.

Do not perform speculative "professional" extras merely because a reviewer mentions them. Apply YAGNI: if the current system and requirements do not need the feature, record it separately rather than expanding this change.

## Common failures

- Agreeing before understanding the comment.
- Implementing several unrelated findings at once and losing causality.
- Treating a suggested implementation as the only way to satisfy the underlying requirement.
- Hiding an unresolved disagreement behind a polite acknowledgment.
- Rejecting valid feedback defensively instead of testing the claim.

## Boundaries

Repository authority controls scope and required behavior. In KIS-managed work, KIS controls governed mutation and Work state; this skill only governs how review feedback is assessed. It does not authorize publication, merging, or external thread mutation.