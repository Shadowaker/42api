from __future__ import annotations

from datetime import datetime

from .base import FortyTwoModel


class EventTheme(FortyTwoModel):
    id: int | None = None
    name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EventWaitlist(FortyTwoModel):
    id: int | None = None
    waitlistable_id: int | None = None
    waitlistable_type: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Event(FortyTwoModel):
    id: int
    name: str | None = None
    description: str | None = None
    location: str | None = None
    kind: str | None = None
    max_people: int | None = None
    nbr_subscribers: int | None = None
    begin_at: datetime | None = None
    end_at: datetime | None = None
    campus_ids: list[int] | None = None
    cursus_ids: list[int] | None = None
    themes: list[EventTheme] | None = None
    waitlist: EventWaitlist | None = None
    prohibition_of_cancellation: int | None = None
    difficulty: int | None = None
    remote: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
