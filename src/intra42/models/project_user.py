"""The ``ProjectUser`` resource: a user's assignment to a project (status,
grading, team membership).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .base import FortyTwoModel


class ProjectUserProjectRef(FortyTwoModel):
    id: int | None = None
    name: str | None = None
    slug: str | None = None
    parent_id: int | None = None


class ProjectUserUserRef(FortyTwoModel):
    id: int | None = None
    login: str | None = None
    url: str | None = None


class TeamMember(FortyTwoModel):
    id: int | None = None
    login: str | None = None
    url: str | None = None
    leader: bool | None = None
    occurrence: int | None = None
    validated: bool | None = None
    projects_user_id: int | None = None


class Team(FortyTwoModel):
    id: int | None = None
    name: str | None = None
    url: str | None = None
    final_mark: int | None = None
    project_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    status: str | None = None
    terminating_at: datetime | None = None
    users: list[TeamMember] | None = None
    locked: bool | None = Field(default=None, alias="locked?")
    validated: bool | None = Field(default=None, alias="validated?")
    closed: bool | None = Field(default=None, alias="closed?")
    repo_url: str | None = None
    repo_uuid: str | None = None
    locked_at: datetime | None = None
    closed_at: datetime | None = None
    project_session_id: int | None = None


class ProjectUser(FortyTwoModel):
    id: int
    occurrence: int | None = None
    final_mark: int | None = None
    status: str | None = None
    validated: bool | None = Field(default=None, alias="validated?")
    current_team_id: int | None = None
    project: ProjectUserProjectRef | None = None
    cursus_ids: list[int] | None = None
    user: ProjectUserUserRef | None = None
    teams: list[Team] | None = None
    retriable_at: datetime | None = None
    marked_at: datetime | None = None
    retriable: bool | None = None
    marked: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
