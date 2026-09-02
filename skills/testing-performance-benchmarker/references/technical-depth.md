# Performance Benchmarking Technical Depth

Load this reference when a change or system needs evidence about latency, throughput, saturation, resource use, scalability, endurance, or user-perceived performance. Establish the workload and requirement before choosing metrics or tools.

## Performance work starts with a baseline

Before optimizing, define:

- the user/system behavior being measured;
- the workload model and concurrency;
- environment and resource allocation;
- dataset size/distribution and cache state;
- dependency behavior;
- success/error correctness criteria;
- SLO/requirement or comparison objective;
- warm-up, run duration, repetitions, and statistical method.

A benchmark without a reproducible baseline is anecdote.

## Workload fidelity

Model traffic from actual or explicitly assumed behavior:

- operation/journey mix;
- arrival rate versus closed-loop virtual users;
- concurrency and think time;
- request/payload sizes;
- read/write ratio;
- tenant/key/data skew;
- cold/warm cache behavior;
- burst/spike patterns;
- background jobs and competing workloads;
- geography/network/device conditions where relevant.

Document synthetic assumptions. A benchmark can be useful before production data exists, but it must not be presented as real-user traffic.

## Benchmark classes

### Baseline / comparison

Measure stable representative behavior before and after a change with equivalent conditions.

### Load

Verify behavior at expected sustained and peak workloads.

### Stress

Increase demand until the system degrades or saturates to identify the limiting resource and failure mode.

### Spike

Test abrupt load transitions, autoscaling/recovery, queue buildup, and admission control.

### Endurance / soak

Run long enough to expose leaks, fragmentation, pool exhaustion, backlog accumulation, cache degradation, or periodic maintenance effects.

### Scalability / capacity

Measure how throughput/latency/resource cost change as workload and capacity change. Distinguish horizontal from vertical scaling and identify non-scaling shared dependencies.

## Metrics and distributions

Use distributions rather than averages alone.

Measure as relevant:

- latency percentiles/tail distribution;
- throughput/completions;
- error/rejection/timeout rate;
- queue wait/lag;
- CPU, memory, GC/allocation;
- disk/network I/O;
- database query/lock/connection-pool behavior;
- cache hit/miss/eviction;
- thread/event-loop/concurrency saturation;
- dependency latency/errors;
- cost/resource units per successful operation.

Check correctness under load. Throughput from failed or incomplete work is not useful capacity.

## Statistical discipline

Performance measurements contain noise. Improve confidence by:

- controlling environment/configuration and background activity;
- using warm-up appropriate to runtime/JIT/cache behavior;
- repeating comparable runs;
- reporting sample/run count and variance/intervals where useful;
- comparing distributions, not one best run;
- investigating outliers rather than discarding them without rationale;
- keeping candidate and baseline workload/configuration equivalent.

Do not claim “95% confidence” merely because a source phrase says so. Use an actual statistical method or report the observed run distribution plainly.

## Bottleneck attribution

Do not jump from a slow metric to an optimization. Correlate saturation and timing evidence across layers.

Typical questions:

- Is CPU saturated or mostly waiting on I/O/locks?
- Is tail latency caused by one dependency, queueing, GC, connection pools, or retries?
- Did a database plan/index/cardinality change?
- Is cache hit rate masking source load or causing stampede on miss?
- Does serialization/compression/copying dominate?
- Are network hops or third-party dependencies setting the lower bound?
- Does concurrency increase throughput until a knee, then only increase queueing?

Use profiler/query-plan/trace evidence where the governing environment permits it.

## Queueing and saturation

Watch for the knee where added concurrency stops increasing useful throughput and starts inflating latency/errors. Bound queues and concurrency so overload is visible and recoverable rather than hidden as unbounded waiting or memory growth.

Test recovery after overload: backlog drain, connection recovery, circuit/rate-limit behavior, autoscaling stabilization, and return to baseline latency/error levels.

## Database performance

Assess:

- query plans and scanned/returned row ratios;
- index selectivity and write cost;
- lock waits/deadlocks/contention;
- transaction duration/isolation;
- connection-pool saturation;
- N+1/repeated queries;
- replication lag;
- pagination/deep-offset behavior;
- migration/backfill load;
- cache interaction.

Do not prescribe a universal query-duration target. Tie it to the end-to-end budget and workload.

## Cache performance

Measure hit ratio plus origin load and correctness.

- cold versus warm cache;
- TTL/invalidation behavior;
- stampede/thundering herd;
- hot-key skew;
- cache memory/eviction;
- stale tolerance;
- behavior when cache is unavailable.

A faster cached path can still be an unacceptable design if consistency or tenant isolation breaks.

## Distributed systems and dependencies

Break end-to-end latency into service/dependency/queue segments. Include retry amplification, timeout budgets, and correlated failures. Measure downstream request multiplication: one incoming request may cause many internal calls.

Use traces when available to attribute tail latency across boundaries, but account for sampling.

## Web and user-perceived performance

For browser/frontend work, distinguish laboratory synthetic metrics from field/RUM data.

Relevant modern Core Web Vitals concepts include:

- Largest Contentful Paint (LCP) for loading experience;
- Interaction to Next Paint (INP) for responsiveness;
- Cumulative Layout Shift (CLS) for visual stability.

The upstream source still names First Input Delay (FID), which is legacy and should not be treated as the current responsiveness Web Vital. Thresholds and metric definitions can change; verify current authoritative web-performance documentation before policy/release claims.

Also consider TTFB, resource waterfalls, JS execution, hydration, image/font strategy, third-party scripts, network/device classes, and accessibility-related interaction cost where relevant.

## Capacity planning

Translate measured resource demand into a model:

- demand per successful unit of work;
- expected peak and growth assumptions;
- safe utilization headroom;
- scaling delay and minimum/maximum capacity;
- dependency quotas and hard limits;
- failure-domain redundancy;
- cost at expected and peak load.

Forecasts are conditional on assumptions. State them and test scaling policy under representative load when possible.

## Regression benchmarking

For performance-sensitive changes:

1. pin candidate and baseline identities;
2. run the same workload/config/data/environment;
3. verify functional correctness;
4. compare relevant distributions and resource metrics;
5. attribute meaningful regressions/improvements;
6. rerun enough to distinguish signal from noise;
7. record environment variance and unobservable factors.

Microbenchmarks are useful for isolated hot code but do not prove end-to-end improvement. System benchmarks can hide local regressions. Use the level matching the claim.

## Performance budgets and gates

A budget is valuable only when tied to product/system requirements and measured consistently. Avoid inheriting arbitrary source targets such as “200 ms,” “10x traffic,” “25% improvement,” or “under 10 minutes.” These may be useful examples, not universal acceptance criteria.

CI performance gates must account for environment noise; use stable benchmark infrastructure, tolerances/statistics, or trend analysis appropriate to the variance.

## Failure modes to challenge

- optimization before baseline/bottleneck evidence;
- average latency hiding tail failures;
- candidate and baseline run under different cache/data/environment states;
- load generator becoming the bottleneck;
- success metric ignoring errors or incorrect results;
- unrealistic constant request mix/data distribution;
- single-run improvement attributed to code despite noise;
- stress result with no recovery analysis;
- resource metric correlated with latency but assumed causal without attribution;
- synthetic browser metric presented as field-user experience;
- legacy FID or fixed source thresholds treated as current policy;
- benchmark tool execution against external/production targets without separate authority.

## Reporting

Include:

- claim/question and requirement;
- candidate/baseline identities;
- environment and workload model;
- run methodology/sample count;
- correctness/error outcomes;
- latency/throughput/resource distributions;
- saturation/bottleneck evidence;
- before/after deltas with uncertainty;
- scalability/recovery observations;
- optimization recommendation only when attributed;
- limitations and assumptions.

## Verification questions

- Is the workload representative or explicitly labeled synthetic?
- Are candidate and baseline conditions equivalent?
- Are percentiles, errors, and resource saturation reported together?
- Can the observed bottleneck be tied to a component/mechanism?
- Does the system recover after stress/spike/endurance conditions?
- Are thresholds requirement-derived and current?
- Are user-perceived conclusions supported by the correct synthetic/field evidence?

## Specification-to-TDD composition

Trace performance requirement → measurable acceptance criterion → workload/system invariant → owning bottleneck/boundary → smallest optimization behavior slice → appropriate benchmark/test → baseline/RED regression evidence → GREEN improvement with correctness preserved → REFACTOR → repeated comparison + broader load/recovery checks → independent review → fresh evidence → governing repository/KIS gate. This specialist does not authorize load against external or production systems.