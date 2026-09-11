"""The ``Accreditation`` resource."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .base import FortyTwoModel

if TYPE_CHECKING:
    from .._async.query import AsyncQuerySet
    from .._sync.query import QuerySet
    from .user import User


class Accreditation(FortyTwoModel):
    id: int
    name: str | None = None
    user_id: int | None = None
    cursus_id: int | None = None
    difficulty: int | None = None
    validated: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def users(self) -> AsyncQuerySet[User] | QuerySet[User]:
        """Users holding this accreditation (``GET /accreditations/{id}/users``)."""
        return self._relation("users")
