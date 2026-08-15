from __future__ import annotations

import ast
import hashlib
import os
import re
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from .fs import opened_path
from .models import CatalogInventory, CatalogSkill

_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")


class FrontmatterError(ValueError):
    pass


class EntryChangedError(RuntimeError):
    pass


def _scalar(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value[0:1] in {"'", '"'}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise FrontmatterError("invalid quoted scalar") from exc
        if not isinstance(parsed, str):
            raise FrontmatterError("frontmatter scalar must be text")
        return parsed
    return value


def _block_value(lines: list[str], start: int, style: str) -> tuple[str, int]:
    values: list[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if line and not line[0].isspace():
            break
        values.append(line.strip())
        index += 1
    if not values:
        raise FrontmatterError("frontmatter block scalar has no content")
    if style == ">":
        rendered = " ".join(item for item in values if item).strip()
    else:
        rendered = "\n".join(values).strip()
    return rendered, index


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("SKILL.md frontmatter must start with ---")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise FrontmatterError("SKILL.md frontmatter closing --- is missing") from exc
    body = lines[1:end]
    result: dict[str, str] = {}
    index = 0
    while index < len(body):
        line = body[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line[0].isspace():
            raise FrontmatterError("unexpected indented frontmatter line")
        match = _KEY_RE.fullmatch(line)
        if match is None:
            raise FrontmatterError(f"invalid frontmatter line: {line.strip()}")
        key, raw = match.groups()
        raw = raw or ""
        if raw.strip() in {">", "|"}:
            value, index = _block_value(body, index + 1, raw.strip())
        else:
            value = _scalar(raw)
            index += 1
            if not raw.strip():
                while index < len(body) and (
                    not body[index].strip() or body[index][0].isspace()
                ):
                    index += 1
        result[key] = value
    return result


def _directory_identity(stat_result: os.stat_result) -> tuple[int, int]:
    return stat_result.st_dev, stat_result.st_ino


def _file_identity(stat_result: os.stat_result) -> tuple[int, int, int, int]:
    return (
        stat_result.st_dev,
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
    )


def _read_skill(
    directory: Path,
    entrypoint: Path,
    *,
    source_path: Path,
    expected_directory_identity: tuple[int, int],
    expected_file_identity: tuple[int, int, int, int],
) -> CatalogSkill:
    warnings: list[str] = []
    content_hash: str | None = None
    modified_at: str | None = None
    try:
        with entrypoint.open("rb") as handle:
            try:
                actual_path = opened_path(handle)
            except OSError as exc:
                raise EntryChangedError(f"cannot verify opened SKILL.md path: {exc}") from exc
            if actual_path.parent != source_path or actual_path.name != entrypoint.name:
                raise EntryChangedError(
                    f"opened SKILL.md escaped validated catalogue directory: {actual_path}"
                )
            opened_stat = os.fstat(handle.fileno())
            current_directory_stat = directory.stat(follow_symlinks=False)
            if _directory_identity(current_directory_stat) != expected_directory_identity:
                raise EntryChangedError("catalogue directory changed during validation")
            if _file_identity(opened_stat) != expected_file_identity:
                raise EntryChangedError("SKILL.md changed during validation")
            raw = handle.read()
            final_stat = os.fstat(handle.fileno())
            if _file_identity(final_stat) != expected_file_identity:
                raise EntryChangedError("SKILL.md changed while being read")
        modified_at = datetime.fromtimestamp(opened_stat.st_mtime, UTC).isoformat()
        content_hash = hashlib.sha256(raw).hexdigest()
        text = raw.decode("utf-8")
        frontmatter = parse_frontmatter(text)
        name = frontmatter.get("name", "").strip()
        description = frontmatter.get("description", "").strip()
        if not name or _NAME_RE.fullmatch(name) is None or "--" in name:
            raise FrontmatterError("frontmatter name is not a canonical skill identifier")
        if name != directory.name:
            raise FrontmatterError(
                f"frontmatter name {name!r} does not match directory {directory.name!r}"
            )
        if not description:
            raise FrontmatterError("frontmatter description is required")
        if len(description) > 1024:
            raise FrontmatterError("frontmatter description exceeds 1024 characters")
        status = frontmatter.get("status", "active").strip() or "active"
        category = frontmatter.get("category", "").strip() or None
        return CatalogSkill(
            name=name,
            description=description,
            source_path=str(source_path),
            modified_at=modified_at,
            content_sha256=content_hash,
            status=status,
            category=category,
            parse_status="valid",
            warnings=(),
        )
    except EntryChangedError:
        raise
    except (OSError, UnicodeError, FrontmatterError) as exc:
        warnings.append(f"frontmatter invalid: {exc}")
        return CatalogSkill(
            name=directory.name,
            description=None,
            source_path=str(source_path),
            modified_at=modified_at,
            content_sha256=content_hash,
            status="invalid",
            category=None,
            parse_status="invalid",
            warnings=tuple(warnings),
        )


def discover_catalog(roots: Iterable[Path | str]) -> CatalogInventory:
    normalized_roots: list[str] = []
    root_statuses: list[tuple[str, str]] = []
    warnings: list[str] = []
    selected: dict[str, CatalogSkill] = {}
    for raw_root in roots:
        root = Path(raw_root).expanduser()
        try:
            resolved = root.resolve()
        except OSError:
            resolved = root.absolute()
        normalized_roots.append(str(resolved))
        if not resolved.is_dir():
            root_statuses.append((str(resolved), "not_available"))
            warnings.append(f"catalogue root unavailable: {resolved}")
            continue
        try:
            children = sorted(resolved.iterdir(), key=lambda item: item.name.casefold())
        except OSError as exc:
            root_statuses.append((str(resolved), "invalid"))
            warnings.append(f"catalogue root unreadable: {resolved}: {exc}")
            continue
        root_statuses.append((str(resolved), "observed"))
        for directory in children:
            if directory.name.startswith("."):
                continue
            if directory.is_symlink():
                warnings.append(f"linked catalogue entry rejected: {directory.absolute()}")
                continue
            try:
                directory_resolved = directory.resolve(strict=True)
            except OSError as exc:
                warnings.append(f"catalogue entry unreadable: {directory.absolute()}: {exc}")
                continue
            if directory_resolved.parent != resolved or not directory_resolved.is_dir():
                warnings.append(f"catalogue entry outside root rejected: {directory.absolute()}")
                continue
            entrypoint = directory / "SKILL.md"
            if entrypoint.is_symlink():
                warnings.append(f"linked SKILL.md rejected: {entrypoint.absolute()}")
                continue
            if not entrypoint.is_file():
                warnings.append(f"missing SKILL.md: {directory_resolved}")
                continue
            try:
                entrypoint_resolved = entrypoint.resolve(strict=True)
            except OSError as exc:
                warnings.append(f"SKILL.md unreadable: {entrypoint.absolute()}: {exc}")
                continue
            if entrypoint_resolved.parent != directory_resolved:
                warnings.append(f"SKILL.md outside catalogue entry rejected: {entrypoint.absolute()}")
                continue
            try:
                expected_directory_identity = _directory_identity(
                    directory.stat(follow_symlinks=False)
                )
                expected_file_identity = _file_identity(
                    entrypoint.stat(follow_symlinks=False)
                )
                entry = _read_skill(
                    directory,
                    entrypoint,
                    source_path=directory_resolved,
                    expected_directory_identity=expected_directory_identity,
                    expected_file_identity=expected_file_identity,
                )
            except EntryChangedError as exc:
                warnings.append(f"catalogue entry changed during validation: {directory_resolved}: {exc}")
                continue
            except OSError as exc:
                warnings.append(f"catalogue entry unreadable: {directory_resolved}: {exc}")
                continue
            prior = selected.get(entry.name)
            if prior is None:
                selected[entry.name] = entry
                continue
            duplicate_warning = f"duplicate skill shadowed from {entry.source_path}"
            selected[entry.name] = replace(
                prior, warnings=tuple((*prior.warnings, duplicate_warning))
            )
    entries = tuple(sorted(selected.values(), key=lambda item: item.name.casefold()))
    return CatalogInventory(
        entries=entries,
        roots=tuple(normalized_roots),
        root_statuses=tuple(root_statuses),
        warnings=tuple(warnings),
    )
