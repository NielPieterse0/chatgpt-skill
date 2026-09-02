---
name: experiment-tracker
description: Use when experiments need stable experiment/run IDs, immutable dataset identities, metrics, checkpoints, artifacts, lineage, or comparison across repeated ML or statistical research runs, including point-in-time timing and data-vintage evidence when time matters.
---
# Experiment Tracker

## Purpose
Make every experiment queryable, comparable, and reconstructible without requiring a specific tracking vendor.

## Workflow
1. Assign stable `experiment_id` and `run_id` before training or evaluation starts.
2. Record immutable dataset version/hash and, when time matters, the as-of timestamp, forecast/decision timing, and vintage/revision identity.
3. Record explicit train/validation/test boundaries, code revision, environment identity, feature/preprocessing identity, model configuration, seeds, and hyperparameters.
4. Log metrics with names, units, split, step/time context, and optimization direction where relevant.
5. Record checkpoints, predictions, evaluation tables, reports, and other artifacts using stable identifiers and hashes.
6. Preserve failed, interrupted, rejected, and superseded runs with status and reason; do not keep only winners.
7. Link evaluation runs to the exact model/checkpoint and datasets they score.
8. Normalize records to the governing repository's experiment schema or contract when one exists; otherwise preserve a portable record containing the fields above.

## Backend Boundary
Tracking systems are adapters, not the experiment definition. The canonical record must remain portable enough to reconstruct comparison logic if the backend changes.

## Guardrails
Never log secrets or credentials. Never use mutable tags as sole identity. Never rewrite historical evidence. Research promotion is not deployment, execution, or trading approval.