# Tracking and reproducibility

Load when model runs must be compared, reconstructed, or audited.

Assign stable experiment/run IDs. Record dataset/version/hash, point-in-time/vintage identity when relevant, split boundaries, code/environment identity, preprocessing/feature identity, model configuration, seeds, hyperparameters, metrics with units/split/context, checkpoints, predictions, reports, and stable artifact hashes. Preserve failed, interrupted, rejected, and superseded runs.

Audit hidden state: notebook edits, unrecorded caches, mutable external data, implicit environment variables, local files, resumed checkpoints, and order-dependent cells. Distinguish exact from statistical reproducibility; do not require bit-for-bit equality where the platform cannot guarantee it. Require bounded, decision-equivalent behavior and record tolerance.
