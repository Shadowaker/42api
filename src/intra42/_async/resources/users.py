from __future__ import annotations

from ...models.user import User
from .base import AsyncResource


class AsyncUsersResource(AsyncResource[User]):
    path = "/users"
    model = User
