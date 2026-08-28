# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from ...models.campus_user import CampusUser
from .base import Resource


class SyncCampusUsersResource(Resource[CampusUser]):
    path = "/campus_users"
    model = CampusUser
