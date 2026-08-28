# Experiment data and reproducibility

Load when preparing datasets for repeated modeling experiments, defining dataset identity/versioning, or auditing whether experiment inputs can be independently reconstructed.

## Dataset manifest
For every experiment-ready dataset record enough information to identify and rebuild it:

- use contract and dataset contract version;
- immutable source snapshot/version identities and acquisition dates where relevant;
- source schema/semantic versions and revision/vintage policy;
- ordered transformation and feature definitions plus parameters;
- material exclusions, filters, deduplication rules, and missing-value policies;
- split definitions/boundaries and entity grouping constraints;
- preprocessing identity and fit scope;
- code/configuration/environment revision when governed by the repository;
- output schema, row grain, keys, row/column counts, and quality disposition;
- known caveats, rejected inputs, and unresolved limitations.

Preserve failed, rejected, superseded, and corrected dataset versions rather than rewriting the identity of an input that was already used for research evidence.

## Deterministic content identity
Distinguish logical dataset identity from file-byte identity.

A robust logical identity can hash a canonical representation of the contract plus normalized content and material transformation inputs. Canonicalization must specify ordering, field names/types, null/missingness representation, numeric/date normalization, encoding, and which metadata are included. Equivalent logical data should not receive different identities merely because Parquet row groups, compression settings, or other non-semantic serialization details differ.

Use a byte-level cryptographic hash when exact file bytes are themselves part of the contract or serialization is controlled deterministically. Record the hashing algorithm and scope; never compare unlabeled digest strings whose canonicalization rules differ.
## Reconstruction protocol
A reconstruction audit should be executable conceptually even when this Tier 0 skill cannot run it itself:

1. Resolve the exact source snapshots/vintages and contract versions.
2. Apply the recorded exclusions, ordering, transformations, feature definitions, and missing-value rules.
3. Recreate splits and preprocessing with the recorded fit scope.
4. Recompute quality/contract assertions.
5. Recompute the declared logical content identity.
6. Compare it with the recorded identity and explain any mismatch before using the dataset as equivalent evidence.
7. When byte identity is required, also compare the deterministic byte hash.

Completion requires stronger evidence than "the pipeline ran." Another researcher should be able to reproduce the declared logical identity or obtain a precise, evidence-backed reason why exact reconstruction is impossible.

## Ordered data and splits
For forecasting or decision-time problems, preserve chronological information boundaries. Expanding-window, rolling-window, or other ordered validation designs may be appropriate; the model-selection protocol itself belongs to `model-tuning`. Data engineering owns the point-in-time dataset/split inputs that make such evaluation possible.

Do not let validation/test outcomes feed back into persisted feature definitions without issuing a new feature/dataset version. A new version may be compared in a new experiment, but it must not masquerade as the unchanged original input.

## Reproducibility principles
Keep a machine-readable or otherwise deterministic path from result inputs back to raw/source identities. Avoid manual unrecorded edits. Preserve intermediate identities when they materially aid audit/recovery. Record exact external-data versions, custom transformation versions, and randomness only where randomness is part of data construction.

This follows the reproducibility direction of Sandve et al. (2013), FAIR provenance/version principles, and modern dataset documentation/versioning work. See `research-evidence.md`.
