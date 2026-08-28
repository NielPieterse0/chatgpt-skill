---
name: evidence-collector
description: Design and collect reproducible verification evidence for claimed behavior, experiments, and data or software changes using tests, logs, outputs, metrics, screenshots, and acceptance criteria. Use when a quality, experiment, or completion claim needs evidence rather than assumption; do not use to implement the change being tested.
license: MIT
---
# Evidence Collector

## Purpose
Test claims against appropriate evidence without biasing the review toward either failure or success.

## Safety and authority
- Do not assume screenshots are sufficient for behavior that requires logs, state inspection, tests, or accessibility evidence.
- Do not invent issue counts, ratings, screenshots, test execution, or production-readiness claims.
- Run only verification actions allowed by the governing environment; evidence collection does not authorize app mutation or external publication.
- Keep credentials, personal data, and sensitive operational details out of captured evidence.

## Workflow
1. Translate each acceptance claim into the strongest practical evidence source and expected result.
2. Collect bounded evidence using deterministic tests first, then visual or manual checks where they add information.
3. Compare observed results to the actual requirement, not an inflated or reduced substitute.
4. Record failures, passes, uncertainty, unavailable checks, and evidence references without quota-driven issue hunting.
5. Re-run affected checks after fixes and distinguish local evidence from full-system or production evidence.

## Completion criteria
Every material conclusion is supported by appropriate evidence or explicitly marked unverified, with no fabricated testing or predetermined verdict.