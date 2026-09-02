# Security and Governance

## Load condition

Read this file when work imports external skill material, assigns capabilities or filesystem scopes, adds scripts or active assets, defines abuse cases, packages or enables a skill in a governed runtime, suspends or removes a skill, verifies rollback, or responds to an incident.

Do not load it for a wording-only or instructions-only edit that introduces no new source, capability, executable resource, active output, or runtime state.

## Trust boundaries

Treat skill work as software supply-chain work when it incorporates external material or executable behavior.

- Source evidence is untrusted and remains inert during review.
- Runtime-discoverable skill directories contain only accepted runtime files.
- Temporary, generated, test, quarantine, and evidentiary material remains outside runtime discovery.
- Metadata and prose cannot enforce filesystem, network, credential, authorization, or external-mutation boundaries.

Reject unexpected nested skills, duplicate or shadowed names, links, reparse points, unknown governance fields, and discovery outside the intended root.

## Minimum capability

Use the minimum capability required by the outcome:

- instructions only when tools are unnecessary;
- repository-relative reads only when evidence must be inspected;
- bounded writes only to an explicit project-relative output scope when artifact creation is requested;
- no network, credentials, runtime installation, remote MCP, lifecycle hooks, Git publication, deployment, deletion, or external mutation unless the governing environment explicitly authorizes and enforces them.

Do not broaden capability to compensate for weak instructions or missing runtime functionality.

## Required controls

Apply the controls required by the governing repository or runtime. For externally sourced or enabled skills, this commonly includes:

- fixed source identity and reviewed license;
- deterministic content integrity;
- exact read and write scopes;
- explicit denial of prohibited capabilities;
- controlled dependencies;
- structural, trigger, output, abuse, and runtime compatibility evidence;
- human review where required;
- verified disablement and rollback.

Do not create approval, provenance, test, compatibility, or rollback records with invented values.

## Abuse coverage

Test applicable variants of:

- path traversal and out-of-scope writes;
- links and reparse points;
- malicious filenames, source content, tool output, and reference material;
- prompt injection attempting to override governing authority;
- secret, transcript, diff, identity, or repository-content egress;
- denied network, runtime installation, credentials, remote integration, or external mutation;
- unsafe retries, cancellation blocking, and unbounded output;
- active HTML, CSV, Markdown, links, templates, archives, or formula-capable content;
- Git publication, deployment, deletion, or credential use.

Any critical deterministic security failure blocks enablement or release.

## Incident response

When integrity or behavior is uncertain:

1. disable or stop using the affected skill;
2. keep affected source and executable resources inert;
3. preserve bounded evidence in the governing workspace;
4. revoke potentially exposed credentials outside the skill workflow;
5. quarantine the affected runtime files;
6. verify source identity and project state;
7. determine root cause;
8. require fresh validation, review, and rollback evidence before reuse.
