"""intra42 — an object-oriented Python client for the 42 School API.

    from intra42 import Client

    with Client(client_id, client_secret) as client:
        user = client.users.get("jdoe")
        for user in client.users.filter(primary_campus_id=1).sort("-pool_year"):
            ...

An async client with the same interface is available as ``AsyncClient``.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

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
from .models.accreditation import Accreditation
from .models.campus import Campus
from .models.campus_user import CampusUser
from .models.cursus import Cursus
from .models.event import Event
from .models.exam import Exam
from .models.location import Location
from .models.project import Project
from .models.project_user import ProjectUser
from .models.user import User

__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "User",
    "Accreditation",
    "Campus",
    "CampusUser",
    "Cursus",
    "Event",
    "Exam",
    "Location",
    "Project",
    "ProjectUser",
    "FortyTwoAPIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
]

# Single source of truth is pyproject.toml; read it from the installed
# distribution metadata rather than hardcoding a copy that drifts.
try:
    __version__ = version("42api")
except PackageNotFoundError:  # pragma: no cover - running from an uninstalled source tree
    __version__ = "0.0.0+unknown"
