# Standalone Scaling

Use this reference only when KIS is not the repository's workflow authority.

Do not map these heuristics onto KIS classifications or treat them as KIS terminology. In KIS-managed work, read the current KIS classification and use it directly.

Scale specialist rigor from the work actually present:

- **Bounded:** one clear, reversible outcome with little design uncertainty. Keep specification and planning compact; still use TDD for behavior changes and fresh completion verification.
- **Non-trivial:** dependent steps, multiple affected surfaces, meaningful design choices, shared interfaces, or a broader regression surface. Use explicit requirements and planning; add brainstorming when decisions are unresolved and review at useful checkpoints.
- **High-risk or complex:** architectural or trust-boundary changes, security/privacy concerns, persistent data, migration, provider/deployment/release coupling, difficult rollback, or uncertainty with high consequence. Use explicit brainstorming, planning, test strategy, review, verification, and recovery evidence.

File count and line count are supporting evidence, not the deciding factor.

Reassess when discovery reveals hidden consumers, shared contracts, broader permissions, data/state changes, migration or rollback needs, additional systems, unclear acceptance criteria, failed assumptions, or repeated verification failures.
