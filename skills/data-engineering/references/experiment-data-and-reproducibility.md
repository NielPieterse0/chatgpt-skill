# Experiment data and reproducibility

Load when preparing datasets for repeated modeling experiments or auditing whether inputs can be reconstructed.

Record immutable dataset hash/version, source snapshots, split boundaries, preprocessing fit scope, feature identity, code/environment revision when governed by the repository, seeds where relevant, lineage, and material exclusions. Preserve failed/rejected dataset versions rather than rewriting history.

For ordered data, use chronological, expanding-window, or rolling-window splits unless a random split is explicitly justified as a non-forecast diagnostic. Keep validation/test periods isolated from feature-design and model-selection decisions.

The data-engineering completion test is reconstructability: a reviewer can determine what information was available at the stated cutoff, which transformations produced the dataset, and whether it was fit for its stated downstream use.
