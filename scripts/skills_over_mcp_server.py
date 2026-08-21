#!/usr/bin/env python3
"""Serve the canonical workspace skill catalogue through a read-only MCP stdio adapter."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import sys
from pathlib import Path
from typing import IO, Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for candidate in (ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from scripts.skills_over_mcp_catalogue import build_catalogue_projection
from scripts.skills_over_mcp_compat import _is_link_like

PROTOCOL_VERSION = "2026-07-28"
EXTENSION_ID = "io.modelcontextprotocol/skills"
DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_RESOURCE_BYTES = 1024 * 1024
_TEXT_SUFFIXES = {".css", ".csv", ".html", ".js", ".json", ".md", ".py", ".txt", ".yaml", ".yml"}


class McpRequestError(ValueError):
    def __init__(self, message: str, *, code: int = -32602) -> None:
        super().__init__(message)
        self.code = code


def _cached(result: dict[str, Any]) -> dict[str, Any]:
    result["resultType"] = "complete"
    result["ttlMs"] = 0
    result["cacheScope"] = "private"
    return result


def _request_params(request: dict[str, Any]) -> dict[str, Any]:
    params = request.get("params", {})
    if not isinstance(params, dict):
        raise McpRequestError("params must be an object")
    meta = params.get("_meta")
    if not isinstance(meta, dict):
        raise McpRequestError("params._meta is required")
    if meta.get("io.modelcontextprotocol/protocolVersion") != PROTOCOL_VERSION:
        raise McpRequestError("unsupported MCP protocol version", code=-32001)
    if not isinstance(meta.get("io.modelcontextprotocol/clientCapabilities"), dict):
        raise McpRequestError("client capabilities are required")
    return params


def _cursor(snapshot: str, offset: int) -> str:
    raw = f"{snapshot}:{offset}".encode("ascii")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _cursor_offset(value: str | None, snapshot: str) -> int:
    if value is None:
        return 0
    if not isinstance(value, str) or not value:
        raise McpRequestError("cursor must be a non-empty string")
    try:
        padded = value + "=" * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")
        cursor_snapshot, raw_offset = decoded.rsplit(":", 1)
        offset = int(raw_offset)
    except (ValueError, UnicodeError) as exc:
        raise McpRequestError("cursor is malformed") from exc
    if cursor_snapshot != snapshot:
        raise McpRequestError("cursor snapshot is stale")
    if offset < 0:
        raise McpRequestError("cursor offset must not be negative")
    return offset


def _page(items: list[dict[str, Any]], params: dict[str, Any], snapshot: str, page_size: int) -> dict[str, Any]:
    offset = _cursor_offset(params.get("cursor"), snapshot)
    if offset > len(items):
        raise McpRequestError("cursor offset exceeds result set")
    end = min(offset + page_size, len(items))
    result: dict[str, Any] = {"items": items[offset:end]}
    if end < len(items):
        result["nextCursor"] = _cursor(snapshot, end)
    return result


def _skill_entry(item: dict[str, Any]) -> dict[str, Any]:
    entry = item["skill_entry"]
    assert isinstance(entry, dict)
    return {
        "uri": entry["uri"],
        "frontmatter": entry["frontmatter"],
        "resources": entry["resources"],
    }


def _resource_index(catalog_root: Path, projection: dict[str, Any]) -> dict[str, tuple[Path, str, str]]:
    index: dict[str, tuple[Path, str, str]] = {}
    for item in projection["skills"]:
        skill_id = str(item["skill_id"])
        entry = item["skill_entry"]
        assert isinstance(entry, dict)
        for resource in entry["resources"]:
            uri = str(resource["uri"])
            prefix = f"skill://{skill_id}/"
            if not uri.startswith(prefix):
                raise ValueError(f"projected resource escaped skill namespace: {uri}")
            relative = uri[len(prefix) :]
            if not relative or relative.startswith("/") or "\\" in relative:
                raise ValueError(f"unsupported projected resource path: {uri}")
            path = catalog_root / skill_id / Path(relative)
            media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            index[uri] = (path, str(resource["digest"]), media_type)
    return index


def _resource_list(projection: dict[str, Any]) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    for item in projection["skills"]:
        skill_id = str(item["skill_id"])
        entry = item["skill_entry"]
        assert isinstance(entry, dict)
        for resource in entry["resources"]:
            uri = str(resource["uri"])
            relative = uri.split(f"skill://{skill_id}/", 1)[1]
            media_type = mimetypes.guess_type(relative)[0] or "application/octet-stream"
            resources.append({"uri": uri, "name": f"{skill_id}/{relative}", "mimeType": media_type})
    resources.sort(key=lambda item: str(item["uri"]).casefold())
    return resources


def _read_resource(
    catalog_root: Path,
    projection: dict[str, Any],
    uri: str,
    *,
    max_resource_bytes: int,
) -> dict[str, Any]:
    record = _resource_index(catalog_root, projection).get(uri)
    if record is None:
        raise McpRequestError("resource URI is not served", code=-32002)
    path, expected_digest, media_type = record
    if _is_link_like(path):
        raise McpRequestError("resource path became linked or reparsed", code=-32002)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise McpRequestError("resource is no longer readable", code=-32002) from exc
    if len(data) > max_resource_bytes:
        raise McpRequestError("resource exceeds configured byte limit", code=-32003)
    observed = "sha256:" + hashlib.sha256(data).hexdigest()
    if observed != expected_digest:
        raise McpRequestError("resource digest changed after projection", code=-32004)
    content: dict[str, Any] = {"uri": uri, "mimeType": media_type}
    if path.suffix.casefold() in _TEXT_SUFFIXES:
        try:
            content["text"] = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise McpRequestError("text resource is not valid UTF-8", code=-32005) from exc
    else:
        content["blob"] = base64.b64encode(data).decode("ascii")
    return _cached({"contents": [content]})


class McpSkillServer:
    def __init__(self, catalog_root: Path, *, page_size: int = DEFAULT_PAGE_SIZE, max_resource_bytes: int = DEFAULT_MAX_RESOURCE_BYTES) -> None:
        if page_size < 1 or page_size > 1000:
            raise ValueError("page size must be between 1 and 1000")
        if max_resource_bytes < 1:
            raise ValueError("max resource bytes must be positive")
        self.catalog_root = Path(catalog_root)
        self.page_size = page_size
        self.max_resource_bytes = max_resource_bytes

    def _projection(self) -> dict[str, Any]:
        return build_catalogue_projection(self.catalog_root)

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any] | None:
        request_id = request.get("id")
        if request.get("jsonrpc") != "2.0":
            return self._error(request_id, -32600, "invalid JSON-RPC request")
        method = request.get("method")
        if not isinstance(method, str):
            return self._error(request_id, -32600, "method must be a string")
        if request_id is None:
            return None
        try:
            params = _request_params(request)
            projection = self._projection()
            snapshot = str(projection["catalogue"]["snapshot_sha256"])
            if method == "server/discover":
                return self._result(request_id, self._discover())
            if method == "skills/list":
                skills = [_skill_entry(item) for item in projection["skills"]]
                page = _page(skills, params, snapshot, self.page_size)
                result = {"skills": page.pop("items"), **page}
                return self._result(request_id, _cached(result))
            if method == "skills/get":
                return self._result(request_id, self._skills_get(projection, params))
            if method == "resources/list":
                page = _page(_resource_list(projection), params, snapshot, self.page_size)
                result = {"resources": page.pop("items"), **page}
                return self._result(request_id, _cached(result))
            if method == "resources/read":
                uri = params.get("uri")
                if not isinstance(uri, str) or not uri:
                    raise McpRequestError("resources/read requires a URI")
                return self._result(request_id, _read_resource(
                    self.catalog_root, projection, uri, max_resource_bytes=self.max_resource_bytes
                ))
            return self._error(request_id, -32601, "method not found")
        except McpRequestError as exc:
            return self._error(request_id, exc.code, str(exc))
        except (OSError, ValueError) as exc:
            return self._error(request_id, -32000, str(exc))

    def _discover(self) -> dict[str, Any]:
        return _cached({
            "supportedVersions": [PROTOCOL_VERSION],
            "capabilities": {
                "resources": {},
                "extensions": {EXTENSION_ID: {"directoryRead": False}},
            },
            "instructions": (
                "Read-only experimental Agent Skills catalogue. Discover skills with skills/list, "
                "confirm one with skills/get, and fetch exact resources with resources/read."
            ),
            "_meta": {
                "io.modelcontextprotocol/serverInfo": {
                    "name": "chatgpt-skill-read-only-adapter",
                    "version": "0.1.0-experimental",
                }
            },
        })

    def _skills_get(self, projection: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        uri = params.get("uri")
        if not isinstance(uri, str) or not uri:
            raise McpRequestError("skills/get requires a URI")
        for item in projection["skills"]:
            entry = _skill_entry(item)
            if entry["uri"] == uri:
                return _cached({"skill": entry})
        raise McpRequestError("skill URI is not served", code=-32002)

    @staticmethod
    def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def serve_stdio(server: McpSkillServer, stdin: IO[str], stdout: IO[str]) -> int:
    for line in stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                response = server._error(None, -32600, "JSON-RPC message must be an object")
            else:
                response = server.dispatch(request)
        except json.JSONDecodeError:
            response = server._error(None, -32700, "parse error")
        if response is not None:
            stdout.write(json.dumps(response, separators=(",", ":"), ensure_ascii=False) + "\n")
            stdout.flush()
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the canonical Agent Skills catalogue over read-only MCP stdio.")
    parser.add_argument("--catalog-root", required=True, type=Path)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--max-resource-bytes", type=int, default=DEFAULT_MAX_RESOURCE_BYTES)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    server = McpSkillServer(
        args.catalog_root,
        page_size=args.page_size,
        max_resource_bytes=args.max_resource_bytes,
    )
    return serve_stdio(server, sys.stdin, sys.stdout)


if __name__ == "__main__":
    raise SystemExit(main())
