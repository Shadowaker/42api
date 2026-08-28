from __future__ import annotations

from ...models.campus import Campus
from .base import AsyncResource


class AsyncCampusesResource(AsyncResource[Campus]):
    path = "/campuses"
    model = Campus
