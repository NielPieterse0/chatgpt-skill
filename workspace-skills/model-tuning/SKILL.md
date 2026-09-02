---
name: model-tuning
description: Design, train, tune, compare, and validate statistical, machine-learning, neural, or forecasting models with controlled experiments, hyperparameter search, uncertainty, backtesting, tracking, and reproducibility. Use after data inputs are defined; use data-engineering for source, dataset, feature, lineage, or pipeline construction.
---
# Model Tuning Specialist

## Purpose
Turn a fixed, auditable dataset into reproducible model evidence: a falsifiable experiment, controlled training, bounded tuning, isolated evaluation, and a defensible research disposition.

## Default sequence
1. **Design the experiment before fitting.** State the hypothesis, decision, target timing, immutable dataset identity, split strategy, baseline, controls, metrics, uncertainty method, leakage checks, seed/repeat policy, resource budget, stopping criteria, and research promotion criteria. Load `references/experiment-design.md` for new studies or materially changed protocols.
2. **Establish the simplest credible baseline.** Confirm the data/split contract and produce a comparable baseline before architecture or tuning complexity.
3. **Train traceably.** Record model family/configuration, seeds, hyperparameters, code/environment identity where governed, hardware/resource budget, diagnostics, checkpoint rule, failures, and selected checkpoint. Load `references/training-and-adaptation.md` for classical ML, neural training, transfer learning, fine-tuning, or parameter-efficient adaptation.
4. **Tune within a bounded search.** Predefine search space, conditional/invalid combinations, optimization metric, validation protocol, trial budget, pruning rule, and stopping rule. Load `references/hyperparameter-search.md` for sweeps, Bayesian/adaptive searches, pruning, or parameterization studies.
5. **Evaluate on isolated evidence.** Compare against predefined baselines using the same protocol; report primary metric with uncertainty, secondary metrics, segment errors, robustness, and caveats. Load `references/evaluation-and-statistics.md` for statistical comparisons, uncertainty, multiple testing, robustness, or final model disposition.
6. **Evaluate temporal/decision consequences separately.** Load `references/time-series-and-backtesting.md` for ordered forecasting, market regimes, signal/policy evaluation, or execution-aware simulation. Keep predictive evaluation distinct from downstream policy/simulation and from live authorization.
7. **Track and reproduce.** Load `references/tracking-and-reproducibility.md` when runs, checkpoints, predictions, metrics, or environment evidence must be compared or reconstructed. Preserve failed, interrupted, rejected, and superseded runs.
8. **Conclude only what the evidence supports.** Research promotion is evidence status, not deployment, trading, procurement, or lifecycle authorization.

## Critical rules
- Never tune, select checkpoints, engineer model decisions, or choose thresholds against the untouched final test set.
- Do not promote from one favorable seed, fold, period, or trial when variance can change the conclusion.
- Keep persisted dataset, feature, split, and preprocessing identities fixed during a comparison unless the experiment explicitly studies them. Experiment-local model-coupled preprocessing may vary only when fitted independently inside each training split; any change to persisted dataset or feature identity returns to `data-engineering` as a new immutable input version.
- Report effect size and uncertainty; significance alone is not practical importance.
- Treat repeated experimentation and multiple comparisons as evidence risks.

## Boundary
Own experiment design, model fitting/adaptation, tuning/parameterization, model evaluation, statistical comparison, forecast backtesting, run tracking, and reproducibility of model evidence. Use `data-engineering` for source semantics, dataset construction, quality, feature generation, lineage, and pipeline engineering. Do not infer deployment, live trading, Git publication, procurement, or project-lifecycle authority.
