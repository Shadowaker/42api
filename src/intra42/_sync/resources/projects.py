# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from ...models.project import Project
from .base import Resource


class ProjectsResource(Resource[Project]):
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
