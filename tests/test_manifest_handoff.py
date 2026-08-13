import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.skill_security import validate_repository


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def skill_hash(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(
        (p for p in skill_dir.rglob("*") if p.is_file() and p.name != "adoption-manifest.json"),
        key=lambda p: p.relative_to(skill_dir).as_posix(),
    )
    for path in files:
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8")
        content = path.read_bytes()
        if path.suffix.lower() in {".md", ".txt", ".py", ".ps1", ".sh", ".bash", ".js", ".mjs", ".cjs", ".ts", ".json", ".yaml", ".yml", ".toml"}:
            content = content.replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def create_repo(root: Path) -> None:
    (root / "skills").mkdir(parents=True)
    (root / "references").mkdir()
    write_json(
        root / "config" / "skill-security-policy.json",
        {
            "schema_version": 1,
            "authority": "docs/security/skill-adoption-security-standard.md",
            "discovery": {"root": "skills", "pattern": "skills/*/SKILL.md", "max_depth": 1, "excluded_roots": ["references", ".work"], "reject_symlinks": True, "reject_nested_skills": True},
            "git": {"required": True, "expected_origin": "https://github.com/example/chatgpt-skill.git", "allowed_origin_schemes": ["https", "ssh"]},
            "admission": {"allowed_tiers": [0, 1, 2], "reject_allowed_tools": True, "require_content_hash": True, "require_license_review": True, "require_human_approval": True, "require_rollback": True},
            "prohibited_capabilities": ["lifecycle_hooks", "network", "credentials", "external_mutations", "runtime_installation", "remote_mcp", "git_publication", "deployment", "deletion"],
        },
    )
    write_json(root / "config" / "runtime-control.json", {"schema_version": 1, "skills_enabled": False, "reason": "test", "changed_at": "2026-08-13T00:00:00Z", "changed_by": "test"})


def create_skill(root: Path, provenance_type: str, handoff: object) -> Path:
    skill_dir = root / "skills" / "handoff-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: handoff-skill\ndescription: Use this skill for handoff validation tests.\n---\n\n# Handoff skill\n", encoding="utf-8")
    flags = {name: False for name in ["lifecycle_hooks", "network", "credentials", "external_mutations", "runtime_installation", "remote_mcp", "git_publication", "deployment", "deletion"]}
    manifest = {
        "schema_version": 2,
        "skill": "handoff-skill",
        "source": {
            "repository": "https://github.com/example/source.git",
            "revision": "a" * 40,
            "imported_at": "2026-08-13",
            "provenance_type": provenance_type,
            "handoff": handoff,
            "adopted_content_sha256": skill_hash(skill_dir),
        },
        "license": {"identifier": "Apache-2.0", "reviewed": True},
        "risk": {"tier": 1, "capabilities": flags},
        "filesystem": {"read": ["."], "write": [], "absolute_paths": False},
        "activation": {"mode": "model", "requires_trusted_project": True, "requires_human_approval": False},
        "dependencies": {"locked": True, "runtime_installation": False},
        "approval": {"status": "approved", "reviewer": "test", "reviewed_at": "2026-08-13"},
        "rollback": {"verified": True, "method": "Remove only the test skill directory."},
    }
    write_json(skill_dir / "adoption-manifest.json", manifest)
    return skill_dir


def codes(report: object) -> set[str]:
    return {item.code for item in report.errors}


class ManifestHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        create_repo(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_trusted_local_without_handoff_is_valid(self) -> None:
        create_skill(self.root, "trusted-local", None)
        report = validate_repository(self.root, require_git=False)
        self.assertTrue(report.ok, report.to_dict())

    def test_import_isolate_complete_handoff_is_valid(self) -> None:
        create_skill(self.root, "import-isolate", {"case_id": "20260813-example_ab12cd34", "artifact": "reviewed-skill", "artifact_sha256": "b" * 64})
        report = validate_repository(self.root, require_git=False)
        self.assertTrue(report.ok, report.to_dict())

    def test_import_isolate_requires_handoff(self) -> None:
        create_skill(self.root, "import-isolate", None)
        self.assertIn("HANDOFF_REQUIRED", codes(validate_repository(self.root, require_git=False)))

    def test_trusted_local_rejects_handoff(self) -> None:
        create_skill(self.root, "trusted-local", {"case_id": "case", "artifact": "artifact", "artifact_sha256": "b" * 64})
        self.assertIn("HANDOFF_UNEXPECTED", codes(validate_repository(self.root, require_git=False)))

    def test_handoff_digest_must_be_sha256(self) -> None:
        create_skill(self.root, "import-isolate", {"case_id": "case", "artifact": "artifact", "artifact_sha256": "not-a-digest"})
        self.assertIn("HANDOFF_DIGEST_INVALID", codes(validate_repository(self.root, require_git=False)))

    def test_handoff_digest_is_distinct_from_adopted_content_digest(self) -> None:
        skill_dir = create_skill(self.root, "import-isolate", {"case_id": "case", "artifact": "artifact", "artifact_sha256": "b" * 64})
        manifest = json.loads((skill_dir / "adoption-manifest.json").read_text(encoding="utf-8"))
        self.assertNotEqual(manifest["source"]["handoff"]["artifact_sha256"], manifest["source"]["adopted_content_sha256"])
        report = validate_repository(self.root, require_git=False)
        self.assertTrue(report.ok, report.to_dict())


if __name__ == "__main__":
    unittest.main()
