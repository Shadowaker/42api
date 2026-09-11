# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from ...models.accreditation import Accreditation
from .base import Resource


class AccreditationsResource(Resource[Accreditation]):
    path = "/accreditations"
    model = Accreditation

    def _bind_relations(self, instance: Accreditation) -> None:
        # Referenced in the users apidoc page: GET /accreditations/:id/users.
        instance._bind_relation(
            "users",
            lambda: self._client.users._queryset(f"/accreditations/{instance.id}/users"),
        )
