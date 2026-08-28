from __future__ import annotations

from typing import TYPE_CHECKING

from .base import FortyTwoModel

if TYPE_CHECKING:
    from .._async.query import AsyncQuerySet
    from .._sync.query import QuerySet
    from .event import Event
    from .user import User


class CampusLanguage(FortyTwoModel):
    id: int
    name: str | None = None
    identifier: str | None = None


class CampusEndpoint(FortyTwoModel):
    id: int
    url: str | None = None
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class Campus(FortyTwoModel):
    id: int
    name: str
    time_zone: str | None = None
    language: CampusLanguage | None = None
    users_count: int | None = None
    vogsphere_id: int | None = None
    country: str | None = None
    address: str | None = None
    zip: str | None = None
    city: str | None = None
    website: str | None = None
    facebook: str | None = None
    twitter: str | None = None
    active: bool | None = None
    public: bool | None = None
    email_extension: str | None = None
    default_hidden_phone: bool | None = None
    endpoint: CampusEndpoint | None = None

    @property
    def users(self) -> AsyncQuerySet[User] | QuerySet[User]:
        """Users of this campus (``GET /campus/{id}/users``).

        Lazily-paginating. Only available on instances fetched via
        ``Client``/``AsyncClient`` — see ``FortyTwoModel._relation``.
        """
        return self._relation("users")

    @property
    def events(self) -> AsyncQuerySet[Event] | QuerySet[Event]:
        """Events at this campus (``GET /campus/{id}/events``)."""
        return self._relation("events")
