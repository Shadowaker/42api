# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.user import User
from .base import Resource

if TYPE_CHECKING:
    from ...models.campus_user import CampusUser
    from ...models.event import Event
    from ...models.location import Location
    from ...models.project_user import ProjectUser
    from ..query import QuerySet


class UsersResource(Resource[User]):
    path = "/users"
    model = User

    # Exactly-typed nested accessors. `user` may be an id, a login or a
    # fetched User; the matching `User.<name>` properties delegate here.

    def events(self, user: int | str | User) -> QuerySet[Event]:
        """Events of a user (``GET /users/{id}/events``)."""
        return self._client.events._queryset(self._scoped_path(user, "events"))

    def campus_users(self, user: int | str | User) -> QuerySet[CampusUser]:
        """Campus memberships of a user (``GET /users/{id}/campus_users``)."""
        return self._client.campus_users._queryset(self._scoped_path(user, "campus_users"))

    def locations(self, user: int | str | User) -> QuerySet[Location]:
        """Login sessions of a user (``GET /users/{id}/locations``)."""
        return self._client.locations._queryset(self._scoped_path(user, "locations"))

    def projects_users(self, user: int | str | User) -> QuerySet[ProjectUser]:
        """Project assignments of a user (``GET /users/{id}/projects_users``)."""
        return self._client.projects_users._queryset(self._scoped_path(user, "projects_users"))

    def _bind_relations(self, instance: User) -> None:
        instance._bind_relation("events", lambda: self.events(instance))
        instance._bind_relation("campus_users", lambda: self.campus_users(instance))
        instance._bind_relation("locations", lambda: self.locations(instance))
        instance._bind_relation("projects_users", lambda: self.projects_users(instance))
