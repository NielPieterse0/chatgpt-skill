# Transformations and features

Load when creating or auditing transformations, features, rolling aggregates, target encodings, embeddings, imputers, scalers, selectors, or dimensionality reduction.

## Transformation contract
For every material transformation, define:

- input fields and their contract versions;
- output fields, type/unit/semantic meaning, and expected range/domain;
- deterministic operation order and parameters;
- availability timestamp and information-cutoff rule;
- grouping, sorting, window, and boundary semantics;
- missing-value behavior and any status/provenance fields retained;
- fit scope when parameters are learned from data;
- code/configuration identity and produced feature version.

Prefer transformations that are deterministic for fixed inputs and parameters. If nondeterminism is unavoidable, record its source and the evidence needed to reproduce or bound it.

## Feature engineering
Start with a simple raw or minimally transformed baseline before adding complex derived features. A feature is not justified merely because it can be computed.

For each feature, evaluate structural evidence here:

- coverage and missingness by time/entity/segment;
- stability and drift;
- sensitivity to units, clipping, winsorization, and outliers;
- temporal availability and leakage risk;
- dependence on revised/backfilled information;
- redundancy or obvious deterministic equivalence;
- computational/storage cost and update complexity.

Predictive incremental value, model-specific feature importance, feature selection against validation metrics, and model-coupled ablation belong to `model-tuning`. Data engineering may prepare stable candidate feature sets and structural diagnostics, then hand them off without selecting winners from predictive outcomes.
## Learned preprocessing
Fit imputers, scalers, encoders, dimensionality reduction, selectors, vocabulary builders, and similar learned transforms only on the permitted training partition. For cross-validation or rolling-origin evaluation, refit inside each training split unless the transform is provably independent of held-out information.

Persisted preprocessing that defines the experiment input belongs to the dataset/feature identity. Experiment-local model-coupled preprocessing may vary inside `model-tuning`, but it must not mutate the frozen source dataset or silently reuse parameters learned from another split.

## High-risk feature patterns
Treat these as leakage-sensitive until cutoff logic is demonstrated:

- target encoding and aggregate statistics involving the target;
- entity history and cumulative/rolling windows;
- centered windows or interpolation using both past and future neighbors;
- joins to refreshed master/reference data;
- backfilled fundamentals, revised macro data, corrected labels, or realized weather;
- forward-fill across entity boundaries, contract rolls, or long source outages;
- features derived from post-event operational fields;
- normalization using full-period extrema, means, quantiles, or ranks.

## Missing-value transforms
Never collapse missingness reasons before deciding whether they are semantically equivalent. Forward-fill requires a domain-valid persistence assumption plus a maximum staleness rule. Interpolation requires an explicit statement that future observations are allowed for the intended task; it is normally invalid for historical forecasting features. Imputation should preserve an indicator/provenance signal when the fact or cause of missingness may carry information.

## Verification
Spot-check boundary rows by hand or with deterministic tests: first/last observations in windows, split boundaries, publication times, timezone/session transitions, and entities with sparse history. For a fixed input snapshot and parameters, rerunning the transformation should yield the same declared logical feature identity.
