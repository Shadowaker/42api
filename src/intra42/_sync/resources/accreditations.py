# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.accreditation import Accreditation
from .base import Resource

if TYPE_CHECKING:
    from ...models.user import User
    from ..query import QuerySet


class AccreditationsResource(Resource[Accreditation]):
    path = "/accreditations"
    model = Accreditation

    def users(self, accreditation: int | Accreditation) -> QuerySet[User]:
        """Users holding an accreditation (``GET /accreditations/{id}/users``).

        Referenced in the users apidoc page. ``Accreditation.users``
        delegates here.
        """
        return self._client.users._queryset(self._scoped_path(accreditation, "users"))

    def _bind_relations(self, instance: Accreditation) -> None:
        instance._bind_relation("users", lambda: self.users(instance))
