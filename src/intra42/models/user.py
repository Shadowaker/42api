from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from .base import FortyTwoModel

if TYPE_CHECKING:
    from .._async.query import AsyncQuerySet
    from .._sync.query import QuerySet
    from .campus_user import CampusUser
    from .event import Event


class ImageVersions(FortyTwoModel):
    large: str | None = None
    medium: str | None = None
    small: str | None = None
    micro: str | None = None


class Image(FortyTwoModel):
    link: str | None = None
    versions: ImageVersions | None = None


class User(FortyTwoModel):
    id: int
    email: str | None = None
    login: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    usual_full_name: str | None = None
    usual_first_name: str | None = None
    url: str | None = None
    phone: str | None = None
    displayname: str | None = None
    kind: str | None = None
    image: Image | None = None
    staff: bool | None = Field(default=None, alias="staff?")
    correction_point: int | None = None
    pool_month: str | None = None
    pool_year: str | None = None
    location: str | None = None
    wallet: int | None = None
    anonymize_date: datetime | None = None
    data_erasure_date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    alumnized_at: datetime | None = None
    alumni: bool | None = Field(default=None, alias="alumni?")
    active: bool | None = Field(default=None, alias="active?")

    @property
    def events(self) -> AsyncQuerySet[Event] | QuerySet[Event]:
        """Events scoped to this user (``GET /users/{id}/events``)"""
        return self._relation("events")

    @property
    def campus_users(self) -> AsyncQuerySet[CampusUser] | QuerySet[CampusUser]:
        """This user's campus memberships (``GET /users/{id}/campus_users``)."""
        return self._relation("campus_users")
