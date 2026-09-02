# Training and adaptation

Load for model fitting, neural architecture work, fine-tuning, transfer learning, or parameter-efficient adaptation.

Record model family/architecture, configuration, seeds, hyperparameters, code/environment revision, hardware/resource budget, duration, diagnostics, checkpoint selection, early stopping, failures, and warnings. Never silently resume stale checkpoints or cached state.

For neural models, first establish a small baseline and confirm the pipeline can intentionally overfit a tiny sample. Track tensor shapes, target/activation/loss compatibility, parameter counts, initialization, optimizer, schedule, batch size, precision, gradients, and numerical stability before adding complexity.

For adaptation, pin base model and preprocessor identity, method, trainable parameter scope, adapter configuration, and resulting artifact. Compare architecture changes with controlled ablations and multiple seeds when variance matters.
