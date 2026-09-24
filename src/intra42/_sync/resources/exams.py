# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from ...models.exam import Exam
from .base import Resource


class ExamsResource(Resource[Exam]):
    path = "/exams"
    model = Exam

    def graph(self, *, field: str | None = None, interval: str | None = None) -> dict[str, int]:
        """Grouped temporal counts (``GET /exams/graph...``)."""
        path = "/exams/graph"
        if interval is not None and field is None:
            field = "created_at"
        if field is not None:
            path += f"/on/{field}"
            if interval is not None:
                path += f"/by/{interval}"
        response = self._client.request("GET", path)
        return response.json()
