from __future__ import annotations

from ...models.accreditation import Accreditation
from .base import AsyncResource


class AsyncAccreditationsResource(AsyncResource[Accreditation]):
    path = "/accreditations"
    model = Accreditation

    def _bind_relations(self, instance: Accreditation) -> None:
        # Referenced in the users apidoc page: GET /accreditations/:id/users.
        instance._bind_relation(
            "users",
            lambda: self._client.users._queryset(f"/accreditations/{instance.id}/users"),
        )
