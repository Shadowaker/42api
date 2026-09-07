"""The ``Location`` resource: a login session at a workstation."""

from __future__ import annotations

from datetime import datetime

from .base import FortyTwoModel


class LocationUser(FortyTwoModel):
    id: int | None = None
    login: str | None = None
    url: str | None = None


class Location(FortyTwoModel):
    id: int
    begin_at: datetime | None = None
    end_at: datetime | None = None
    primary: bool | None = None
    floor: str | None = None
    row: str | None = None
    post: str | None = None
    host: str | None = None
    campus_id: int | None = None
    user: LocationUser | None = None
