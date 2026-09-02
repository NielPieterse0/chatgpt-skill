# Hyperparameter search

Load for tuning model parameters or model-coupled preprocessing declared inside an experiment. Data-engineering owns persisted dataset, feature, transformation, and preprocessing identities.

Require a fixed dataset version, validation protocol, baseline, primary metric, and compute budget. Model-tuning may vary only preprocessing that is part of the experiment's model configuration and is fitted independently inside each training split. If a proposed change alters persisted dataset or feature identity, return it to `data-engineering` and create a new immutable input version before continuing the comparison. Define the search space before trials, including conditional parameters and invalid combinations. Start bounded; use adaptive/Bayesian search only when it improves the practical experiment over a simple sweep.

Record completed, pruned, failed, and invalid trials with configuration, seed, metric, duration, and artifacts. Use pruning only when intermediate metrics are comparable. Check winner stability across seeds/folds/time windows. Re-evaluate only the selected configuration on the untouched final test set. Do not expand the search indefinitely after near-misses or treat validation-search significance as confirmatory evidence.
