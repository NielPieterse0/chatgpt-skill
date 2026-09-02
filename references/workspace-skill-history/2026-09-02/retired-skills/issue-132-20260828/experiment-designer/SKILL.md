---
name: experiment-designer
description: Use when turning a research question into a falsifiable ML or statistical experiment with explicit data boundaries, split strategy, baselines, controls, metrics, uncertainty, and promotion or decision criteria; include point-in-time and temporal semantics when ordered data makes them relevant.
---
# Experiment Designer

## Purpose
Design experiments so a positive result can survive leakage checks, baseline comparison, repeated runs, and independent review.

## Workflow
1. Write a falsifiable hypothesis and the research decision the experiment should inform.
2. Define the target or outcome and its measurement timing. When time matters, define the prediction or decision timestamp, target observation timestamp, horizon, and information cutoff before training.
3. Bind every dataset to an immutable identity, hash, or version; include as-of and vintage/revision identity when source data can change over time.
4. Define explicit training, validation, and test boundaries and the split strategy; use temporal boundaries for ordered forecasting tasks.
5. Bind feature definitions and preprocessing to immutable identities; fit learned preprocessing on training data only.
6. Choose the simplest credible baseline and at least one control that can expose false signal.
7. Predefine primary and secondary metrics, uncertainty method, failure criteria, leakage checks, seed policy, repeats, resource budget, and stopping criteria.
8. Define promotion or decision criteria that require robustness rather than peak score.

## Experiment Contract
Use the governing repository's experiment schema or contract when one exists. Otherwise record the required fields explicitly in the experiment artifact. Promotion is research or model evidence status only; operational authorization remains outside this skill.

## Failure Modes
Test-set tuning; weak baselines; leakage; future or revised data used as if historically available; implicit split boundaries; unversioned preprocessing; metric hunting; promotion from one favorable seed, fold, or period.