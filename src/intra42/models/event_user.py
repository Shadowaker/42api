"""The ``EventUser`` resource: a user's registration to an event."""

from __future__ import annotations

from datetime import datetime

from .base import FortyTwoModel


class EventUserEventRef(FortyTwoModel):
    id: int | None = None
    name: str | None = None
    location: str | None = None
    kind: str | None = None
    begin_at: datetime | None = None
    end_at: datetime | None = None


class EventUserUserRef(FortyTwoModel):
    id: int | None = None
    login: str | None = None
    url: str | None = None


class EventUser(FortyTwoModel):
    id: int
    event_id: int | None = None
    user_id: int | None = None
    event: EventUserEventRef | None = None
    user: EventUserUserRef | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
