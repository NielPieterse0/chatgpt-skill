# Candidate Intake Queue

This is a repository-owned **non-discovery** queue for skill and plugin candidates. It records intake/review state only; nothing under this tree becomes a canonical skill, runtime capability, installed plugin, or activated component by being present here.

Each durable candidate uses:

```text
intake/candidates/<candidate-id>/intake-record.json
```

`candidate-id` must match the directory name. Every record links to an exact `NielPieterse0/chatgpt-skill` source issue and records Work Management projection state separately.

External web/GitHub acquisition is outside this repository. Use `provenance.type = "import-isolate"`; before a finalized handoff exists, keep provenance `pending`. A verified external candidate must bind the finalized `case_id`, artifact name, artifact SHA-256, immutable source revision, and candidate SHA-256.

Explicitly trusted local candidates use `provenance.type = "trusted-local"` and no import-isolate handoff. Verified trusted-local provenance still requires immutable revision and candidate SHA-256 evidence.

Run:

```powershell
python scripts/intake_queue.py validate --repo-root .
python scripts/intake_queue.py report --repo-root .
```

The dashboard consumes this queue read-only and keeps intake candidates separate from canonical skill totals. Work Management projection gaps remain visible; they do not authorize a repository-local shadow lifecycle state.
