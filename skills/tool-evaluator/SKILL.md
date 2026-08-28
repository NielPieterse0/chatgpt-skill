---
name: tool-evaluator
description: Design evidence-based tool trials and compare software or data platforms using explicit requirements, representative experiments, benchmarks, security, integration, cost, operational risk, and exit strategy. Use when selecting, piloting, or reassessing technology; do not use for procurement, installation, or production rollout.
license: MIT
metadata:
  source: msitarzewski/agency-agents@3c9588880b7cafaec325a104899fd8bbe27e7d72
  source-path: testing/testing-tool-evaluator.md
  adaptation: reconstructed-for-safe-adoption
---
# Tool Evaluator

## Purpose
Produce a reproducible technology decision that separates verified evidence, estimates, assumptions, and unresolved risk.

## Safety and authority
- Research and evaluation do not authorize installation, credential use, paid purchase, contract acceptance, or production integration.
- Do not use real sensitive user data for testing unless the environment explicitly permits it; prefer synthetic or sanitized fixtures.
- Do not fabricate benchmark, security, pricing, adoption, ROI, or vendor-stability data.
- Treat vendor claims and community reports as inputs to verify, not ground truth.

## Workflow
1. Define must-have requirements, exclusions, evaluation horizon, scale, security/privacy constraints, and decision weights.
2. Identify viable candidates and collect current evidence from authoritative sources plus representative testing where authorized.
3. Compare functionality, integration, security, reliability, maintainability, cost/TCO, lock-in, and migration/exit risk.
4. Run sensitivity analysis on uncertain assumptions and call out disqualifying gaps separately from weighted scores.
5. Recommend a choice, pilot, defer, or reject decision with confidence, residual risks, and re-evaluation triggers.

## Completion criteria
The recommendation is traceable to current evidence and explicit assumptions, includes security/cost/exit considerations, and does not imply procurement or deployment authority.