from __future__ import annotations

from ...models.exam import Exam
from .base import AsyncResource


class AsyncExamsResource(AsyncResource[Exam]):
    path = "/exams"
    model = Exam

    async def graph(
        self, *, field: str | None = None, interval: str | None = None
    ) -> dict[str, int]:
        """Grouped temporal counts (``GET /exams/graph...``)."""
        path = "/exams/graph"
        if interval is not None and field is None:
            field = "created_at"
        if field is not None:
            path += f"/on/{field}"
            if interval is not None:
                path += f"/by/{interval}"
        response = await self._client.request("GET", path)
        return response.json()
