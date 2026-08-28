# Pipelines and workflows

Load for multi-stage, scheduled, streaming, retrying, stateful, or failure-prone data processing.

Model explicit states and contracts for inputs, validation, transformations, outputs, handoffs, retries, partial writes, quarantine, recovery, and acceptance. Define branch conditions and observable evidence for each failure class.

Retries must be bounded and idempotent where state can be repeated. Separate documented intent from observed implementation; report drift rather than silently choosing one. Keep raw, cleaned, feature-ready, and evaluation-ready layers independently identifiable.

Use repository implementation/testing workflows to make code changes. This reference specifies data-workflow behavior; it does not grant execution or lifecycle authority.
