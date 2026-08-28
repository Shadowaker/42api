"""intra42 — an object-oriented Python client for the 42 School API.

    from intra42 import Client

    with Client(client_id, client_secret) as client:
        user = client.users.get("jdoe")
        for user in client.users.filter(campus_id=1).sort("-level"):
            ...

An async client with the same interface is available as ``AsyncClient``.
"""

from __future__ import annotations

from ._async.client import AsyncClient
from ._config import ClientConfig
from ._sync.client import Client
from .exceptions import (
    AuthenticationError,
    FortyTwoAPIError,
    NetworkError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models.campus import Campus
from .models.campus_user import CampusUser
from .models.user import User

__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "User",
    "Campus",
    "CampusUser",
    "FortyTwoAPIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
]

__version__ = "0.1.0"
