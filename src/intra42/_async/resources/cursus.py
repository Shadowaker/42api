from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.cursus import Cursus
from .base import AsyncResource

if TYPE_CHECKING:
    from ...models.event import Event
    from ...models.project import Project
    from ...models.user import User
    from ..query import AsyncQuerySet


class AsyncCursusResource(AsyncResource[Cursus]):
    path = "/cursus"
    model = Cursus

    # Exactly-typed nested accessors. `cursus` may be an id or a fetched
    # Cursus; the matching `Cursus.<name>` properties delegate here.

    def users(self, cursus: int | Cursus) -> AsyncQuerySet[User]:
        """Users in a cursus (``GET /cursus/{id}/users``)."""
        return self._client.users._queryset(self._scoped_path(cursus, "users"))

    def events(self, cursus: int | Cursus) -> AsyncQuerySet[Event]:
        """Events of a cursus (``GET /cursus/{id}/events``)."""
        return self._client.events._queryset(self._scoped_path(cursus, "events"))

    def projects(self, cursus: int | Cursus) -> AsyncQuerySet[Project]:
        """Projects of a cursus (``GET /cursus/{id}/projects``)."""
        return self._client.projects._queryset(self._scoped_path(cursus, "projects"))

    def _bind_relations(self, instance: Cursus) -> None:
        instance._bind_relation("users", lambda: self.users(instance))
        instance._bind_relation("events", lambda: self.events(instance))
        instance._bind_relation("projects", lambda: self.projects(instance))
