from __future__ import annotations

from ...models.campus import Campus
from .base import AsyncResource


class AsyncCampusesResource(AsyncResource[Campus]):
    path = "/campus"
    model = Campus

    def _bind_relations(self, instance: Campus) -> None:
        instance._bind_relation(
            "users",
            lambda: self._client.users._queryset(f"/campus/{instance.id}/users"),
        )
        instance._bind_relation(
            "events",
            lambda: self._client.events._queryset(f"/campus/{instance.id}/events"),
        )
