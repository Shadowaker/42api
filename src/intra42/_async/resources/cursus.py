from __future__ import annotations

from ...models.cursus import Cursus
from .base import AsyncResource


class AsyncCursusResource(AsyncResource[Cursus]):
    path = "/cursus"
    model = Cursus

    def _bind_relations(self, instance: Cursus) -> None:
        instance._bind_relation(
            "users",
            lambda: self._client.users._queryset(f"/cursus/{instance.id}/users"),
        )
        instance._bind_relation(
            "events",
            lambda: self._client.events._queryset(f"/cursus/{instance.id}/events"),
        )
        instance._bind_relation(
            "projects",
            lambda: self._client.projects._queryset(f"/cursus/{instance.id}/projects"),
        )
