"""The ``Exam`` resource."""

from __future__ import annotations

from datetime import datetime

from .base import FortyTwoModel
from .campus import Campus
from .cursus import Cursus
from .project import Project


class Exam(FortyTwoModel):
    id: int
    name: str | None = None
    ip_range: str | None = None
    begin_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = None
    max_people: int | None = None
    nbr_subscribers: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    campus_id: int | None = None
    campus: Campus | None = None
    cursus: list[Cursus] | None = None
    projects: list[Project] | None = None
    visible: bool | None = None
    validated: bool | None = None
    validated_at: datetime | None = None
    validator_id: int | None = None
    prohibition_of_cancellation: int | None = None
