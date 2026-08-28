from __future__ import annotations

from ...models.campus_user import CampusUser
from .base import AsyncResource


class AsyncCampusUsersResource(AsyncResource[CampusUser]):
    path = "/campus_users"
    model = CampusUser
