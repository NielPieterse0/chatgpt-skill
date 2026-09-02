---
name: systematic-debugging
description: Use when a bug, failing test, regression, performance anomaly, or other unexpected behavior needs a root-cause investigation before a fix is proposed.
license: MIT
---

# Systematic Debugging

Find evidence for the root cause before changing production behavior.

## Iron law

Do not propose a fix until you can state a supported causal hypothesis for the observed failure. Symptom suppression is not root-cause resolution.

## Phase 1: Root-cause investigation

1. Reproduce the failure consistently or define what evidence is missing when reproduction is intermittent.
2. Read the complete error, stack, failing assertion, logs, and recent relevant change context.
3. Trace incorrect values or state backward through component boundaries until you find where expected and actual behavior diverge.
4. Instrument boundaries when needed to distinguish where bad state is introduced from where it is merely observed.

## Phase 2: Pattern analysis

Compare a working case with the failing case. List meaningful differences in input, environment, sequencing, state, version, configuration, or dependency behavior. Do not guess which difference matters before testing it.

## Phase 3: Hypothesis and test

State one falsifiable hypothesis. Run the smallest experiment that can disprove it. Change one variable at a time and record the result.## Phase 4: Implement the supported fix

Once the cause is supported:

1. create or identify the smallest failing regression case when applicable;
2. use `test-driven-development` for the behavior-changing fix;
3. change the root cause rather than adding unrelated defenses around symptoms;
4. verify the original failure, the new regression test, and relevant surrounding behavior.

If three attempted fixes fail, stop stacking patches. Treat that as evidence the current causal model is wrong and return to investigation, architecture, or instrumentation.

## Red flags

- Editing code immediately after reading only the final error line.
- Weakening or skipping a test to make the failure disappear.
- Adding arbitrary waits without evidence that timing is the cause.
- Changing several variables at once and losing the ability to learn from the result.
- Calling a workaround a root-cause fix without tracing how the failure arose.

## Boundaries

Do not depend on bundled shell helpers or a particular debugger. Use repository-provided diagnostics and tools. In KIS-managed repositories, KIS governs execution and repository mutation where applicable; this skill supplies the debugging method. Use `verification-before-completion` before claiming the defect is fixed.