from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.skill_security import build_catalog, validate_repository

EXPECTED_ORIGIN = "https://github.com/example/chatgpt-skill.git"

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

def independent_skill_hash(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((p for p in skill_dir.rglob("*") if p.is_file() and p.name != "adoption-manifest.json"), key=lambda p: p.relative_to(skill_dir).as_posix()):
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8"); content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big")); digest.update(relative); digest.update(len(content).to_bytes(8, "big")); digest.update(content)
    return digest.hexdigest()

def default_policy() -> dict[str, object]:
    return {"schema_version":1,"authority":"docs/security/skill-adoption-security-standard.md","discovery":{"root":"skills","pattern":"skills/*/SKILL.md","max_depth":1,"excluded_roots":["references",".work"],"reject_symlinks":True,"reject_nested_skills":True},"git":{"required":True,"expected_origin":EXPECTED_ORIGIN,"allowed_origin_schemes":["https","ssh"]},"admission":{"allowed_tiers":[0,1,2],"reject_allowed_tools":True,"require_content_hash":True,"require_license_review":True,"require_human_approval":True,"require_rollback":True},"prohibited_capabilities":["lifecycle_hooks","network","credentials","external_mutations","runtime_installation","remote_mcp","git_publication","deployment","deletion"]}

def default_runtime(enabled: bool = True) -> dict[str, object]:
    return {"schema_version":1,"skills_enabled":enabled,"reason":"test","changed_at":"2026-07-26T00:00:00Z","changed_by":"test-suite"}

def create_repo(root: Path, *, enabled: bool = True) -> None:
    (root/"skills").mkdir(parents=True); (root/"references").mkdir(); write_json(root/"config"/"skill-security-policy.json",default_policy()); write_json(root/"config"/"runtime-control.json",default_runtime(enabled))

def create_skill(root: Path, name: str = "safe-skill", *, tier: int = 1, activation_mode: str = "model", capabilities: dict[str,bool] | None = None, allowed_tools: str | None = None, write_paths: list[str] | None = None) -> Path:
    skill_dir=root/"skills"/name; skill_dir.mkdir(parents=True)
    frontmatter=["---",f"name: {name}","description: Use this skill when a test needs a safe repository-read-only capability.","license: Apache-2.0"]
    if allowed_tools is not None: frontmatter.append(f"allowed-tools: {allowed_tools}")
    frontmatter.extend(["---","",f"# {name}","","Read repository files only.",""]); (skill_dir/"SKILL.md").write_text("\n".join(frontmatter),encoding="utf-8")
    flags={"lifecycle_hooks":False,"network":False,"credentials":False,"external_mutations":False,"runtime_installation":False,"remote_mcp":False,"git_publication":False,"deployment":False,"deletion":False}; flags.update(capabilities or {})
    manifest={"schema_version":1,"skill":name,"source":{"repository":"https://github.com/example/source.git","revision":"a"*40,"imported_at":"2026-07-26","content_sha256":independent_skill_hash(skill_dir)},"license":{"identifier":"Apache-2.0","reviewed":True},"risk":{"tier":tier,"capabilities":flags},"filesystem":{"read":["."],"write":[] if tier<2 else (write_paths if write_paths is not None else ["."]),"absolute_paths":False},"activation":{"mode":activation_mode,"requires_trusted_project":True,"requires_human_approval":tier>=2},"dependencies":{"locked":True,"runtime_installation":False},"approval":{"status":"approved","reviewer":"security-owner","reviewed_at":"2026-07-26"},"rollback":{"verified":True,"method":"Remove the skill directory and disable runtime."}}
    write_json(skill_dir/"adoption-manifest.json",manifest); return skill_dir

def refresh_manifest_hash(skill_dir: Path) -> None:
    path=skill_dir/"adoption-manifest.json"; manifest=json.loads(path.read_text(encoding="utf-8")); manifest["source"]["content_sha256"]=independent_skill_hash(skill_dir); write_json(path,manifest)

def error_codes(report: object) -> set[str]: return {issue.code for issue in report.errors}

class SkillSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name); create_repo(self.root)
    def tearDown(self) -> None: self.temp.cleanup()
    def test_valid_skill_is_admitted(self):
        create_skill(self.root); report=validate_repository(self.root,require_git=False); catalog=build_catalog(self.root,require_git=False); self.assertTrue(report.ok,report.to_dict()); self.assertEqual(["safe-skill"],[x["name"] for x in catalog["skills"]])
    def test_malformed_policy_fails_closed_without_exception(self):
        write_json(self.root/"config"/"skill-security-policy.json",{"schema_version":1}); report=validate_repository(self.root,require_git=False); self.assertFalse(report.ok); self.assertIn("POLICY_MISSING",error_codes(report))
    def test_reference_skill_is_never_discovered(self):
        create_skill(self.root); bad=self.root/"references"/"poisoned"/"SKILL.md"; bad.parent.mkdir(parents=True); bad.write_text("malicious reference content",encoding="utf-8"); report=validate_repository(self.root,require_git=False); catalog=build_catalog(self.root,require_git=False); self.assertTrue(report.ok,report.to_dict()); self.assertEqual(1,len(catalog["skills"]))
    def test_nested_skill_is_rejected(self):
        create_skill(self.root); nested=self.root/"skills"/"container"/"nested"/"SKILL.md"; nested.parent.mkdir(parents=True); nested.write_text("---\nname: nested\ndescription: nested test\n---\n",encoding="utf-8"); self.assertIn("NESTED_SKILL",error_codes(validate_repository(self.root,require_git=False)))
    def test_symlink_in_skill_tree_is_rejected(self):
        skill_dir=create_skill(self.root); target=skill_dir/"target.txt"; target.write_text("content",encoding="utf-8"); link=skill_dir/"linked.txt"
        try: os.symlink(target,link)
        except (OSError,NotImplementedError) as exc: self.skipTest(f"symlink unavailable: {exc}")
        self.assertIn("SYMLINK_REJECTED",error_codes(validate_repository(self.root,require_git=False)))
    def test_frontmatter_name_must_match_directory(self):
        d=create_skill(self.root); p=d/"SKILL.md"; p.write_text(p.read_text(encoding="utf-8").replace("name: safe-skill","name: other-skill"),encoding="utf-8"); self.assertIn("SKILL_NAME_MISMATCH",error_codes(validate_repository(self.root,require_git=False)))
    def test_allowed_tools_is_rejected(self):
        create_skill(self.root,allowed_tools="Bash(*)"); self.assertIn("ALLOWED_TOOLS_REJECTED",error_codes(validate_repository(self.root,require_git=False)))
    def test_missing_manifest_is_rejected(self):
        d=create_skill(self.root); (d/"adoption-manifest.json").unlink(); self.assertIn("MANIFEST_MISSING",error_codes(validate_repository(self.root,require_git=False)))
    def test_content_hash_mismatch_is_rejected(self):
        d=create_skill(self.root); (d/"SKILL.md").write_text((d/"SKILL.md").read_text(encoding="utf-8")+"changed\n",encoding="utf-8"); self.assertIn("CONTENT_HASH_MISMATCH",error_codes(validate_repository(self.root,require_git=False)))
    def test_prohibited_capability_is_rejected(self):
        create_skill(self.root,tier=3,activation_mode="explicit",capabilities={"network":True}); codes=error_codes(validate_repository(self.root,require_git=False)); self.assertIn("TIER_NOT_ALLOWED",codes); self.assertIn("PROHIBITED_CAPABILITY",codes)
    def test_tier_two_requires_explicit_activation_and_approval(self):
        create_skill(self.root,tier=2,activation_mode="model"); self.assertIn("ACTIVATION_MODE_INVALID",error_codes(validate_repository(self.root,require_git=False)))
    def test_kill_switch_returns_empty_catalog(self):
        create_skill(self.root); write_json(self.root/"config"/"runtime-control.json",default_runtime(False)); catalog=build_catalog(self.root,require_git=False); self.assertFalse(catalog["enabled"]); self.assertEqual([],catalog["skills"])
    def test_hook_artifact_is_rejected_even_when_manifest_claims_safe(self):
        d=create_skill(self.root); hooks=d/"hooks"/"hooks.json"; hooks.parent.mkdir(); hooks.write_text("{}\n",encoding="utf-8"); refresh_manifest_hash(d); self.assertIn("HAZARDOUS_ARTIFACT",error_codes(validate_repository(self.root,require_git=False)))
    def test_runtime_installation_pattern_is_rejected(self):
        d=create_skill(self.root); scripts=d/"scripts"; scripts.mkdir(); (scripts/"bootstrap.py").write_text("import subprocess\nsubprocess.run(['python', '-m', 'pip', 'install', 'unsafe'])\n",encoding="utf-8"); refresh_manifest_hash(d); self.assertIn("RUNTIME_INSTALLATION_PATTERN",error_codes(validate_repository(self.root,require_git=False)))
    def test_tier_two_allows_repository_root_write_scope(self):
        create_skill(self.root,tier=2,activation_mode="explicit",write_paths=["."]); self.assertTrue(validate_repository(self.root,require_git=False).ok)
    def test_tier_two_requires_non_empty_write_scope(self):
        create_skill(self.root,tier=2,activation_mode="explicit",write_paths=[]); self.assertIn("WRITE_SCOPE_INVALID",error_codes(validate_repository(self.root,require_git=False)))
    def test_tier_two_rejects_direct_git_metadata_write_scope(self):
        create_skill(self.root,tier=2,activation_mode="explicit",write_paths=[".git/**"]); self.assertIn("WRITE_SCOPE_INVALID",error_codes(validate_repository(self.root,require_git=False)))
    def test_tier_two_rejects_write_scope_traversal(self):
        create_skill(self.root,tier=2,activation_mode="explicit",write_paths=["../outside"]); self.assertIn("FILESYSTEM_SCOPE_INVALID",error_codes(validate_repository(self.root,require_git=False)))
    @unittest.skipUnless(shutil.which("git"),"git executable required")
    def test_git_origin_must_match_policy(self):
        create_skill(self.root); subprocess.run(["git","init"],cwd=self.root,check=True,capture_output=True); subprocess.run(["git","remote","add","origin","https://github.com/example/wrong.git"],cwd=self.root,check=True,capture_output=True); self.assertIn("GIT_ORIGIN_MISMATCH",error_codes(validate_repository(self.root,require_git=True)))

if __name__ == "__main__": unittest.main()
