#!/usr/bin/env python3
"""Fail-closed security gate for repository-owned Agent Skills.

The validator intentionally uses only the Python standard library. It never
executes skill scripts and never scans the untrusted reference corpus for
runtime discovery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse

POLICY_PATH = Path("config/skill-security-policy.json")
RUNTIME_CONTROL_PATH = Path("config/runtime-control.json")
MANIFEST_NAME = "adoption-manifest.json"
SKILL_FILE_NAME = "SKILL.md"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_REVISION_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

CAPABILITY_NAMES = (
    "lifecycle_hooks", "network", "credentials", "external_mutations", "runtime_installation",
    "remote_mcp", "git_publication", "deployment", "deletion",
)
HAZARDOUS_ARTIFACT_NAMES = {"hooks.json", ".mcp.json"}
HAZARDOUS_DIRECTORY_NAMES = {"hooks", ".claude-plugin"}
TEXT_SCAN_SUFFIXES = {".md", ".txt", ".py", ".ps1", ".sh", ".bash", ".js", ".mjs", ".cjs", ".ts", ".json", ".yaml", ".yml", ".toml"}
RUNTIME_INSTALLATION_PATTERNS = (
    re.compile(r"\bpython(?:3(?:\.\d+)?)?\s+-m\s+pip\s+install\b", re.IGNORECASE),
    re.compile(r"\bpip(?:3)?\s+install\b", re.IGNORECASE),
    re.compile(r"\bnpm\s+(?:install|i)\b", re.IGNORECASE),
    re.compile(r"\b(?:npx|bunx|uvx)\b", re.IGNORECASE),
    re.compile(r"\bdeno\s+run\s+(?:npm:|jsr:|https?://)", re.IGNORECASE),
    re.compile(r"\bbundler/inline\b", re.IGNORECASE),
)
PROHIBITED_OPERATION_PATTERNS = (
    re.compile(r"\bgit\s+push\b", re.IGNORECASE), re.compile(r"\bgh\s+pr\s+create\b", re.IGNORECASE),
    re.compile(r"\bkubectl\s+(?:apply|delete)\b", re.IGNORECASE), re.compile(r"\bterraform\s+apply\b", re.IGNORECASE),
    re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|pwsh|powershell)\b", re.IGNORECASE),
    re.compile(r"\brm\s+-rf\b", re.IGNORECASE), re.compile(r"\bRemove-Item\b[^\n]*\b-Recurse\b", re.IGNORECASE),
)
NETWORK_EXECUTION_PATTERNS = (
    re.compile(r"\b(?:curl|wget)\s+https?://", re.IGNORECASE), re.compile(r"\bInvoke-(?:WebRequest|RestMethod)\b", re.IGNORECASE),
    re.compile(r"\brequests\.(?:get|post|put|patch|delete)\s*\(", re.IGNORECASE),
    re.compile(r"\bhttpx\.(?:get|post|put|patch|delete)\s*\(", re.IGNORECASE), re.compile(r"\burllib\.request\.", re.IGNORECASE),
)

@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    path: str | None = None
    def to_dict(self) -> dict[str, str]:
        result = {"code": self.code, "message": self.message}
        if self.path is not None:
            result["path"] = self.path
        return result

@dataclass
class ValidationReport:
    repo_root: Path
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    skills: list[dict[str, Any]] = field(default_factory=list)
    runtime_enabled: bool = False
    @property
    def ok(self) -> bool: return not self.errors
    def add_error(self, code: str, message: str, path: Path | str | None = None) -> None:
        self.errors.append(Issue(code, message, _display_path(self.repo_root, path)))
    def add_warning(self, code: str, message: str, path: Path | str | None = None) -> None:
        self.warnings.append(Issue(code, message, _display_path(self.repo_root, path)))
    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "runtime_enabled": self.runtime_enabled, "skills": self.skills,
                "errors": [x.to_dict() for x in self.errors], "warnings": [x.to_dict() for x in self.warnings]}

class SecurityValidationError(RuntimeError):
    def __init__(self, report: ValidationReport):
        super().__init__("Skill security validation failed"); self.report = report

def _display_path(repo_root: Path, path: Path | str | None) -> str | None:
    if path is None: return None
    candidate = Path(path)
    try: return candidate.resolve(strict=False).relative_to(repo_root.resolve(strict=False)).as_posix()
    except (ValueError, OSError): return str(path)

def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle: return json.load(handle)

def _write_json_stdout(value: Any) -> None:
    json.dump(value, sys.stdout, indent=2, sort_keys=True); sys.stdout.write("\n")

def compute_skill_hash(skill_dir: Path) -> str:
    skill_dir = skill_dir.resolve(strict=True); digest = hashlib.sha256(); files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if path.is_symlink(): raise ValueError(f"Symlink cannot be hashed safely: {path}")
        if path.is_file() and path.name != MANIFEST_NAME: files.append(path)
    for path in sorted(files, key=lambda item: item.relative_to(skill_dir).as_posix()):
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8"); content = path.read_bytes()
        if path.suffix.lower() in TEXT_SCAN_SUFFIXES:
            content = content.replace(bytes([13, 10]), bytes([10])).replace(bytes([13]), bytes([10]))
        digest.update(len(relative).to_bytes(8, "big")); digest.update(relative)
        digest.update(len(content).to_bytes(8, "big")); digest.update(content)
    return digest.hexdigest()

def _validate_exact_keys(value: Any, required: set[str], report: ValidationReport, code_prefix: str, path: Path) -> dict[str, Any] | None:
    if not isinstance(value, dict): report.add_error(f"{code_prefix}_TYPE", "Expected a JSON object.", path); return None
    missing = sorted(required - set(value)); unknown = sorted(set(value) - required)
    if missing: report.add_error(f"{code_prefix}_MISSING", f"Missing fields: {', '.join(missing)}.", path)
    if unknown: report.add_error(f"{code_prefix}_UNKNOWN", f"Unknown fields: {', '.join(unknown)}.", path)
    return value

def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str): return False
    try: date.fromisoformat(value); return True
    except ValueError: return False

def _validate_policy(policy: Any, report: ValidationReport, path: Path) -> dict[str, Any] | None:
    initial_error_count = len(report.errors)
    obj = _validate_exact_keys(policy, {"schema_version", "authority", "discovery", "git", "admission", "prohibited_capabilities"}, report, "POLICY", path)
    if obj is None: return None
    if obj.get("schema_version") != 1: report.add_error("POLICY_SCHEMA_VERSION", "Policy schema_version must be 1.", path)
    discovery = _validate_exact_keys(obj.get("discovery"), {"root", "pattern", "max_depth", "excluded_roots", "reject_symlinks", "reject_nested_skills"}, report, "POLICY_DISCOVERY", path)
    if discovery is not None:
        expected = {"root":"skills","pattern":"skills/*/SKILL.md","max_depth":1,"reject_symlinks":True,"reject_nested_skills":True}
        for key, expected_value in expected.items():
            if discovery.get(key) != expected_value: report.add_error("DISCOVERY_POLICY_UNSAFE", f"discovery.{key} must equal {expected_value!r}.", path)
        excluded = discovery.get("excluded_roots")
        if not isinstance(excluded, list) or not {"references", ".work"}.issubset(set(excluded)):
            report.add_error("DISCOVERY_EXCLUSIONS_UNSAFE", "references and .work must be permanently excluded.", path)
    git_policy = _validate_exact_keys(obj.get("git"), {"required", "expected_origin", "allowed_origin_schemes"}, report, "POLICY_GIT", path)
    if git_policy is not None:
        if git_policy.get("required") is not True: report.add_error("GIT_POLICY_UNSAFE", "Git metadata must be required.", path)
        if not isinstance(git_policy.get("expected_origin"), str) or not git_policy.get("expected_origin"): report.add_error("GIT_EXPECTED_ORIGIN_MISSING", "A non-empty expected origin is required.", path)
        schemes = git_policy.get("allowed_origin_schemes")
        if not isinstance(schemes, list) or not schemes or any(item not in {"https", "ssh"} for item in schemes): report.add_error("GIT_SCHEMES_INVALID", "Only explicit https and/or ssh origin schemes are allowed.", path)
    admission = _validate_exact_keys(obj.get("admission"), {"allowed_tiers","reject_allowed_tools","require_content_hash","require_license_review","require_human_approval","require_rollback"}, report, "POLICY_ADMISSION", path)
    if admission is not None:
        if admission.get("allowed_tiers") != [0,1,2]: report.add_error("ALLOWED_TIERS_UNSAFE", "P0 allowed tiers must be exactly [0, 1, 2].", path)
        for key in ("reject_allowed_tools","require_content_hash","require_license_review","require_human_approval","require_rollback"):
            if admission.get(key) is not True: report.add_error("ADMISSION_POLICY_UNSAFE", f"admission.{key} must be true.", path)
    prohibited = obj.get("prohibited_capabilities")
    if not isinstance(prohibited, list) or set(prohibited) != set(CAPABILITY_NAMES): report.add_error("PROHIBITED_CAPABILITIES_UNSAFE", "P0 prohibited_capabilities must contain every high-risk capability exactly once.", path)
    return obj if len(report.errors) == initial_error_count else None

def _validate_runtime_control(value: Any, report: ValidationReport, path: Path) -> dict[str, Any] | None:
    obj = _validate_exact_keys(value, {"schema_version","skills_enabled","reason","changed_at","changed_by"}, report, "RUNTIME_CONTROL", path)
    if obj is None: return None
    if obj.get("schema_version") != 1: report.add_error("RUNTIME_SCHEMA_VERSION", "runtime-control schema_version must be 1.", path)
    if not isinstance(obj.get("skills_enabled"), bool): report.add_error("RUNTIME_ENABLED_TYPE", "skills_enabled must be boolean.", path)
    if not isinstance(obj.get("reason"), str) or not obj.get("reason", "").strip(): report.add_error("RUNTIME_REASON_MISSING", "A non-empty runtime reason is required.", path)
    if not isinstance(obj.get("changed_by"), str) or not obj.get("changed_by", "").strip(): report.add_error("RUNTIME_ACTOR_MISSING", "A non-empty changed_by value is required.", path)
    if not isinstance(obj.get("changed_at"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", obj.get("changed_at", "")): report.add_error("RUNTIME_TIMESTAMP_INVALID", "changed_at must use UTC YYYY-MM-DDTHH:MM:SSZ.", path)
    report.runtime_enabled = obj.get("skills_enabled") is True; return obj

def _unquote_scalar(value: str) -> str:
    value=value.strip()
    if len(value)>=2 and value[0]==value[-1]=='"':
        try:
            parsed=json.loads(value); return parsed if isinstance(parsed,str) else value
        except json.JSONDecodeError: return value
    if len(value)>=2 and value[0]==value[-1]=="'": return value[1:-1].replace("''", "'")
    return value

def parse_skill_frontmatter(skill_path: Path) -> tuple[dict[str, Any], str]:
    text=skill_path.read_text(encoding="utf-8"); lines=text.splitlines()
    if not lines or lines[0].strip()!="---": raise ValueError("SKILL.md must start with a YAML frontmatter delimiter.")
    try: closing=next(index for index in range(1,len(lines)) if lines[index].strip()=="---")
    except StopIteration as exc: raise ValueError("SKILL.md frontmatter has no closing delimiter.") from exc
    frontmatter_lines=lines[1:closing]; result:dict[str,Any]={}; index=0
    while index<len(frontmatter_lines):
        line=frontmatter_lines[index]
        if not line.strip() or line.lstrip().startswith("#"): index+=1; continue
        if line[:1].isspace(): raise ValueError(f"Unexpected indentation in frontmatter line {index+2}.")
        match=re.fullmatch(r"([A-Za-z0-9-]+):(?:\s*(.*))?",line)
        if not match: raise ValueError(f"Malformed frontmatter line {index+2}.")
        key,raw=match.group(1),match.group(2) or ""
        if key in result: raise ValueError(f"Duplicate frontmatter field: {key}.")
        if raw.lstrip().startswith(("&","*","!!")): raise ValueError(f"YAML anchors, aliases, and explicit tags are not allowed: {key}.")
        if raw in {"|",">"}:
            block=[]; index+=1
            while index<len(frontmatter_lines) and (frontmatter_lines[index].startswith(" ") or not frontmatter_lines[index].strip()):
                current=frontmatter_lines[index]; block.append(current[2:] if current.startswith("  ") else current.lstrip()); index+=1
            result[key] = ("\n" if raw=="|" else " ").join(block).strip(); continue
        if key=="metadata" and raw=="":
            metadata={}; index+=1
            while index<len(frontmatter_lines) and frontmatter_lines[index].startswith("  "):
                nested=frontmatter_lines[index][2:]; m=re.fullmatch(r"([A-Za-z0-9_.-]+):\s*(.*)",nested)
                if not m: raise ValueError(f"Malformed metadata line {index+2}.")
                if m.group(1) in metadata: raise ValueError(f"Duplicate metadata field: {m.group(1)}.")
                metadata[m.group(1)]=_unquote_scalar(m.group(2)); index+=1
            result[key]=metadata; continue
        result[key]=_unquote_scalar(raw); index+=1
    return result, "\n".join(lines[closing+1:]).strip()

def _validate_frontmatter(skill_dir: Path, report: ValidationReport) -> dict[str, Any] | None:
    skill_path=skill_dir/SKILL_FILE_NAME
    try: frontmatter,body=parse_skill_frontmatter(skill_path)
    except (OSError,UnicodeError,ValueError) as exc: report.add_error("SKILL_FRONTMATTER_INVALID",str(exc),skill_path); return None
    allowed_fields={"name","description","license","compatibility","metadata","allowed-tools"}; unknown=sorted(set(frontmatter)-allowed_fields)
    if unknown: report.add_error("SKILL_FIELD_UNKNOWN",f"Unknown frontmatter fields: {', '.join(unknown)}.",skill_path)
    if "allowed-tools" in frontmatter: report.add_error("ALLOWED_TOOLS_REJECTED","allowed-tools is experimental and cannot define the repository security boundary.",skill_path)
    name=frontmatter.get("name")
    if not isinstance(name,str) or not NAME_PATTERN.fullmatch(name) or len(name)>64: report.add_error("SKILL_NAME_INVALID","name must be 1-64 lowercase letters, numbers, or single hyphen separators.",skill_path)
    elif name!=skill_dir.name: report.add_error("SKILL_NAME_MISMATCH","name must match the parent directory.",skill_path)
    description=frontmatter.get("description")
    if not isinstance(description,str) or not 1<=len(description.strip())<=1024: report.add_error("SKILL_DESCRIPTION_INVALID","description must contain 1-1024 characters.",skill_path)
    license_value=frontmatter.get("license")
    if license_value is not None and (not isinstance(license_value,str) or not license_value.strip()): report.add_error("SKILL_LICENSE_INVALID","license must be a non-empty string when present.",skill_path)
    compatibility=frontmatter.get("compatibility")
    if compatibility is not None and (not isinstance(compatibility,str) or not 1<=len(compatibility.strip())<=500): report.add_error("SKILL_COMPATIBILITY_INVALID","compatibility must contain 1-500 characters.",skill_path)
    metadata=frontmatter.get("metadata")
    if metadata is not None and (not isinstance(metadata,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in metadata.items())): report.add_error("SKILL_METADATA_INVALID","metadata must map strings to strings.",skill_path)
    if not body: report.add_error("SKILL_BODY_EMPTY","SKILL.md must contain instructions after frontmatter.",skill_path)
    return frontmatter

def _safe_repository_path(value: Any) -> bool:
    if not isinstance(value,str) or not value or "\\" in value or "\x00" in value: return False
    if re.match(r"^[A-Za-z]:",value) or value.startswith(("/","//")): return False
    return ".." not in PurePosixPath(value).parts

def _validate_manifest(skill_dir: Path, policy: dict[str, Any], report: ValidationReport) -> dict[str, Any] | None:
    manifest_path=skill_dir/MANIFEST_NAME
    if not manifest_path.is_file(): report.add_error("MANIFEST_MISSING",f"{MANIFEST_NAME} is required.",manifest_path); return None
    try: value=load_json(manifest_path)
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: report.add_error("MANIFEST_INVALID_JSON",str(exc),manifest_path); return None
    manifest=_validate_exact_keys(value,{"schema_version","skill","source","license","risk","filesystem","activation","dependencies","approval","rollback"},report,"MANIFEST",manifest_path)
    if manifest is None: return None
    if manifest.get("schema_version")!=2: report.add_error("MANIFEST_SCHEMA_VERSION","schema_version must be 2.",manifest_path)
    if manifest.get("skill")!=skill_dir.name: report.add_error("MANIFEST_SKILL_MISMATCH","manifest skill must match the directory name.",manifest_path)
    source=_validate_exact_keys(manifest.get("source"),{"repository","revision","imported_at","provenance_type","handoff","adopted_content_sha256"},report,"MANIFEST_SOURCE",manifest_path)
    if source is not None:
        repository=source.get("repository"); parsed=urlparse(repository) if isinstance(repository,str) else None
        if parsed is None or parsed.scheme!="https" or not parsed.netloc: report.add_error("SOURCE_REPOSITORY_INVALID","source.repository must be an absolute HTTPS URI.",manifest_path)
        if not isinstance(source.get("revision"),str) or not HEX_REVISION_PATTERN.fullmatch(source.get("revision", "")): report.add_error("SOURCE_REVISION_INVALID","source.revision must be an exact 40- or 64-character lowercase hex revision.",manifest_path)
        if not _is_iso_date(source.get("imported_at")): report.add_error("SOURCE_IMPORT_DATE_INVALID","source.imported_at must be an ISO date.",manifest_path)
        provenance_type=source.get("provenance_type")
        handoff=source.get("handoff")
        if provenance_type not in {"import-isolate","trusted-local"}: report.add_error("PROVENANCE_TYPE_INVALID","source.provenance_type must be import-isolate or trusted-local.",manifest_path)
        elif provenance_type=="import-isolate":
            if handoff is None:
                report.add_error("HANDOFF_REQUIRED","import-isolate provenance requires a finalized handoff record.",manifest_path)
            else:
                handoff_record=_validate_exact_keys(handoff,{"case_id","artifact","artifact_sha256"},report,"HANDOFF",manifest_path)
                if handoff_record is not None:
                    case_id=handoff_record.get("case_id"); artifact=handoff_record.get("artifact"); artifact_hash=handoff_record.get("artifact_sha256")
                    if not isinstance(case_id,str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,160}",case_id): report.add_error("HANDOFF_CASE_ID_INVALID","handoff.case_id must be a non-empty import-isolate case identifier.",manifest_path)
                    if not isinstance(artifact,str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,200}",artifact): report.add_error("HANDOFF_ARTIFACT_INVALID","handoff.artifact must be one safe artifact name.",manifest_path)
                    if not isinstance(artifact_hash,str) or not SHA256_PATTERN.fullmatch(artifact_hash): report.add_error("HANDOFF_DIGEST_INVALID","handoff.artifact_sha256 must be lowercase SHA-256 hex.",manifest_path)
        elif handoff is not None:
            report.add_error("HANDOFF_UNEXPECTED","trusted-local provenance must not claim an import-isolate handoff.",manifest_path)
        recorded_hash=source.get("adopted_content_sha256")
        if not isinstance(recorded_hash,str) or not SHA256_PATTERN.fullmatch(recorded_hash): report.add_error("CONTENT_HASH_INVALID","source.adopted_content_sha256 must be lowercase SHA-256 hex.",manifest_path)
        else:
            try: actual_hash=compute_skill_hash(skill_dir)
            except (OSError,ValueError) as exc: report.add_error("CONTENT_HASH_FAILED",str(exc),skill_dir)
            else:
                if recorded_hash!=actual_hash: report.add_error("CONTENT_HASH_MISMATCH","Recorded adopted-content hash does not match current skill content.",manifest_path)
    license_record=_validate_exact_keys(manifest.get("license"),{"identifier","reviewed"},report,"MANIFEST_LICENSE",manifest_path)
    if license_record is not None:
        if not isinstance(license_record.get("identifier"),str) or not license_record.get("identifier","").strip(): report.add_error("LICENSE_IDENTIFIER_INVALID","license.identifier must be non-empty.",manifest_path)
        if license_record.get("reviewed") is not True: report.add_error("LICENSE_NOT_REVIEWED","The source license must be reviewed.",manifest_path)
    risk=_validate_exact_keys(manifest.get("risk"),{"tier","capabilities"},report,"MANIFEST_RISK",manifest_path); tier=None
    if risk is not None:
        tier_value=risk.get("tier")
        if not isinstance(tier_value,int) or isinstance(tier_value,bool) or not 0<=tier_value<=4: report.add_error("TIER_INVALID","risk.tier must be an integer from 0 through 4.",manifest_path)
        else:
            tier=tier_value
            if tier not in policy["admission"]["allowed_tiers"]: report.add_error("TIER_NOT_ALLOWED",f"Tier {tier} is not allowed under P0 policy.",manifest_path)
        capabilities=_validate_exact_keys(risk.get("capabilities"),set(CAPABILITY_NAMES),report,"MANIFEST_CAPABILITIES",manifest_path)
        if capabilities is not None:
            for name in CAPABILITY_NAMES:
                val=capabilities.get(name)
                if not isinstance(val,bool): report.add_error("CAPABILITY_TYPE",f"Capability {name} must be boolean.",manifest_path)
                if name in policy["prohibited_capabilities"] and val is True: report.add_error("PROHIBITED_CAPABILITY",f"Capability {name} is prohibited at P0.",manifest_path)
    filesystem=_validate_exact_keys(manifest.get("filesystem"),{"read","write","absolute_paths"},report,"MANIFEST_FILESYSTEM",manifest_path)
    if filesystem is not None:
        read_paths=filesystem.get("read"); write_paths=filesystem.get("write")
        for label,paths in (("read",read_paths),("write",write_paths)):
            if not isinstance(paths,list) or any(not _safe_repository_path(item) for item in paths): report.add_error("FILESYSTEM_SCOPE_INVALID",f"filesystem.{label} must contain safe repository-relative paths.",manifest_path)
        if filesystem.get("absolute_paths") is not False: report.add_error("ABSOLUTE_PATHS_REJECTED","filesystem.absolute_paths must be false.",manifest_path)
        if tier in {0,1} and write_paths!=[]: report.add_error("WRITE_SCOPE_INVALID",f"Tier {tier} must not request write access.",manifest_path)
        if tier==2 and isinstance(write_paths,list):
            direct_git_scope=any(item==".git" or item.startswith(".git/") for item in write_paths)
            if not write_paths or direct_git_scope: report.add_error("WRITE_SCOPE_INVALID","Tier 2 requires at least one repository-relative write scope and must not target .git metadata directly.",manifest_path)
    activation=_validate_exact_keys(manifest.get("activation"),{"mode","requires_trusted_project","requires_human_approval"},report,"MANIFEST_ACTIVATION",manifest_path)
    if activation is not None:
        if activation.get("mode") not in {"model","explicit"}: report.add_error("ACTIVATION_MODE_INVALID","activation.mode must be model or explicit.",manifest_path)
        if activation.get("requires_trusted_project") is not True: report.add_error("TRUSTED_PROJECT_REQUIRED","Adopted skills must require a trusted project.",manifest_path)
        if not isinstance(activation.get("requires_human_approval"),bool): report.add_error("APPROVAL_FLAG_TYPE","requires_human_approval must be boolean.",manifest_path)
        if tier==2 and (activation.get("mode")!="explicit" or activation.get("requires_human_approval") is not True): report.add_error("ACTIVATION_MODE_INVALID","Tier 2 requires explicit activation and human approval.",manifest_path)
    dependencies=_validate_exact_keys(manifest.get("dependencies"),{"locked","runtime_installation"},report,"MANIFEST_DEPENDENCIES",manifest_path)
    if dependencies is not None:
        if dependencies.get("locked") is not True: report.add_error("DEPENDENCIES_UNLOCKED","All dependencies must be locked.",manifest_path)
        if dependencies.get("runtime_installation") is not False: report.add_error("RUNTIME_INSTALLATION_REJECTED","Runtime dependency installation is prohibited.",manifest_path)
    approval=_validate_exact_keys(manifest.get("approval"),{"status","reviewer","reviewed_at"},report,"MANIFEST_APPROVAL",manifest_path)
    if approval is not None:
        if approval.get("status")!="approved": report.add_error("APPROVAL_STATUS_INVALID","approval.status must be approved.",manifest_path)
        if not isinstance(approval.get("reviewer"),str) or not approval.get("reviewer","").strip(): report.add_error("APPROVAL_REVIEWER_MISSING","approval.reviewer must be non-empty.",manifest_path)
        if not _is_iso_date(approval.get("reviewed_at")): report.add_error("APPROVAL_DATE_INVALID","approval.reviewed_at must be an ISO date.",manifest_path)
    rollback=_validate_exact_keys(manifest.get("rollback"),{"verified","method"},report,"MANIFEST_ROLLBACK",manifest_path)
    if rollback is not None:
        if rollback.get("verified") is not True: report.add_error("ROLLBACK_NOT_VERIFIED","Rollback must be verified.",manifest_path)
        if not isinstance(rollback.get("method"),str) or len(rollback.get("method","").strip())<10: report.add_error("ROLLBACK_METHOD_INVALID","Rollback method must contain at least 10 characters.",manifest_path)
    if tier==0 and (skill_dir/"scripts").exists(): report.add_error("TIER_ZERO_SCRIPTS","Tier 0 skills cannot contain scripts.",skill_dir/"scripts")
    return manifest

def _walk_without_following_links(skill_dir: Path) -> Iterable[Path]:
    for current_root,directories,files in os.walk(skill_dir,followlinks=False):
        current=Path(current_root)
        for name in directories: yield current/name
        for name in files: yield current/name

def _validate_skill_tree(skill_dir: Path, report: ValidationReport) -> None:
    for path in _walk_without_following_links(skill_dir):
        relative_parts=path.relative_to(skill_dir).parts
        if path.is_symlink(): report.add_error("SYMLINK_REJECTED","Symlinks are prohibited in adopted skills.",path); continue
        if path.name in HAZARDOUS_ARTIFACT_NAMES or any(part in HAZARDOUS_DIRECTORY_NAMES for part in relative_parts): report.add_error("HAZARDOUS_ARTIFACT","Lifecycle-hook, plugin, and remote-MCP artifacts are prohibited at P0.",path)
        if not path.is_file() or path.name==MANIFEST_NAME or path.suffix.lower() not in TEXT_SCAN_SUFFIXES: continue
        try:
            if path.stat().st_size>1_000_000: report.add_error("TEXT_FILE_TOO_LARGE","Text files above 1 MB require separate review.",path); continue
            content=path.read_text(encoding="utf-8")
        except (OSError,UnicodeError) as exc: report.add_error("TEXT_SCAN_FAILED",str(exc),path); continue
        normalized_content=re.sub(r"[^A-Za-z0-9_.:/+-]+"," ",content); normalized_content=re.sub(r"\s+"," ",normalized_content)
        for pattern in RUNTIME_INSTALLATION_PATTERNS:
            if pattern.search(content) or pattern.search(normalized_content): report.add_error("RUNTIME_INSTALLATION_PATTERN",f"Runtime dependency resolution pattern is prohibited: {pattern.pattern}.",path); break
        for pattern in PROHIBITED_OPERATION_PATTERNS:
            if pattern.search(content): report.add_error("PROHIBITED_OPERATION_PATTERN",f"Prohibited external or destructive operation pattern: {pattern.pattern}.",path); break
        for pattern in NETWORK_EXECUTION_PATTERNS:
            if pattern.search(content): report.add_error("NETWORK_OPERATION_PATTERN",f"Network execution pattern is prohibited at P0: {pattern.pattern}.",path); break

def _remote_identity(remote: str) -> tuple[str,str] | None:
    remote=remote.strip()
    if re.fullmatch(r"git@[^:]+:.+",remote):
        host,path=remote[4:].split(":",1); return "ssh",f"{host}/{path.removesuffix('.git')}".lower()
    parsed=urlparse(remote)
    if parsed.scheme in {"http","https","ssh"} and parsed.hostname:
        scheme="https" if parsed.scheme in {"http","https"} else "ssh"; return scheme,f"{parsed.hostname}/{parsed.path.lstrip('/').removesuffix('.git')}".lower()
    return None

def _run_git(repo_root: Path,args:list[str])->subprocess.CompletedProcess[str]:
    return subprocess.run(["git","-C",str(repo_root),*args],check=False,capture_output=True,text=True,timeout=15)

def _validate_git(repo_root: Path,policy:dict[str,Any],report:ValidationReport)->None:
    try: inside=_run_git(repo_root,["rev-parse","--is-inside-work-tree"])
    except (OSError,subprocess.TimeoutExpired) as exc: report.add_error("GIT_UNAVAILABLE",str(exc),repo_root); return
    if inside.returncode!=0 or inside.stdout.strip()!="true": report.add_error("GIT_METADATA_MISSING","Repository Git metadata is required.",repo_root); return
    origin=_run_git(repo_root,["remote","get-url","origin"])
    if origin.returncode!=0 or not origin.stdout.strip(): report.add_error("GIT_ORIGIN_MISSING","A configured origin remote is required.",repo_root); return
    actual=_remote_identity(origin.stdout.strip()); expected=_remote_identity(policy["git"]["expected_origin"])
    if actual is None: report.add_error("GIT_ORIGIN_INVALID","origin must use an allowed HTTPS or SSH Git URL.",repo_root); return
    if actual[0] not in policy["git"]["allowed_origin_schemes"]: report.add_error("GIT_ORIGIN_SCHEME",f"origin scheme {actual[0]} is not allowed.",repo_root)
    if expected is None or actual[1]!=expected[1]: report.add_error("GIT_ORIGIN_MISMATCH",f"origin {origin.stdout.strip()!r} does not match configured repository identity.",repo_root)

def _load_required_json(repo_root:Path,relative:Path,report:ValidationReport,code:str)->Any|None:
    path=repo_root/relative
    try: return load_json(path)
    except FileNotFoundError: report.add_error(f"{code}_MISSING",f"Required file is missing: {relative.as_posix()}.",path)
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: report.add_error(f"{code}_INVALID",str(exc),path)
    return None

def validate_repository(repo_root:Path,*,require_git:bool=True)->ValidationReport:
    repo_root=repo_root.resolve(strict=True); report=ValidationReport(repo_root=repo_root)
    policy_value=_load_required_json(repo_root,POLICY_PATH,report,"POLICY"); runtime_value=_load_required_json(repo_root,RUNTIME_CONTROL_PATH,report,"RUNTIME_CONTROL")
    policy=_validate_policy(policy_value,report,repo_root/POLICY_PATH) if policy_value is not None else None
    if runtime_value is not None: _validate_runtime_control(runtime_value,report,repo_root/RUNTIME_CONTROL_PATH)
    if policy is None: return report
    skills_root=repo_root/policy["discovery"]["root"]
    if not skills_root.is_dir(): report.add_error("SKILLS_ROOT_MISSING","The skills discovery root must exist.",skills_root); return report
    if skills_root.is_symlink(): report.add_error("SYMLINK_REJECTED","The skills discovery root cannot be a symlink.",skills_root); return report
    for skill_file in sorted(skills_root.rglob(SKILL_FILE_NAME)):
        if len(skill_file.relative_to(skills_root).parts)!=2: report.add_error("NESTED_SKILL","Only direct children matching skills/*/SKILL.md are permitted.",skill_file)
    seen_names:set[str]=set()
    direct_dirs=sorted((p for p in skills_root.iterdir() if p.is_dir() or p.is_symlink()),key=lambda p:p.name)
    for skill_dir in direct_dirs:
        if skill_dir.is_symlink(): report.add_error("SYMLINK_REJECTED","Skill directories cannot be symlinks.",skill_dir); continue
        skill_path=skill_dir/SKILL_FILE_NAME
        if not skill_path.is_file(): report.add_error("ORPHAN_SKILL_DIRECTORY","Every direct directory below skills must contain SKILL.md.",skill_dir); continue
        _validate_skill_tree(skill_dir,report); frontmatter=_validate_frontmatter(skill_dir,report); manifest=_validate_manifest(skill_dir,policy,report)
        name=frontmatter.get("name") if frontmatter is not None else None
        if isinstance(name,str):
            if name in seen_names: report.add_error("DUPLICATE_SKILL_NAME",f"Duplicate skill name: {name}.",skill_path)
            seen_names.add(name)
        if frontmatter is not None and manifest is not None:
            risk=manifest.get("risk") if isinstance(manifest.get("risk"),dict) else {}; activation=manifest.get("activation") if isinstance(manifest.get("activation"),dict) else {}; source=manifest.get("source") if isinstance(manifest.get("source"),dict) else {}
            report.skills.append({"name":name,"description":frontmatter.get("description"),"location":skill_path.relative_to(repo_root).as_posix(),"risk_tier":risk.get("tier"),"activation_mode":activation.get("mode"),"adopted_content_sha256":source.get("adopted_content_sha256")})
    if require_git and policy["git"]["required"] is True: _validate_git(repo_root,policy,report)
    return report

def build_catalog(repo_root:Path,*,require_git:bool=True)->dict[str,Any]:
    repo_root=repo_root.resolve(strict=True); runtime_path=repo_root/RUNTIME_CONTROL_PATH
    try: runtime=load_json(runtime_path)
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        report=ValidationReport(repo_root=repo_root); report.add_error("RUNTIME_CONTROL_INVALID",str(exc),runtime_path); raise SecurityValidationError(report) from exc
    if isinstance(runtime,dict) and runtime.get("skills_enabled") is False: return {"enabled":False,"reason":runtime.get("reason","Emergency runtime switch is disabled."),"skills":[]}
    report=validate_repository(repo_root,require_git=require_git)
    if not report.ok: raise SecurityValidationError(report)
    return {"enabled":True,"reason":runtime.get("reason","enabled"),"skills":report.skills}

def _build_parser()->argparse.ArgumentParser:
    parser=argparse.ArgumentParser(description="Validate and catalog repository-owned Agent Skills."); subparsers=parser.add_subparsers(dest="command",required=True)
    validate=subparsers.add_parser("validate",help="Validate policy, skills, provenance, and Git identity."); validate.add_argument("--repo",default=".",help="Repository root (default: current directory)."); validate.add_argument("--skip-git",action="store_true",help="Skip Git checks for pre-initialization validation only.")
    catalog=subparsers.add_parser("catalog",help="Emit the fail-closed runtime catalog as JSON."); catalog.add_argument("--repo",default=".",help="Repository root (default: current directory)."); catalog.add_argument("--skip-git",action="store_true",help="Skip Git checks for controlled tests only.")
    hash_command=subparsers.add_parser("hash",help="Compute a deterministic adopted-skill content hash."); hash_command.add_argument("skill_dir",help="Path to the adopted skill directory.")
    return parser

def main(argv:list[str]|None=None)->int:
    args=_build_parser().parse_args(argv)
    if args.command=="hash":
        try: result=compute_skill_hash(Path(args.skill_dir))
        except (OSError,ValueError) as exc: _write_json_stdout({"ok":False,"error":str(exc)}); return 2
        _write_json_stdout({"ok":True,"adopted_content_sha256":result}); return 0
    repo_root=Path(args.repo)
    if args.command=="validate":
        try: report=validate_repository(repo_root,require_git=not args.skip_git)
        except (OSError,ValueError) as exc: _write_json_stdout({"ok":False,"errors":[{"code":"REPOSITORY_INVALID","message":str(exc)}]}); return 2
        _write_json_stdout(report.to_dict()); return 0 if report.ok else 1
    if args.command=="catalog":
        try: catalog=build_catalog(repo_root,require_git=not args.skip_git)
        except SecurityValidationError as exc: _write_json_stdout(exc.report.to_dict()); return 1
        except (OSError,ValueError) as exc: _write_json_stdout({"ok":False,"errors":[{"code":"REPOSITORY_INVALID","message":str(exc)}]}); return 2
        _write_json_stdout(catalog); return 0
    return 2

if __name__=="__main__": raise SystemExit(main())
