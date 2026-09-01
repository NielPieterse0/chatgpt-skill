# Technical Depth

## Core concerns
- representative workload and data shape
- warmup steady state and cache state
- concurrency arrival rate and backpressure
- p50 p95 p99 and tail distributions
- throughput saturation and queueing
- CPU memory IO network and lock contention
- baseline variance confidence and regression thresholds
- profiling attribution and capacity headroom

## Method
- define the user-visible or system performance question first
- fix hardware software data and background-load conditions where possible
- separate warmup from measured steady state
- vary load across realistic concurrency or arrival-rate points
- record distributions not only means
- correlate latency with resource saturation and queue depth
- repeat enough to characterize normal variance before declaring regression
- profile only after a reproducible bottleneck is established

## Failure modes to challenge
- single-run before/after claims
- mean latency hiding tail regression
- benchmark data too small for real access patterns
- coordinated omission in load generation
- uncontrolled cache or JIT warmup differences
- throughput compared at unequal concurrency
- microbenchmark used to infer end-to-end capacity
- optimization without bottleneck attribution

## Verification questions
- baseline and candidate use equivalent controlled conditions
- warmup and measurement windows are explicit
- latency distribution and throughput are both reported when relevant
- saturation point is identified or bounded
- variance is visible across repeats
- resource signals support bottleneck attribution
- regression criterion is tied to user/SLO impact
- limitations and unobservable production factors are stated

## SDD to TDD composition
When implementation follows a specification, preserve this trace: requirement -> observable acceptance criterion -> domain invariant/system behavior -> owning module or architectural boundary -> smallest independently deliverable behavior slice -> lowest appropriate test level -> concrete failing test -> RED -> GREEN -> REFACTOR -> boundary/contract/integration checks -> independent review -> focused verification -> repository/KIS gate. Select only the portions owned by this specialist; do not duplicate lifecycle authority.
