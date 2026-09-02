---
name: verification-before-completion
description: Use when about to claim that work is complete, fixed, correct, passing, ready for integration, or otherwise successful and the claim requires fresh observable evidence.
license: MIT
---

# Verification Before Completion

Evidence must precede every material completion claim.

## Iron law

Do not upgrade expectation, confidence, reviewer opinion, or stale output into a factual success claim. Identify what would prove the claim, obtain that evidence on the current state, then state only what the evidence supports.

## Gate

1. Name the exact claim you are about to make.
2. Identify the command, check, provider observation, or artifact inspection that proves that claim.
3. Run or obtain it against the current artifact, branch, output, revision, or runtime state.
4. Read the complete result: exit status, failures, warnings, skips, checked identity, and evidence freshness.
5. Compare evidence with the claim. If it proves less, report the narrower truth.
6. For multiple claims, require evidence for each one. One passing focused test does not prove repository-wide verification, runtime commissioning, deployment, or merge state.7. If evidence is unavailable, stale, partial, or blocked, say so explicitly instead of substituting inference.

## Freshness rule

A material change after verification invalidates evidence that depends on the changed state. Re-run affected checks. Head-specific CI, review, and merge readiness must match the exact head the claim concerns.

## Red flags

- "It should pass now."
- Reusing a test result from before the last edit.
- Trusting an agent's or tool's success summary without inspecting the authoritative result.
- Treating a clean diff as proof of behavior.
- Saying "merged," "deployed," or "live" based only on a request to perform that action.
- Omitting skipped or unavailable checks from the completion report.

## Boundaries

This is evidence discipline, not mutation authority. Repository policy defines required checks and authoritative evidence sources. In KIS-managed repositories, use the live KIS/repository verification and provider evidence required by the governing workflow; do not reconstruct or bypass those gates.