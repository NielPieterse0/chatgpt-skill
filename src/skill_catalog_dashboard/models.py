from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class CatalogSkill:
    name: str
    description: str | None
    source_path: str
    modified_at: str | None
    content_sha256: str | None
    status: str
    category: str | None
    parse_status: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CatalogInventory:
    entries: tuple[CatalogSkill, ...]
    roots: tuple[str, ...]
    root_statuses: tuple[tuple[str, str], ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RepoEvidence:
    skill_id: str
    adoption_status: str = "not_recorded"
    adopted_content_sha256: str | None = None
    adoption_path: str | None = None
    evaluation_status: str = "not_recorded"
    evaluation_disposition: str | None = None
    evaluation_path: str | None = None
    evaluation_runtime_sha256: str | None = None
    last_evaluated_at: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TelemetryEvidence:
    skill_id: str
    content_sha256: str
    discovered_count: int = 0
    loaded_count: int = 0
    resource_read_count: int = 0
    evaluated_count: int = 0
    mutation_count: int = 0
    applied_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    error_count: int = 0
    last_used_at: str | None = None
    last_used_status: str = "not_observable"
    projects: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TelemetrySnapshot:
    groups: tuple[TelemetryEvidence, ...]
    status: str
    source: str | None = None
    event_count: int | None = None
    warnings: tuple[str, ...] = ()

    @property
    def by_identity(self) -> Mapping[tuple[str, str], TelemetryEvidence]:
        return {(item.skill_id, item.content_sha256): item for item in self.groups}


@dataclass(frozen=True, slots=True)
class SkillReportRow:
    catalog: CatalogSkill
    repository: RepoEvidence
    telemetry: TelemetryEvidence | None
    telemetry_status: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DashboardReport:
    summary: Mapping[str, object]
    sources: Mapping[str, object]
    skills: tuple[SkillReportRow, ...]
    warnings: tuple[str, ...] = ()
    schema_version: int = 1
