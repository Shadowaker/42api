from __future__ import annotations

from ...models.user import User
from .base import AsyncResource


class AsyncUsersResource(AsyncResource[User]):
    path = "/users"
    model = User

    def _bind_relations(self, instance: User) -> None:
        instance._bind_relation(
            "events",
            lambda: self._client.events._queryset(f"/users/{instance.id}/events"),
        )
        instance._bind_relation(
            "campus_users",
            lambda: self._client.campus_users._queryset(f"/users/{instance.id}/campus_users"),
        )
