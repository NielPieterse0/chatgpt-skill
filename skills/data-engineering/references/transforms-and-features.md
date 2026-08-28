# Transformations and features

Load when creating or auditing transformations, features, rolling aggregates, target encodings, embeddings, imputers, scalers, selectors, or dimensionality reduction.

- Specify ordered deterministic transformations from source columns to output columns.
- Define each material feature's source fields, transform, expected type/range, availability timestamp, and version.
- Establish a simple raw-feature baseline before complex derivations.
- Fit learned preprocessing only on the permitted training partition, and within each temporal split when applicable.
- Test missingness, sparsity, cardinality, drift, stability, and incremental value by split/time/segment.
- Treat target encoding, entity history, rolling windows, refreshed external attributes, and backfills as high-risk until cutoff logic is proven.
- Prefer interpretable derivations with repeatable incremental value; remove unsupported complexity.
