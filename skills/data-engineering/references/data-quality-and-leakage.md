# Data quality and leakage

Load when deciding whether a dataset is fit for modeling, experimentation, inference, evaluation, or downstream analysis.

## Audit order
Start with semantics before statistics:

1. Confirm intended use, grain, keys, target/time semantics, and contract version.
2. Test uniqueness, referential integrity, schema/types, allowed domains, units, and temporal validity.
3. Measure completeness and missingness by field, time, entity, source, segment, and missingness reason.
4. Validate joins using expected cardinality, match rates, row multiplication, duplicate keys, and temporal alignment.
5. Inspect duplicates, impossible values, outliers, stale values, and distribution changes.
6. Test leakage and split contamination only after the dataset's basic meaning is trusted.

Do not summarize quality as one score unless the aggregation rule and loss of detail are justified. Preserve critical invariant failures individually.

## Missing data
A null rate alone is not a missing-data analysis. Distinguish data-pipeline absence from statistical missingness assumptions.

Operationally classify why the value is absent when possible: not applicable, not observed, not yet published, source unavailable, suppressed/redacted, invalid/rejected, or genuinely unknown. Profile missingness patterns and co-occurrence across variables, time, entities, and source systems.

For statistical analysis, MCAR/MAR/MNAR can be useful concepts, but do not infer a missingness mechanism from labels alone. The mechanism is an assumption about the data-generating/observation process and may require sensitivity analysis, especially with multiple incomplete variables. Preserve missingness indicators/provenance when absence itself may be informative.

Never choose imputation solely to eliminate nulls. Define what information the imputer may use, fit it only inside the permitted training partition when learned, and evaluate how the choice changes distributions and downstream conclusions.
## Leakage taxonomy
Treat leakage as any information path that makes training/evaluation data contain target-relevant information that would not legitimately be available at the prediction/decision point.

Check for:

- future timestamps or later revisions/backfills;
- post-outcome fields and direct/indirect target proxies;
- entity duplicates or linked records crossing train/evaluation boundaries;
- preprocessing, scaling, imputation, feature selection, or encoding fitted on evaluation data;
- target encodings or rolling aggregates whose windows include the current/future target;
- joins that select the latest record globally rather than latest-as-of the decision cutoff;
- overlapping labels/outcome windows across temporal splits;
- contract rolls, publication calendars, or external attributes chosen with future knowledge;
- manual cleaning decisions made after inspecting final evaluation outcomes.

Leakage prevention is a data-lineage property as much as a model-validation property. Record the availability rule for each high-risk feature and prove it with boundary examples.

## Distribution change
Compare distributions by time, source, entity segment, acquisition regime, and contract version. Distinguish likely defects from legitimate dataset shift, population change, regime change, instrumentation change, or policy change. Do not automatically "correct" a real distribution change into historical-looking data.

## Fitness disposition
For each material finding record evidence, affected scope, severity, confidence, likely cause, downstream impact, remediation, and whether the finding blocks the stated use. End with one of:

- `fit`: critical contract, cutoff, quality, and leakage requirements are satisfied;
- `fit-with-caveats`: limitations are bounded, explicit, and acceptable for the stated use;
- `not-fit`: a critical semantic, quality, leakage, or reconstruction requirement fails.

Research basis: Breck et al. (2019) on ML data validation; Kaufman, Rosset & Perlich (2011) on leakage; Quiñonero-Candela et al. (2008) on dataset shift; and missing-data methodology originating with Rubin and later refinements. See `research-evidence.md`.
