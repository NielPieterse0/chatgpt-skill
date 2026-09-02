"""Maintain the tracked workspace-skills mirror and canonical workspace catalogue."""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

DEFAULT_CATALOGUE = Path(os.environ.get("CHATGPT_SKILL_CATALOGUE_ROOT", r"C:\Projects\.agents\skills"))


def files(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    result: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"symlink not allowed: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def digest(payload: dict[str, bytes]) -> str:
    h = hashlib.sha256()
    for name, data in sorted(payload.items()):
        raw = name.encode("utf-8")
        h.update(len(raw).to_bytes(8, "big")); h.update(raw)
        h.update(len(data).to_bytes(8, "big")); h.update(data)
    return h.hexdigest()

def repo_runtime_packages(repo: Path) -> dict[str, dict[str, bytes]]:
    packages: dict[str, dict[str, bytes]] = {}
    for skill in sorted((repo / "skills").iterdir()):
        if not skill.is_dir() or not (skill / "SKILL.md").is_file():
            continue
        payload = files(skill)
        payload.pop("adoption-manifest.json", None)
        packages[skill.name] = payload
    return packages


def replace_tree(destination: Path, payload: dict[str, bytes]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    wanted = set(payload)
    for candidate in sorted(destination.rglob("*"), reverse=True):
        relative = candidate.relative_to(destination).as_posix()
        if candidate.is_file() and relative not in wanted:
            candidate.unlink()
        elif candidate.is_dir() and not any(candidate.iterdir()):
            candidate.rmdir()
    for name, data in payload.items():
        target = destination / Path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)


def refresh(repo: Path) -> list[str]:
    mirror = repo / "workspace-skills"
    mirror.mkdir(exist_ok=True)
    changed: list[str] = []
    for name, payload in repo_runtime_packages(repo).items():
        target = mirror / name
        if files(target) != payload:
            replace_tree(target, payload)
            changed.append(name)
    return changed

def verify_repo_mirror(repo: Path) -> list[str]:
    errors: list[str] = []
    mirror = repo / "workspace-skills"
    if not mirror.is_dir():
        return ["tracked workspace-skills mirror is missing"]
    for skill in sorted(p for p in mirror.iterdir() if p.is_dir()):
        if not (skill / "SKILL.md").is_file():
            errors.append(f"mirror skill missing SKILL.md: {skill.name}")
        if (skill / "adoption-manifest.json").exists():
            errors.append(f"repository-only manifest leaked into mirror: {skill.name}")
    for name, payload in repo_runtime_packages(repo).items():
        actual = files(mirror / name)
        if actual != payload:
            errors.append(f"repo-owned mirror mismatch: {name}")
    return errors


def verify_catalogue(repo: Path, catalogue: Path) -> list[str]:
    errors = verify_repo_mirror(repo)
    mirror = repo / "workspace-skills"
    if not catalogue.exists():
        return errors
    mirror_names = {p.name for p in mirror.iterdir() if p.is_dir()}
    catalogue_names = {p.name for p in catalogue.iterdir() if p.is_dir()}
    for name in sorted(mirror_names | catalogue_names):
        if name not in mirror_names:
            errors.append(f"canonical-only skill: {name}")
        elif name not in catalogue_names:
            errors.append(f"canonical missing skill: {name}")
        elif files(mirror / name) != files(catalogue / name):
            errors.append(f"canonical mismatch: {name}")
    return errors


def publish(repo: Path, catalogue: Path) -> list[str]:
    errors = verify_repo_mirror(repo)
    if errors:
        raise RuntimeError("; ".join(errors))
    mirror = repo / "workspace-skills"
    catalogue.mkdir(parents=True, exist_ok=True)
    mirror_names = {p.name for p in mirror.iterdir() if p.is_dir()}
    catalogue_names = {p.name for p in catalogue.iterdir() if p.is_dir()}
    extras = sorted(catalogue_names - mirror_names)
    if extras:
        raise RuntimeError("canonical catalogue has untracked skills: " + ", ".join(extras))
    changed: list[str] = []
    for name in sorted(mirror_names):
        payload = files(mirror / name)
        target = catalogue / name
        if files(target) != payload:
            replace_tree(target, payload)
            changed.append(name)
    return changed

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["refresh", "verify", "publish"])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--catalogue-root", default=str(DEFAULT_CATALOGUE))
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    catalogue = Path(args.catalogue_root).resolve()
    try:
        if args.mode == "refresh":
            changed = refresh(repo)
            print("refreshed:", ", ".join(changed) if changed else "none")
        elif args.mode == "publish":
            changed = publish(repo, catalogue)
            print("published:", ", ".join(changed) if changed else "none")
        else:
            errors = verify_catalogue(repo, catalogue)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("workspace skill mirror: OK")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
