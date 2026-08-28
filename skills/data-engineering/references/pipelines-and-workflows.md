# Pipelines and workflows

Load for multi-stage, scheduled, incremental, streaming, retrying, stateful, or failure-prone data processing.

## Pipeline contract
Define observable states and contracts for source acquisition, validation, transformation, output publication, downstream handoff, retry, backfill/replay, quarantine, recovery, and acceptance. For every stage specify inputs, outputs, invariants, failure classes, and evidence of success.

Do not let orchestration semantics substitute for data semantics. A successful task run is not evidence that its output contract, cutoff rules, or quality invariants passed.

## Idempotency and atomicity
For the same immutable inputs, contract version, parameters, and code/configuration identity, an idempotent pipeline should produce the same declared logical output without duplicate side effects.

- Use stable business/event keys rather than arrival order when deduplicating.
- Detect already-applied writes or make repeated application converge to the same state.
- Stage outputs and expose them atomically when partial visibility would mislead consumers.
- Make retry behavior explicit for each external or stateful boundary.
- Do not claim exactly-once semantics unless the complete source-processing-sink path provides it; otherwise describe the actual at-least-once/effectively-once guarantees and deduplication strategy.

## Incremental processing, CDC, and replay
Incremental pipelines must define their change key/version semantics, deletion/tombstone behavior, ordering assumptions, and replay window. A checkpoint is operational state, not historical truth; preserve enough immutable source evidence to rebuild from a known boundary.

Backfills must be distinguishable from normal arrivals. Record why they occurred, what event/availability timestamps they carry, and whether they are corrections, late arrivals, or newly discovered historical data. Replaying a later correction into an old decision-time feature set can create look-ahead even when the pipeline is mechanically correct.
## Streaming and late-arriving data
Define event time, processing time, allowed lateness, ordering behavior, watermark/finality policy, deduplication identity, and correction strategy. A watermark is an operational completeness assumption, not proof that no later event can arrive.

Specify what happens when data arrive after a window is considered complete: revise prior output, emit a correction, quarantine, or preserve both versions. Downstream consumers must be able to distinguish provisional from final/corrected results when that distinction matters.

## Schema and contract changes
Detect contract drift before publication. Decide whether to reject, quarantine, adapt through an explicit migration, or publish a new contract version. Storage-engine schema merge does not establish semantic compatibility.

## Observability
Track signals that diagnose data correctness, not only infrastructure health:

- freshness and availability lag;
- source and output row counts;
- contract/schema violations;
- duplicate and unmatched-key rates;
- missingness by reason;
- late-arrival and correction counts;
- distribution/drift indicators;
- quarantine/reject counts;
- dataset/content identities and contract versions emitted by each run.

Alert thresholds should follow the use contract and historical variability. Avoid universal percentages that are unrelated to business/research impact.

## Cost and resource trade-offs
Prefer incremental/CDC/reuse when they preserve correctness and materially reduce compute, storage, transfer, or latency. Quantify cost/latency trade-offs when evidence is available. Never sacrifice replayability, point-in-time correctness, or validation merely to reduce runtime cost.

Use repository implementation/testing workflows for code changes. This reference describes specialist data-pipeline behavior; it grants no execution, network, mutation, deployment, or lifecycle authority.
