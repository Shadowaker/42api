"""The async client, do not hand-maintain a parallel sync
implementation of the request logic here.
"""

from __future__ import annotations

from typing import Any

import httpx

from .._auth import TokenManager
from .._config import DEFAULT_BASE_URL, ClientConfig
from .._rate_limit import RateLimiter
from ..exceptions import NetworkError, raise_for_status
from .resources.campuses import AsyncCampusesResource
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
        self.campuses = AsyncCampusesResource(self)

    @property
    def base_url(self) -> str:
        return self._config.base_url

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
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
        """
        url = self._build_url(path)
        response: httpx.Response | None = None

        for attempt in range(self._config.max_retries + 1):
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

            if response.status_code == 429:
                self._rate_limiter.notify_retry_after(
                    _parse_retry_after(response.headers.get("Retry-After"))
                )
                if attempt < self._config.max_retries:
                    continue

            raise_for_status(response)
            return response

        assert response is not None  # loop always runs at least once
        raise_for_status(response)
        return response  # pragma: no cover - raise_for_status always raises on a 429

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()
