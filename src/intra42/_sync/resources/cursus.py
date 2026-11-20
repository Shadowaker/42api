# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.cursus import Cursus
from .base import Resource

if TYPE_CHECKING:
    from ...models.event import Event
    from ...models.project import Project
    from ...models.user import User
    from ..query import QuerySet


class CursusResource(Resource[Cursus]):
    path = "/cursus"
    model = Cursus

    # Exactly-typed nested accessors. `cursus` may be an id or a fetched
    # Cursus; the matching `Cursus.<name>` properties delegate here.

    def users(self, cursus: int | Cursus) -> QuerySet[User]:
        """Users in a cursus (``GET /cursus/{id}/users``)."""
        return self._client.users._queryset(self._scoped_path(cursus, "users"))

    def events(self, cursus: int | Cursus) -> QuerySet[Event]:
        """Events of a cursus (``GET /cursus/{id}/events``)."""
        return self._client.events._queryset(self._scoped_path(cursus, "events"))

    def projects(self, cursus: int | Cursus) -> QuerySet[Project]:
        """Projects of a cursus (``GET /cursus/{id}/projects``)."""
        return self._client.projects._queryset(self._scoped_path(cursus, "projects"))

    def _bind_relations(self, instance: Cursus) -> None:
        instance._bind_relation("users", lambda: self.users(instance))
        instance._bind_relation("events", lambda: self.events(instance))
        instance._bind_relation("projects", lambda: self.projects(instance))
