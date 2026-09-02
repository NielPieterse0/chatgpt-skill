# Scripts and Source Governance

## Load condition

Read this file when deciding whether to add an executable helper, dependency, one-off command, external source, portability claim, or source-maintenance control.

Do not load it for instructions-only work with no executable resource, dependency, external material, or portability claim.

## Choose the simplest execution form

| Need | Preferred form |
|---|---|
| One reliable reasoning or transformation step | No script |
| Short invocation of an existing permitted tool | Documented command |
| Repeated command with fragile quoting or many flags | Bounded wrapper |
| Repeated parsing, validation, conversion, or generation | Tested deterministic script |
| Destructive or stateful work | Plan, validation, dry run, explicit approval, bounded execution |

A script must earn its maintenance, dependency, portability, and attack-surface cost.

## Agent-oriented script contract

An admitted script must:

- be non-interactive;
- accept explicit command-line arguments, controlled environment values, stdin, or structured input files;
- provide concise `--help`, defaults, valid values, exit codes, and realistic examples;
- reject ambiguous inputs instead of guessing;
- emit structured results to stdout and diagnostics to stderr;
- state what failed, what was received, what was expected, and how to correct it;
- be idempotent, detect an existing result, or reject an unsafe retry;
- support a preview or dry run for stateful work;
- require explicit opt-in for destructive behavior;
- canonicalize paths and enforce the allowed repository-relative scope;
- reject traversal, links, reparse points, and unexpected file types;
- bound retries, time, processes, memory, and output where enforceable;
- avoid runtime installation, network access, inherited credentials, and ambient secrets;
- use locked, repository-supplied dependencies;
- have deterministic tests for normal and failure behavior.

Source scripts remain inert during assessment.

## External source review

Before copying or adapting external material, record:

1. canonical owner and source location;
2. immutable revision or equivalent fixed identity;
3. license and required notices;
4. complete content review, including hidden, linked, executable, and generated material;
5. filesystem, shell, network, connector, credential, and mutation requirements;
6. copied, rewritten, omitted, and added content;
7. structural, trigger, output, security, and compatibility evidence;
8. maintenance owner, update process, rollback, and removal.

Popularity, ranking, installation count, or a plausible name does not establish trust.

Do not execute imported scripts merely to understand them. Do not automatically synchronize upstream changes; reassess each revision deliberately.

## Portability claims

A portable package claim covers package structure and content only. Verify every claimed runtime separately for discovery, activation, permissions, relative paths, resource loading, context retention, and unsupported capabilities.

Load `agent-skill-support.md` when the task moves from a portability claim into runtime implementation.
