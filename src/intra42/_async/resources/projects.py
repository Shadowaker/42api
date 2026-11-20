from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.project import Project
from .base import AsyncResource

if TYPE_CHECKING:
    from ...models.project_user import ProjectUser
    from ..query import AsyncQuerySet


class AsyncProjectsResource(AsyncResource[Project]):
    path = "/projects"
    model = Project

    def projects_users(self, project: int | Project) -> AsyncQuerySet[ProjectUser]:
        """Assignments to a project (``GET /projects/{id}/projects_users``).

        Referenced in the projects_users apidoc page.
        ``Project.projects_users`` delegates here.
        """
        return self._client.projects_users._queryset(self._scoped_path(project, "projects_users"))

    def _bind_relations(self, instance: Project) -> None:
        instance._bind_relation("projects_users", lambda: self.projects_users(instance))
