# Issue 132 implementation plan

## Goal
Consolidate the live Commodity data/model research specialist family into two repository-owned, progressively disclosed Tier 0 skills: `data-engineering` and `model-tuning`.

## Source-to-destination map

### data-engineering
Absorb the durable specialist knowledge from `data-engineer`, `dataset-auditor`, `commodity-market-data`, and `feature-engineer`, plus the data-pipeline portions of `time-series-research`. The already-adopted `workflow-architect` remains a general workflow specialist; its data-pipeline concepts are deliberately represented here so data-engineering does not require a second activation.

### model-tuning
Absorb the durable specialist knowledge from `experiment-designer`, `experiment-tracker`, `model-trainer`, `hyperparameter-optimizer`, `model-evaluator`, `neural-network-engineer`, `statistical-analyst`, `forecast-backtesting`, `reproducibility-auditor`, and the experiment/model portions of `time-series-research`.

## Progressive order
`data-engineering`: frame question -> understand sources/time semantics -> acquire/layer -> audit quality/leakage -> transform/features -> engineer pipeline -> experiment handoff -> verify reconstructability.

`model-tuning`: design experiment -> establish baseline -> train/adapt -> bounded hyperparameter search -> isolated evaluation/statistics -> time-series/backtesting when relevant -> tracking/reproducibility -> evidence-bounded research disposition.

## Runtime consolidation
After merge, synchronize the two accepted packages to the canonical workspace catalogue, retire only the 14 superseded domain-specific workspace entries listed above, refresh KIS discovery, and verify the intended two specialists are active and the superseded entries no longer appear.

## Acceptance
- Both packages satisfy the package/security/evaluation standards and live parser constraints.
- Full repository verification is green.
- Exact-head CI is green and merge is through KIS-controlled GitHub operations.
- Workspace sync/retirement is bounded and reversible.
- Live KIS catalogue exposes `data-engineering` and `model-tuning` and not the 14 superseded domain entries.
