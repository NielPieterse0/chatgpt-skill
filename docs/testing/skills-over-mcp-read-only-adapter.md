# Skills over MCP Read-only Adapter

## Scope

Issue #91 serves the active canonical workspace skill catalogue through a local, read-only MCP transport. It consumes the deterministic #90 catalogue projector and does not create a second catalogue, execute skill scripts, grant permissions, or change KIS governance.

Canonical catalogue input remains `C:\Projects\.agents\skills`. The adapter reads it dynamically for each request and treats the resulting URI/digest manifest as the only transport view for that request.

## Protocol source decision

The issue was written on 2026-08-16 with a `skill://index.json` catalogue resource in scope. Upstream SEP-2640 subsequently superseded that carrier: the current V1 proposal uses required `skills/list` and `skills/get`, per-file digest manifests, and ordinary MCP resource reads. The `skill://` scheme is conventional rather than privileged.

Current MCP protocol verification on 2026-08-21 also shows version `2026-07-28` is stateless: requests carry protocol version and client capabilities in `_meta`, and servers expose capabilities through `server/discover`.

Repository decision: implement the current V1 proposal rather than the superseded index shape, but label the adapter experimental until SEP-2640 is confirmed accepted/final upstream.
## Adapter contract

The local stdio adapter supports:

- `server/discover` for MCP `2026-07-28` capability discovery;
- `skills/list` with deterministic pagination and per-file SHA-256 manifests;
- `skills/get` for exact skill entrypoint URIs;
- `resources/list` as the ordinary MCP resource discovery surface;
- `resources/read` for exact projected resources.

Every request is re-bound to a freshly validated catalogue projection. Pagination cursors bind to the projection snapshot and fail if the catalogue changes between pages. Resource reads verify the bytes against the projected digest before returning them.

The server declares the `io.modelcontextprotocol/skills` extension without `directoryRead`. `resources/directory/read`, subscriptions, activation, skill execution, remote mutation, catalogue writes, and permission elevation are intentionally unsupported.

## Security boundary

Incoming URIs are never converted directly into filesystem paths. A read is allowed only when the URI exactly matches a resource emitted by the validated catalogue projection. The underlying #90 projector already rejects malformed packages, linked/reparse paths, identity mismatches, and case-folded URI collisions.
Reads are size-bounded and fail closed when the projected digest no longer matches the bytes read from disk. Text resources are returned as UTF-8 text; non-text resources are returned as base64 blobs so transport encoding does not alter canonical bytes.

## External integration boundary

This repository owns only the experimental adapter and its tests. No `kis-mcp` repository change is authorized. If KIS exposure requires server composition, registration, configuration, or capability changes, provide that work as a user-routed handoff with this adapter contract and its acceptance evidence.

## Verification target

Focused verification must cover discovery, `skills/list`, `skills/get`, exact resource reads, binary preservation, pagination/snapshot invalidation, traversal/unknown URI rejection, stale digest rejection, size bounds, malformed requests, and no script execution or writes.

Completion still requires the repository-wide `npm run verify`, skill-security validation, diff review, and exact-head GitHub verification before merge.

## Source verification

Verified 2026-08-21 against the MCP 2026-07-28 specification and Skills over MCP Working Group material. The latest located upstream status still described SEP-2640 as a V1 proposal awaiting the core-maintainer acceptance vote, so this repository does not claim the extension is final.
