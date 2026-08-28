from __future__ import annotations

from ...models.event import Event
from .base import AsyncResource


class AsyncEventsResource(AsyncResource[Event]):
    path = "/events"
    model = Event
