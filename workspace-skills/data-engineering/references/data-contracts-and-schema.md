# Data contracts and schema

Load when defining or reviewing source/consumer contracts, schemas, keys, grain, compatibility, or schema evolution.

## Contract first
A data contract is the explicit agreement that makes a dataset interpretable and safely consumable. Define the contract before optimizing storage or pipeline mechanics. A useful contract covers both structure and meaning.

For each dataset or material layer, record:

- purpose, owner/steward, intended consumers, and prohibited or unsupported uses;
- row grain and entity/event identity;
- primary/business keys, uniqueness rules, foreign-key expectations, and expected join cardinalities;
- field names, types, units, domains/ranges, semantic definitions, and allowed enumerations;
- nullability plus the meaning of absence, not merely whether a null is technically allowed;
- event/observation, availability/publication, and ingestion timestamps where applicable;
- freshness/latency expectations and whether they are guarantees, objectives, or observations;
- revision, correction, deletion, and backfill policy;
- schema/contract version and compatibility expectations;
- provenance needed to trace produced fields to sources and transformations.

## Grain, keys, and cardinality
Never infer grain from column names alone. State it in one sentence, then test it.

Examples of grain questions:

- Is one row an order, order line, customer-day, instrument-timestamp, contract-session, or publication vintage?
- Is the key truly unique, unique only within a partition, or only unique after filtering?
- Can a source emit corrections with the same business key but a later version timestamp?
- Is a relationship one-to-one, one-to-many, many-to-one, or legitimately many-to-many?

Before a join, declare the expected relationship. After the join, verify left/right row counts, matched and unmatched key counts, duplicate-key counts, multiplicative expansion, and any changed null rates. Treat unexplained row multiplication as a defect until shown otherwise.
## Schema evolution
Classify changes by consumer impact rather than by syntax alone.

- Additive optional fields may be backward compatible if consumers ignore unknown fields.
- Renames, type changes, unit changes, semantic reinterpretations, key changes, and nullable-to-required changes are breaking unless a migration contract proves otherwise.
- Enumeration expansion can break closed-world consumers even when the physical type is unchanged.
- Timestamp timezone, precision, or interpretation changes are semantic schema changes.
- A source correction policy can be as important as column schema: consumers need to know whether historical rows can change.

Detect schema drift before it silently changes downstream meaning. Do not auto-accept a changed schema merely because a storage engine can merge it.

## Layer contracts
Raw/bronze-like layers should preserve source fidelity and acquisition metadata. Validated/cleaned layers may standardize representation while preserving traceability. Feature/evaluation layers may impose stronger semantic and temporal constraints. Do not force a named medallion architecture when the project uses a different layering model; preserve the underlying guarantees instead.

A layer handoff is ready when its contract is versioned, critical invariants are tested, known violations are explicit, and consumers can identify which contract version produced the data they received.

## Source-derived and research basis
The harvested upstream Data Engineer explicitly emphasized producer/consumer contracts, source profiling, cardinality, schema validation/evolution, lineage, deliberate null handling, and publishing contracts before consumer use. Issue #134 retains those durable requirements while removing platform-specific assumptions.

Academic/production research strengthens the same direction: Breck et al., *Data Validation for Machine Learning* (SysML 2019), treats input data quality and schema validation as first-class ML-system concerns; Sculley et al., *Hidden Technical Debt in Machine Learning Systems* (NeurIPS 2015), highlights undeclared consumers and unstable data dependencies as system-level debt. See `research-evidence.md` for citations and scope.
