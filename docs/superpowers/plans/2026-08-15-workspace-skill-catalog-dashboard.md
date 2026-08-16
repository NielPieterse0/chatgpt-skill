# Workspace Skill Catalogue Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build issue #56 as a read-only local catalogue/evaluation/telemetry report and dashboard.

**Architecture:** Keep each evidence source isolated behind a small collector and merge immutable records in `report.py`. Use only Python standard library so the command runs in the repository without dependency installation; a minimal root bootstrap exposes the `src/` package to `python -m skill_catalog_dashboard`.

**Tech Stack:** Python 3.11 standard library, `unittest`, `sqlite3`, `http.server`.

## Global Constraints

- Lane B / issue #56 only; no lifecycle, evaluation-policy, catalogue mutation, or Work Management changes.
- Canonical skill content remains in the configured workspace catalogue; the repository stores no duplicate skill content.
- Missing or incomplete evidence stays explicit; telemetry is never treated as causal effectiveness evidence.
- Shared authority files remain untouched.

---

### Task 1: Catalogue model and discovery

**Files:** create `src/skill_catalog_dashboard/models.py`, `catalog.py`, `__init__.py`; test `tests/test_skill_catalog_dashboard.py`.

- [ ] Write failing discovery/frontmatter/multiple-root/determinism tests.
- [ ] Run the focused test and confirm feature-missing failure.
- [ ] Implement immutable models and bounded top-level frontmatter parsing/discovery.
- [ ] Rerun focused tests to green.

### Task 2: Repository and telemetry evidence

**Files:** create `src/skill_catalog_dashboard/repo.py`, `telemetry.py`; extend `tests/test_skill_catalog_dashboard.py`.

- [ ] Write failing adoption/evaluation/stale-hash and missing/SQLite/JSON telemetry tests.
- [ ] Run the focused tests and confirm expected failures.
- [ ] Implement deterministic repository evidence selection and read-only telemetry collectors.
- [ ] Rerun focused tests to green.

### Task 3: Report, CLI, and web dashboard

**Files:** create `src/skill_catalog_dashboard/report.py`, `web.py`, `__main__.py`; create root bootstrap `skill_catalog_dashboard/__init__.py`; extend tests.

- [ ] Write failing aggregation, CLI, JSON, and HTTP smoke tests.
- [ ] Run them and confirm expected failures.
- [ ] Implement report merging/serialization, CLI options, and GET-only local server.
- [ ] Rerun focused tests to green.

### Task 4: Verification and delivery

- [ ] Run `python -m unittest tests.test_skill_catalog_dashboard -v`.
- [ ] Run the complete repository test suite and project/security verification required by the repository.
- [ ] Smoke the literal CLI against `C:\Projects\.agents\skills` and the documented local KIS telemetry store.
- [ ] Inspect the issue-only diff, run scope/quality checks available through KIS, and correct any findings.
- [ ] Commit the issue #56 change, publish a review branch through registered GitHub workflow, and open a PR linked to #56 without merging unrelated work.
