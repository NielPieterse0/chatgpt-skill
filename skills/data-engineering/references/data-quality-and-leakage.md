# Data quality and leakage

Load when deciding whether a dataset is fit for modeling, experimentation, inference, or evaluation.

Audit in this order: grain/keys/target/time semantics; completeness/uniqueness/validity/consistency/integrity/freshness/schema drift; join coverage and row multiplication; missingness, labels, duplicates, impossible values, outliers and distribution shift; then leakage.

Leakage checks include future timestamps, post-outcome fields, target proxies, duplicate entities across splits, full-data preprocessing, revised/backfilled information, overlapping labels, and hidden calendar/roll lookahead. Distinguish actual defects from legitimate regime, instrumentation, or population changes.

For each material finding record evidence, affected scope, severity, confidence, likely cause, downstream impact, and remediation. End with `fit`, `fit-with-caveats`, or `not-fit` for the stated use.
