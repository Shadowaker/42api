# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.campus import Campus
from .base import Resource

if TYPE_CHECKING:
    from ...models.event import Event
    from ...models.location import Location
    from ...models.user import User
    from ..query import QuerySet


class CampusesResource(Resource[Campus]):
    path = "/campus"
    model = Campus

    # Exactly-typed nested accessors. `campus` may be an id or a fetched
    # Campus; the matching `Campus.<name>` properties delegate here.

    def users(self, campus: int | Campus) -> QuerySet[User]:
        """Users of a campus (``GET /campus/{id}/users``)."""
        return self._client.users._queryset(self._scoped_path(campus, "users"))

    def events(self, campus: int | Campus) -> QuerySet[Event]:
        """Events at a campus (``GET /campus/{id}/events``)."""
        return self._client.events._queryset(self._scoped_path(campus, "events"))

    def locations(self, campus: int | Campus) -> QuerySet[Location]:
        """Login sessions at a campus (``GET /campus/{id}/locations``)."""
        return self._client.locations._queryset(self._scoped_path(campus, "locations"))

    def _bind_relations(self, instance: Campus) -> None:
        instance._bind_relation("users", lambda: self.users(instance))
        instance._bind_relation("events", lambda: self.events(instance))
        instance._bind_relation("locations", lambda: self.locations(instance))
