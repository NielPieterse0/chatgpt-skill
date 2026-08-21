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
class IntakeRecord:
    candidate_id: str
    candidate_type: str
    requested_at: str
    source_repository: str
    source_issue_number: int
    work_management_state: str
    provenance_type: str
    provenance_state: str
    license_state: str
    adaptation_state: str
    evaluation_state: str
    human_review_state: str
    disposition: str
    next_action: str | None
    assessment_states: Mapping[str, str]
    targets: Mapping[str, str]
    source_path: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class IntakeSnapshot:
    records: tuple[IntakeRecord, ...]
    status: str
    source: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkItem:
    item_id: str
    number: int
    title: str
    url: str
    repository: str
    source_state: str
    work_state: str
    priority: str | None
    effort: str | None
    execution_owner: str | None
    blocked_by: str | None


@dataclass(frozen=True, slots=True)
class WorkSnapshot:
    items: tuple[WorkItem, ...]
    status: str
    source: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DashboardReport:
    summary: Mapping[str, object]
    sources: Mapping[str, object]
    skills: tuple[SkillReportRow, ...]
    intake: tuple[IntakeRecord, ...] = ()
    work: tuple[WorkItem, ...] = ()
    warnings: tuple[str, ...] = ()
    schema_version: int = 2
