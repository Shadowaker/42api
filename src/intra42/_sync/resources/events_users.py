# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

from __future__ import annotations

from ..._paths import path_segment
from ...models.event_user import EventUser
from .base import Resource


class EventsUsersResource(Resource[EventUser]):
    path = "/events_users"
    model = EventUser

    def subscribe(self, *, event_id: int, user_id: int) -> EventUser:
        """Register a user to an event: ``POST /v2/events_users``.

        This is a write action: it requires a resource-owner (user) token
        scoped on ``profile`` with enough privileges (a student registering
        themselves), or an application with the ``Advanced staff`` or
        ``Events manager`` role. The app-level client-credentials token used
        for read endpoints is not sufficient — build the client with
        :meth:`AsyncClient.from_access_token` (a user token) to call this.

        ``user_id`` must be unique within the scope of a given event.
        """
        response = self._client.request(
            "POST",
            self.path,
            json={"events_user": {"event_id": event_id, "user_id": user_id}},
        )
        return EventUser.model_validate(response.json())

    def unsubscribe(self, id: int) -> None:
        """Cancel a registration: ``DELETE /v2/events_users/{id}``.

        Like :meth:`subscribe`, this requires a resource-owner token scoped on
        ``profile`` (or a sufficiently privileged application).

        ``id`` is percent-encoded as one path segment.
        """
        self._client.request("DELETE", f"{self.path}/{path_segment(id)}")
