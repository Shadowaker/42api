from __future__ import annotations

from ...models.project import Project
from .base import AsyncResource


class AsyncProjectsResource(AsyncResource[Project]):
    path = "/projects"
    model = Project

    def _bind_relations(self, instance: Project) -> None:
        # Referenced in the projects_users apidoc page:
        # GET /projects/:id/projects_users.
        instance._bind_relation(
            "projects_users",
            lambda: self._client.projects_users._queryset(
                f"/projects/{instance.id}/projects_users"
            ),
        )
