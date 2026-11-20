from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.campus import Campus
from .base import AsyncResource

if TYPE_CHECKING:
    from ...models.event import Event
    from ...models.location import Location
    from ...models.user import User
    from ..query import AsyncQuerySet


class AsyncCampusesResource(AsyncResource[Campus]):
    path = "/campus"
    model = Campus

    # Exactly-typed nested accessors. `campus` may be an id or a fetched
    # Campus; the matching `Campus.<name>` properties delegate here.

    def users(self, campus: int | Campus) -> AsyncQuerySet[User]:
        """Users of a campus (``GET /campus/{id}/users``)."""
        return self._client.users._queryset(self._scoped_path(campus, "users"))

    def events(self, campus: int | Campus) -> AsyncQuerySet[Event]:
        """Events at a campus (``GET /campus/{id}/events``)."""
        return self._client.events._queryset(self._scoped_path(campus, "events"))

    def locations(self, campus: int | Campus) -> AsyncQuerySet[Location]:
        """Login sessions at a campus (``GET /campus/{id}/locations``)."""
        return self._client.locations._queryset(self._scoped_path(campus, "locations"))

    def _bind_relations(self, instance: Campus) -> None:
        instance._bind_relation("users", lambda: self.users(instance))
        instance._bind_relation("events", lambda: self.events(instance))
        instance._bind_relation("locations", lambda: self.locations(instance))
