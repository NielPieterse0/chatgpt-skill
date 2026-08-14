#!/usr/bin/env python3
"""Validate shared lifecycle skill entrypoints against the repository contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_contract(repo: Path) -> dict:
    path = repo / "config" / "skill-lifecycle-contract.json"
    return json.loads(path.read_text(encoding="utf-8"))


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not terminated")
    return text[4:end], text[end + 5 :]


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*)$", frontmatter)
    if not match:
        return None
    value = match.group(1).strip()
    if value not in {">", "|", ">-", "|-"}:
        return value.strip('"\'')
    lines = frontmatter[match.end() :].splitlines()
    folded: list[str] = []
    for line in lines:
        if not line and not folded:
            continue
        if not line.startswith((" ", "\t")):
            break
        folded.append(line.strip())
    return " ".join(folded).strip()


def validate_skill(root: Path, skill_id: str, rules: dict, common: dict) -> list[str]:
    errors: list[str] = []
    path = root / skill_id / "SKILL.md"
    if not path.is_file():
        return [f"{skill_id}: missing SKILL.md"]
    text = path.read_text(encoding="utf-8")
    try:
        frontmatter, _ = split_frontmatter(text)
    except ValueError as exc:
        return [f"{skill_id}: {exc}"]

    name = frontmatter_value(frontmatter, "name")
    description = frontmatter_value(frontmatter, "description")
    if name != skill_id or not name or not NAME_RE.fullmatch(name):
        errors.append(f"{skill_id}: invalid or mismatched name")
    if not description:
        errors.append(f"{skill_id}: missing description")
    elif len(description) > int(common["max_description_chars"]):
        errors.append(f"{skill_id}: description exceeds limit")
    if len(text.splitlines()) > int(common["max_skill_lines"]):
        errors.append(f"{skill_id}: SKILL.md exceeds line limit")

    frontmatter_keys = {
        line.split(":", 1)[0].strip()
        for line in frontmatter.splitlines()
        if line and not line[0].isspace() and ":" in line
    }
    for field in common.get("prohibited_frontmatter", []):
        if field in frontmatter_keys:
            errors.append(f"{skill_id}: prohibited frontmatter field {field}")

    folded_text = text.casefold()
    for term in common.get("required_authority_terms", []):
        if term.casefold() not in folded_text:
            errors.append(f"{skill_id}: missing authority term {term!r}")
    for term in rules.get("required_terms", []):
        if term.casefold() not in folded_text:
            errors.append(f"{skill_id}: missing lifecycle term {term!r}")
    for term in common.get("prohibited_mandatory_terms", []):
        if term.casefold() in folded_text:
            errors.append(f"{skill_id}: mandatory optional-tool command remains: {term}")
    return errors


def validate_catalog(repo: Path, catalog_root: Path) -> list[str]:
    contract = load_contract(repo)
    if contract.get("schema_version") != 1:
        return ["contract: unsupported schema_version"]
    common = contract["common"]
    errors: list[str] = []
    for skill_id, rules in contract["skills"].items():
        errors.extend(validate_skill(catalog_root, skill_id, rules, common))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate create/evaluate/improve shared skill lifecycle entrypoints."
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--catalog-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = args.repo.resolve()
    catalog_root = args.catalog_root.resolve()
    errors = validate_catalog(repo, catalog_root)
    result = {
        "schema_version": 1,
        "catalog_root": str(catalog_root),
        "valid": not errors,
        "errors": errors,
    }
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print("Shared skill lifecycle contract: PASS")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
