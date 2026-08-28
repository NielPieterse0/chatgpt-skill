---
name: data-engineering
description: Build and validate reproducible research data pipelines, datasets, joins, features, lineage, point-in-time market data, and data-quality controls. Use for end-to-end data engineering from source understanding through experiment-ready datasets; use model-tuning for fitting, tuning, or evaluating models.
---
# Data Engineering Specialist

## Purpose
Turn source data into experiment-ready datasets that are point-in-time correct, reproducible, quality-audited, and traceable. Treat dataset construction as part of the research evidence.

## Default sequence
1. **Frame the data question.** Define downstream decision, population, grain, keys, target timing, information cutoff, and required outputs before choosing transformations.
2. **Understand sources.** Inventory provenance, schema, freshness, access constraints, timestamp semantics, revisions/vintages, units, calendars, and contract identities. Load `references/source-and-time-semantics.md` when sources are historical, revised, market, futures, weather, or otherwise time-sensitive.
3. **Acquire and layer data.** Preserve immutable raw/source identities and separate raw, cleaned, feature-ready, and evaluation-ready layers. Never silently overwrite a dataset already used by an experiment.
4. **Audit quality before complexity.** Check grain, uniqueness, completeness, validity, join coverage, row multiplication, missingness, drift, labels, and leakage. Load `references/data-quality-and-leakage.md` for dataset fitness decisions or suspicious joins/splits.
5. **Transform and engineer features.** Define deterministic transformations, temporal availability, preprocessing fit scope, lineage, and feature versions. Load `references/transforms-and-features.md` when deriving features, learned preprocessing, rolling windows, target encodings, or aggregations.
6. **Engineer the pipeline.** Make states, inputs, outputs, retries, idempotency, partial-write behavior, observability, quarantine/recovery, and acceptance evidence explicit. Load `references/pipelines-and-workflows.md` for multi-stage, scheduled, streaming, retrying, or failure-prone workflows.
7. **Hand off to experimentation.** Produce immutable dataset/split/feature identities and record enough lineage to reconstruct the exact inputs. Load `references/experiment-data-and-reproducibility.md` when preparing data for repeated experiments or auditing reproducibility.
8. **Verify completion.** Confirm another researcher can reconstruct what data was available, how it changed, and why the resulting dataset is fit for its stated use. Use repository/KIS verification and lifecycle mechanisms for execution evidence and completion state; this skill does not replace them.

## Critical rules
- When time matters, separate observation time, publication/release time, ingestion time, and decision/information-cutoff time.
- Never substitute later revisions, future-known values, post-outcome fields, or globally fitted preprocessing into historical training/evaluation data.
- Validate joins with key cardinality, row counts, unmatched keys, many-to-many expansion, temporal alignment, units, and types.
- Preserve source, dataset, split, feature, and transformation identities with stable hashes/versions where available.
- Keep secrets, credentials, restricted personal data, and sensitive values out of logs and artifacts.

## Boundary
Own data research, acquisition semantics, dataset construction, quality, features, lineage, and pipeline design. Hand off model fitting, hyperparameter search, statistical model comparison, backtesting of model outputs, and model promotion evidence to `model-tuning`. Do not infer deployment, trading, procurement, Git publication, or project-lifecycle authority.
