"""The ``Cursus`` resource (a curriculum/track, e.g. "42", "Piscine C")."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .base import FortyTwoModel

if TYPE_CHECKING:
    from .._async.query import AsyncQuerySet
    from .._sync.query import QuerySet
    from .event import Event
    from .project import Project
    from .user import User


class Cursus(FortyTwoModel):
    id: int
    name: str | None = None
    slug: str | None = None
    kind: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    restricted: bool | None = None
    is_subscriptable: bool | None = None

    @property
    def users(self) -> AsyncQuerySet[User] | QuerySet[User]:
        """Users enrolled in this cursus (``GET /cursus/{id}/users``)."""
        return self._relation("users")

    @property
    def events(self) -> AsyncQuerySet[Event] | QuerySet[Event]:
        """Events for this cursus (``GET /cursus/{id}/events``)."""
        return self._relation("events")

    @property
    def projects(self) -> AsyncQuerySet[Project] | QuerySet[Project]:
        """Projects belonging to this cursus (``GET /cursus/{id}/projects``)."""
        return self._relation("projects")
