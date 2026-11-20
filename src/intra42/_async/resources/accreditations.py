from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.accreditation import Accreditation
from .base import AsyncResource

if TYPE_CHECKING:
    from ...models.user import User
    from ..query import AsyncQuerySet


class AsyncAccreditationsResource(AsyncResource[Accreditation]):
    path = "/accreditations"
    model = Accreditation

    def users(self, accreditation: int | Accreditation) -> AsyncQuerySet[User]:
        """Users holding an accreditation (``GET /accreditations/{id}/users``).

        Referenced in the users apidoc page. ``Accreditation.users``
        delegates here.
        """
        return self._client.users._queryset(self._scoped_path(accreditation, "users"))

    def _bind_relations(self, instance: Accreditation) -> None:
        instance._bind_relation("users", lambda: self.users(instance))
