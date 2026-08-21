from __future__ import annotations

import base64
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skills_over_mcp_server.py"


def load_module():
    spec = importlib.util.spec_from_file_location("skills_over_mcp_server", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_skill(root: Path, name: str) -> Path:
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "scripts").mkdir()
    (skill / "assets").mkdir()
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Use this skill for MCP adapter tests.\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (skill / "scripts" / "probe.py").write_text(
        "from pathlib import Path\nPath('EXECUTED').write_text('bad')\n", encoding="utf-8"
    )
    (skill / "assets" / "blob.bin").write_bytes(b"\x00\x01\xffbinary")
    return skill


def request(module, method: str, *, request_id: int = 1, **params):
    params["_meta"] = {
        "io.modelcontextprotocol/protocolVersion": module.PROTOCOL_VERSION,
        "io.modelcontextprotocol/clientCapabilities": {
            "extensions": {module.EXTENSION_ID: {}}
        },
    }
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}


class SkillsOverMcpServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "skills"
        self.root.mkdir()
        self.alpha = make_skill(self.root, "alpha-skill")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_server_discover_declares_read_only_skills_extension(self) -> None:
        server = self.module.McpSkillServer(self.root)
        response = server.dispatch(request(self.module, "server/discover"))
        self.assertEqual(response["result"]["supportedVersions"], ["2026-07-28"])
        self.assertEqual(response["result"]["capabilities"]["resources"], {})
        self.assertEqual(
            response["result"]["capabilities"]["extensions"][self.module.EXTENSION_ID],
            {"directoryRead": False},
        )
        self.assertEqual(response["result"]["ttlMs"], 0)
        self.assertEqual(response["result"]["cacheScope"], "private")

    def test_skills_list_and_get_preserve_frontmatter_and_digests(self) -> None:
        server = self.module.McpSkillServer(self.root)
        listed = server.dispatch(request(self.module, "skills/list"))["result"]
        self.assertEqual(len(listed["skills"]), 1)
        skill = listed["skills"][0]
        self.assertEqual(skill["uri"], "skill://alpha-skill/SKILL.md")
        self.assertEqual(skill["frontmatter"]["name"], "alpha-skill")
        digests = {item["uri"]: item["digest"] for item in skill["resources"]}
        expected = hashlib.sha256((self.alpha / "SKILL.md").read_bytes()).hexdigest()
        self.assertEqual(digests[skill["uri"]], f"sha256:{expected}")

        fetched = server.dispatch(
            request(self.module, "skills/get", uri="skill://alpha-skill/SKILL.md")
        )["result"]["skill"]
        self.assertEqual(fetched, skill)

    def test_resources_read_preserves_text_and_binary_bytes(self) -> None:
        server = self.module.McpSkillServer(self.root)
        text = server.dispatch(
            request(self.module, "resources/read", uri="skill://alpha-skill/SKILL.md")
        )["result"]["contents"][0]
        self.assertEqual(text["text"], (self.alpha / "SKILL.md").read_bytes().decode("utf-8"))

        binary = server.dispatch(
            request(self.module, "resources/read", uri="skill://alpha-skill/assets/blob.bin")
        )["result"]["contents"][0]
        self.assertEqual(base64.b64decode(binary["blob"]), (self.alpha / "assets" / "blob.bin").read_bytes())

    def test_resources_list_is_deterministic_and_paginated(self) -> None:
        server = self.module.McpSkillServer(self.root, page_size=2)
        first = server.dispatch(request(self.module, "resources/list"))["result"]
        self.assertEqual(len(first["resources"]), 2)
        self.assertIn("nextCursor", first)
        second = server.dispatch(
            request(self.module, "resources/list", cursor=first["nextCursor"])
        )["result"]
        self.assertEqual(len(second["resources"]), 2)
        combined = first["resources"] + second["resources"]
        self.assertEqual(
            [item["uri"] for item in combined],
            sorted([item["uri"] for item in combined], key=str.casefold),
        )

    def test_cursor_fails_when_catalogue_snapshot_changes(self) -> None:
        make_skill(self.root, "beta-skill")
        server = self.module.McpSkillServer(self.root, page_size=1)
        first = server.dispatch(request(self.module, "skills/list"))["result"]
        self.assertIn("nextCursor", first)
        (self.alpha / "references" / "guide.md").write_text("changed\n", encoding="utf-8")
        second = server.dispatch(
            request(self.module, "skills/list", cursor=first["nextCursor"])
        )
        self.assertEqual(second["error"]["code"], -32602)
        self.assertIn("stale", second["error"]["message"])

    def test_unknown_and_traversal_like_uris_fail_closed(self) -> None:
        server = self.module.McpSkillServer(self.root)
        for uri in (
            "skill://alpha-skill/../secret.txt",
            "skill://missing-skill/SKILL.md",
            "file:///etc/passwd",
        ):
            response = server.dispatch(request(self.module, "resources/read", uri=uri))
            self.assertEqual(response["error"]["code"], -32002)

    def test_read_rejects_stale_digest_after_projection(self) -> None:
        projection = self.module.build_catalogue_projection(self.root)
        uri = "skill://alpha-skill/references/guide.md"
        (self.alpha / "references" / "guide.md").write_text("mutated\n", encoding="utf-8")
        with self.assertRaisesRegex(self.module.McpRequestError, "digest changed"):
            self.module._read_resource(
                self.root, projection, uri, max_resource_bytes=1024 * 1024
            )

    def test_resource_size_limit_fails_closed(self) -> None:
        server = self.module.McpSkillServer(self.root, max_resource_bytes=4)
        response = server.dispatch(
            request(self.module, "resources/read", uri="skill://alpha-skill/assets/blob.bin")
        )
        self.assertEqual(response["error"]["code"], -32003)

    def test_missing_current_protocol_metadata_is_rejected(self) -> None:
        server = self.module.McpSkillServer(self.root)
        response = server.dispatch(
            {"jsonrpc": "2.0", "id": 7, "method": "skills/list", "params": {}}
        )
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("_meta", response["error"]["message"])

    def test_reading_script_never_executes_it(self) -> None:
        marker = self.alpha / "EXECUTED"
        server = self.module.McpSkillServer(self.root)
        response = server.dispatch(
            request(self.module, "resources/read", uri="skill://alpha-skill/scripts/probe.py")
        )
        self.assertIn("Path('EXECUTED')", response["result"]["contents"][0]["text"])
        self.assertFalse(marker.exists())

    def test_stdio_returns_one_line_json_and_parse_errors(self) -> None:
        server = self.module.McpSkillServer(self.root)
        good = json.dumps(request(self.module, "server/discover"))
        stdin = io.StringIO("not-json\n" + good + "\n")
        stdout = io.StringIO()
        self.assertEqual(self.module.serve_stdio(server, stdin, stdout), 0)
        lines = stdout.getvalue().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["error"]["code"], -32700)
        self.assertIn("result", json.loads(lines[1]))


if __name__ == "__main__":
    unittest.main()
