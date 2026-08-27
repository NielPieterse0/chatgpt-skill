# Workflow Boundary

This reference exists for standalone use only. It is not a KIS lifecycle definition.

In a KIS-managed repository, use the current KIS workflow, state, transitions, approvals, verification, and closeout rules exactly as discovered from KIS and repository authority. Do not translate them into this file's terminology.

For repositories without KIS, a lightweight development flow is usually sufficient:

`understand -> specify -> plan -> implement -> review -> verify -> close`

Apply specialist methods at the relevant point rather than treating them as lifecycle transitions. For example, brainstorming strengthens specification/design work, TDD strengthens implementation, systematic debugging strengthens defect investigation, and verification-before-completion strengthens completion evidence.

Stop when authority conflicts, a required decision or approval is missing, destructive action lacks consent, or verification fails. Update requirements before implementing changed behavior, and rerun affected review or verification after later edits.
