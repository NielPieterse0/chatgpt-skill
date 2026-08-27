# Standalone Artifact Guidance

Use this reference only when KIS is not the repository's workflow authority and the repository does not already define artifact locations.

Prefer the repository's existing issue, task, change, specification, planning, or `.work` conventions. Do not create a parallel hierarchy merely because this skill is active.

For bounded work, a durable issue/task record or compact specification may be enough. For non-trivial work, keep requirements, implementation tasks, test/evidence expectations, review findings, and recovery information together or in the repository's normal split artifacts.

When no project convention exists, place temporary or working artifacts under the repository's existing temporary-work area (commonly `.work/`) rather than inventing a `superpowers` directory. Use neutral names based on the repository's work item, change, feature, or task identity.

Maintain enough traceability to connect requirements -> implementation tasks -> tests/evidence for non-trivial work. Code and tests implement requirements; they do not silently redefine them.

In KIS-managed repositories, ignore this fallback and use the current KIS-defined change/workspace structure and artifact locations.
