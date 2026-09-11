from __future__ import annotations

from ...models.project_user import ProjectUser
from .base import AsyncResource


class AsyncProjectUsersResource(AsyncResource[ProjectUser]):
    path = "/projects_users"
    model = ProjectUser

    async def graph(
        self, *, field: str | None = None, interval: str | None = None
    ) -> dict[str, int]:
        path = "/projects_users/graph"
        if interval is not None and field is None:
            field = "created_at"
        if field is not None:
            path += f"/on/{field}"
            if interval is not None:
                path += f"/by/{interval}"
        response = await self._client.request("GET", path)
        return response.json()
