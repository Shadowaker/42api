"""The ``Project`` resource."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .base import FortyTwoModel
from .campus import Campus
from .cursus import Cursus

if TYPE_CHECKING:
    from .._async.query import AsyncQuerySet
    from .._sync.query import QuerySet
    from .project_user import ProjectUser


class ProjectRef(FortyTwoModel):
    """A lightweight project reference, used for ``parent`` and ``children``."""

    id: int | None = None
    name: str | None = None
    slug: str | None = None
    url: str | None = None


class ProjectSkill(FortyTwoModel):
    id: int | None = None
    name: str | None = None
    created_at: datetime | None = None


class ProjectTag(FortyTwoModel):
    id: int | None = None
    name: str | None = None
    kind: str | None = None


class ProjectSessionScale(FortyTwoModel):
    id: int | None = None
    correction_number: int | None = None
    is_primary: bool | None = None


class ProjectSessionUpload(FortyTwoModel):
    id: int | None = None
    name: str | None = None


class ProjectSession(FortyTwoModel):
    id: int | None = None
    solo: bool | None = None
    begin_at: datetime | None = None
    end_at: datetime | None = None
    difficulty: int | None = None
    # Confirmed against a real account: not always an int (seconds) as the
    # apidoc example showed (2592000) — also seen as a free-form duration
    # string ("1 day").
    estimate_time: int | str | None = None
    duration_days: int | None = None
    terminating_after: int | None = None
    project_id: int | None = None
    campus_id: int | None = None
    cursus_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    max_people: int | None = None
    is_subscriptable: bool | None = None
    scales: list[ProjectSessionScale] | None = None
    uploads: list[ProjectSessionUpload] | None = None
    team_behaviour: str | None = None


class Project(FortyTwoModel):
    id: int
    name: str | None = None
    slug: str | None = None
    difficulty: int | None = None
    description: str | None = None
    parent_id: int | None = None
    parent: ProjectRef | None = None
    children: list[ProjectRef] | None = None
    objectives: list[str] | None = None
    attachments: list[Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    exam: bool | None = None
    cursus: list[Cursus] | None = None
    campus: list[Campus] | None = None
    skills: list[ProjectSkill] | None = None
    videos: list[Any] | None = None
    tags: list[ProjectTag] | None = None
    project_sessions: list[ProjectSession] | None = None
    visible: bool | None = None
    inherited_team: bool | None = None
    position: int | None = None
    has_git: bool | None = None
    has_mark: bool | None = None
    repository: str | None = None
    git_id: int | None = None
    cached_repository_path: str | None = None

    @property
    def projects_users(self) -> AsyncQuerySet[ProjectUser] | QuerySet[ProjectUser]:
        """Assignments of this project (``GET /projects/{id}/projects_users``)."""
        return self._relation("projects_users")
