"""OAuth2 client-credentials token acquisition and caching.

:class:`TokenManager` is shared, mutable state used from both the sync and
async clients. Both paths guard the same cached-token state with a lock and use
double-checked locking so concurrent callers queued on the lock don't each
trigger a redundant refresh.
"""

from __future__ import annotations

import asyncio
import threading
import time

import httpx

from .exceptions import AuthenticationError

TOKEN_URL = "https://api.intra.42.fr/oauth/token"

DEFAULT_LEEWAY = 60.0  # Refresh before expire


class TokenManager:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        token_url: str = TOKEN_URL,
        leeway: float = DEFAULT_LEEWAY,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._leeway = leeway

        self._access_token: str | None = None
        self._expires_at: float = 0.0

        self._lock = threading.Lock()
        self._alock = asyncio.Lock()

    def _is_valid(self) -> bool:
        return self._access_token is not None and time.time() < self._expires_at - self._leeway

    def invalidate(self, token: str) -> None:
        with self._lock:
            if self._access_token == token:
                self._access_token = None
                self._expires_at = 0.0

    def _body(self) -> dict[str, str]:
        return {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

    def _store(self, payload: dict[str, object]) -> str:
        token = payload.get("access_token")
        if not isinstance(token, str):
            raise AuthenticationError(
                "Token endpoint response did not include an access_token",
            )
        expires_in = payload.get("expires_in", 7200)
        try:
            expires_in = float(expires_in)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            expires_in = 7200.0
        self._access_token = token
        self._expires_at = time.time() + expires_in
        return token

    def ensure_token(self, http: httpx.Client) -> str:
        if self._is_valid():
            return self._access_token  # type: ignore[return-value]
        with self._lock:
            if self._is_valid():
                return self._access_token  # type: ignore[return-value]
            try:
                response = http.post(self._token_url, data=self._body())
            except httpx.TransportError as exc:
                raise AuthenticationError(f"Failed to reach token endpoint: {exc}") from exc
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Token endpoint rejected credentials (status {response.status_code})",
                    status_code=response.status_code,
                    response=response,
                )
            return self._store(response.json())

    async def aensure_token(self, http: httpx.AsyncClient) -> str:
        if self._is_valid():
            return self._access_token  # type: ignore[return-value]
        async with self._alock:
            if self._is_valid():
                return self._access_token  # type: ignore[return-value]
            try:
                response = await http.post(self._token_url, data=self._body())
            except httpx.TransportError as exc:
                raise AuthenticationError(f"Failed to reach token endpoint: {exc}") from exc
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Token endpoint rejected credentials (status {response.status_code})",
                    status_code=response.status_code,
                    response=response,
                )
            return self._store(response.json())


class StaticTokenManager:
    """A token source backed by a pre-obtained access token.

    Used when a client acts on behalf of a user (authorization-code flow)
    rather than as the application (client-credentials). The token is used
    verbatim and never refreshed, so write endpoints that require a
    resource-owner token (e.g. ``events_users``) can be called. Exposes the
    same ``ensure_token`` / ``aensure_token`` interface as :class:`TokenManager`.
    """

    def __init__(self, access_token: str) -> None:
        if not access_token:
            raise AuthenticationError("access_token must be a non-empty string")
        self._access_token = access_token

    def invalidate(self, token: str) -> None:
        """No-op: a caller-supplied token has no cached state to refresh.

        Part of the token-source interface the client's 401 handler relies on.
        Unlike :class:`TokenManager`, there is no credentials grant to re-run, so
        the token is kept as-is; the handler's single retry re-sends it and a
        second 401 surfaces as :class:`AuthenticationError`.
        """

    def ensure_token(self, http: httpx.Client) -> str:
        return self._access_token

    async def aensure_token(self, http: httpx.AsyncClient) -> str:
        return self._access_token
