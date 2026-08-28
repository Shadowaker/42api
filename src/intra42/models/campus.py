from __future__ import annotations

from .base import FortyTwoModel


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
