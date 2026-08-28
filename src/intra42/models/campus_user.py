"""The ``CampusUser`` resource: the join between a user and a campus."""

from __future__ import annotations

from datetime import datetime

from .base import FortyTwoModel


class CampusUser(FortyTwoModel):
    id: int
    user_id: int | None = None
    campus_id: int | None = None
    is_primary: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
