"""The async client, do not hand-maintain a parallel sync
implementation of the request logic here.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

import httpx

from .._auth import TokenManager
from .._config import DEFAULT_BASE_URL, ClientConfig
from .._rate_limit import RateLimiter
from ..exceptions import FortyTwoAPIError, NetworkError, raise_for_status
from .resources.accreditations import AsyncAccreditationsResource
from .resources.campus_users import AsyncCampusUsersResource
from .resources.campuses import AsyncCampusesResource
from .resources.cursus import AsyncCursusResource
from .resources.events import AsyncEventsResource
from .resources.exams import AsyncExamsResource
from .resources.locations import AsyncLocationsResource
from .resources.projects import AsyncProjectsResource
from .resources.projects_users import AsyncProjectUsersResource
from .resources.users import AsyncUsersResource


def _parse_retry_after(value: str | None) -> float:
    """Parse a ``Retry-After`` header value as seconds.

    Assumed to be the integer-seconds form.
    """
    if value is None:
        return 1.0
    try:
        return max(0.0, float(value))
    except ValueError:
        return 1.0


class AsyncClient:
    """Async client for the 42 API, authenticated via OAuth2 client credentials."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        max_retries: int = 3,
        config: ClientConfig | None = None,
    ) -> None:
        self._config = config or ClientConfig(
            base_url=base_url, timeout=timeout, max_retries=max_retries
        )
        self._http = httpx.AsyncClient(timeout=self._config.timeout)
        self._token_manager = TokenManager(client_id, client_secret)
        self._rate_limiter = RateLimiter(
            rate=self._config.rate,
            burst=self._config.burst,
            hourly_quota=self._config.hourly_quota,
        )

        self.users = AsyncUsersResource(self)
        self.accreditations = AsyncAccreditationsResource(self)
        self.campuses = AsyncCampusesResource(self)
        self.campus_users = AsyncCampusUsersResource(self)
        self.cursus = AsyncCursusResource(self)
        self.events = AsyncEventsResource(self)
        self.exams = AsyncExamsResource(self)
        self.locations = AsyncLocationsResource(self)
        self.projects = AsyncProjectsResource(self)
        self.projects_users = AsyncProjectUsersResource(self)

    @property
    def base_url(self) -> str:
        return self._config.base_url

    def _build_url(self, path: str) -> str:
        """
        Resolve ``path`` against ``base_url``.

        Absolute URLs are accepted only when their scheme and host match ``base_url``:
        every request carries the Bearer token, so following a URL to any other
        origin would leak it.
        """
        if path.startswith("http://") or path.startswith("https://"):
            target = urlsplit(path)
            base = urlsplit(self._config.base_url)
            if (target.scheme, target.netloc.lower()) != (base.scheme, base.netloc.lower()):
                raise FortyTwoAPIError("URL does not match base_url")
            return path
        return f"{self._config.base_url}{path}"

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Send one authenticated, rate-limited, error-mapped request.

        Retries on 429 up to ``max_retries`` times, honoring the response's
        ``Retry-After`` header via the shared rate limiter's cooldown gate,
        before raising :class:`intra42.exceptions.RateLimitError`.

        On a 401 the cached token is discarded and the request is retried
        once with a freshly fetched token (it may have been revoked or
        expired server-side early); a second 401 raises
        :class:`intra42.exceptions.AuthenticationError`.
        """
        url = self._build_url(path)
        rate_limit_retries = 0
        auth_retried = False

        while True:
            token = await self._token_manager.aensure_token(self._http)
            await self._rate_limiter.aacquire()
            try:
                response = await self._http.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers={"Authorization": f"Bearer {token}"},
                )
            except httpx.TransportError as exc:
                raise NetworkError(f"Request to {url} failed: {exc}") from exc

            if response.status_code == 401 and not auth_retried:
                auth_retried = True
                self._token_manager.invalidate(token)
                continue

            if response.status_code == 429:
                self._rate_limiter.notify_retry_after(
                    _parse_retry_after(response.headers.get("Retry-After"))
                )
                if rate_limit_retries < self._config.max_retries:
                    rate_limit_retries += 1
                    continue

            raise_for_status(response)
            return response

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()
