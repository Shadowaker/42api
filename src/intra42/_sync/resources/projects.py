# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.project import Project
from .base import Resource

if TYPE_CHECKING:
    from ...models.project_user import ProjectUser
    from ..query import QuerySet


class ProjectsResource(Resource[Project]):
    path = "/projects"
    model = Project

    def projects_users(self, project: int | Project) -> QuerySet[ProjectUser]:
        """Assignments to a project (``GET /projects/{id}/projects_users``).

        Referenced in the projects_users apidoc page.
        ``Project.projects_users`` delegates here.
        """
        return self._client.projects_users._queryset(self._scoped_path(project, "projects_users"))

    def _bind_relations(self, instance: Project) -> None:
        instance._bind_relation("projects_users", lambda: self.projects_users(instance))
