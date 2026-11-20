"""Mocked tests for the base_url origin check and the 401 token-refresh retry."""

import httpx
import pytest

from intra42._async.client import AsyncClient
from intra42._sync.client import Client
from intra42.exceptions import AuthenticationError, FortyTwoAPIError

USERS_URL = "https://api.intra.42.fr/v2/users"


# --- origin check -----------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example.com/v2/users?page=2",
        "http://api.intra.42.fr/v2/users?page=2",  # scheme downgrade
        "https://api.intra.42.fr.evil.example.com/v2/users",
        "https://api.intra.42.fr:8443/v2/users",  # different port
    ],
)
def test_build_url_rejects_foreign_origin(url: str) -> None:
    client = Client("id", "secret")
    try:
        with pytest.raises(FortyTwoAPIError, match="URL does not match base_url"):
            client._build_url(url)
    finally:
        client.close()


def test_build_url_accepts_same_origin_and_relative() -> None:
    client = Client("id", "secret")
    try:
        same = "https://API.intra.42.fr/v2/users?page=2"
        assert client._build_url(same) == same
        assert client._build_url("/users") == USERS_URL
    finally:
        client.close()


async def test_pagination_does_not_follow_foreign_link_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get(USERS_URL).mock(
        return_value=httpx.Response(
            200,
            json=[{"id": 1}],
            headers={"Link": '<https://evil.example.com/v2/users?page=2>; rel="next"'},
        )
    )
    evil = mock.get(url__startswith="https://evil.example.com").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        with pytest.raises(FortyTwoAPIError, match="URL does not match base_url"):
            await client.users.all()
    finally:
        await client.aclose()

    assert not evil.called


def test_pagination_does_not_follow_foreign_link_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get(USERS_URL).mock(
        return_value=httpx.Response(
            200,
            json=[{"id": 1}],
            headers={"Link": '<https://evil.example.com/v2/users?page=2>; rel="next"'},
        )
    )
    evil = mock.get(url__startswith="https://evil.example.com").mock(
        return_value=httpx.Response(200, json=[])
    )

    with Client("id", "secret") as client:
        with pytest.raises(FortyTwoAPIError, match="URL does not match base_url"):
            client.users.all()

    assert not evil.called


# --- 401 -> refresh token -> retry once ---------------------------------------


def _rotating_tokens(token_route) -> None:
    token_route.side_effect = [
        httpx.Response(200, json={"access_token": "stale-token", "expires_in": 7200}),
        httpx.Response(200, json={"access_token": "fresh-token", "expires_in": 7200}),
    ]


async def test_401_refreshes_token_and_retries_async(mock_token_route) -> None:
    mock, token_route = mock_token_route
    _rotating_tokens(token_route)
    route = mock.get(f"{USERS_URL}/1")
    route.side_effect = [
        httpx.Response(401, json={"error": "invalid_token"}),
        httpx.Response(200, json={"id": 1}),
    ]

    client = AsyncClient("id", "secret")
    try:
        user = await client.users.get(1)
    finally:
        await client.aclose()

    assert user.id == 1
    assert token_route.call_count == 2
    assert route.call_count == 2
    assert route.calls[0].request.headers["Authorization"] == "Bearer stale-token"
    assert route.calls[1].request.headers["Authorization"] == "Bearer fresh-token"


def test_401_refreshes_token_and_retries_sync(mock_token_route) -> None:
    mock, token_route = mock_token_route
    _rotating_tokens(token_route)
    route = mock.get(f"{USERS_URL}/1")
    route.side_effect = [
        httpx.Response(401, json={"error": "invalid_token"}),
        httpx.Response(200, json={"id": 1}),
    ]

    with Client("id", "secret") as client:
        user = client.users.get(1)

    assert user.id == 1
    assert token_route.call_count == 2
    assert route.calls[1].request.headers["Authorization"] == "Bearer fresh-token"


async def test_second_401_raises_authentication_error(mock_token_route) -> None:
    mock, token_route = mock_token_route
    route = mock.get(f"{USERS_URL}/1").mock(
        return_value=httpx.Response(401, json={"error": "invalid_token"})
    )

    client = AsyncClient("id", "secret")
    try:
        with pytest.raises(AuthenticationError):
            await client.users.get(1)
    finally:
        await client.aclose()

    assert route.call_count == 2  # original + exactly one retry
    assert token_route.call_count == 2


async def test_401_retry_does_not_consume_429_budget(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(f"{USERS_URL}/1")
    route.side_effect = [
        httpx.Response(401, json={"error": "invalid_token"}),
        httpx.Response(429, headers={"Retry-After": "0"}),
        httpx.Response(200, json={"id": 1}),
    ]

    client = AsyncClient("id", "secret", max_retries=1)
    try:
        user = await client.users.get(1)
    finally:
        await client.aclose()

    assert user.id == 1
    assert route.call_count == 3


def test_invalidate_keeps_newer_token() -> None:
    from intra42._auth import TokenManager

    manager = TokenManager("id", "secret")
    manager._store({"access_token": "newer", "expires_in": 7200})
    manager.invalidate("older")  # a stale caller's rejected token
    assert manager._access_token == "newer"
    manager.invalidate("newer")
    assert manager._access_token is None
