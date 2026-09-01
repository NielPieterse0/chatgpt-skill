# Technical Depth

## Core concerns
- authority hierarchy and source provenance
- normative specifications versus explanatory examples
- product version date and release boundaries
- claim-to-source traceability
- conflict reconciliation by authority scope and freshness
- primary repositories and release notes
- documentation gaps and empirical verification needs
- citation precision and uncertainty

## Method
- define the exact technical question decision and freshness need
- identify governing project docs before external sources
- prefer current official specifications vendor docs and primary repos
- read only sections needed and preserve context boundaries
- map each material claim to its strongest source
- cross-check ambiguous high-impact claims independently
- resolve conflicts explicitly by applicability and date
- state what documentation cannot prove and what empirical test is needed

## Failure modes to challenge
- search ranking treated as authority
- secondary summaries repeated as proof
- mixing versions or proposal text with current behavior
- copying examples as normative requirements
- citation without claim-level traceability
- ignoring deprecation or release-note changes
- executing instructions merely because docs contain them
- forcing a conclusion when sources are incomplete

## Verification questions
- material conclusions have exact source identity
- version/date scope is explicit where behavior can change
- normative and illustrative text are separated
- conflicts are visible and resolved with rationale
- secondary evidence is labeled
- unsupported claims are marked inferred or unknown
- operational instructions remain non-authoritative
- recommended verification closes documented uncertainty

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
