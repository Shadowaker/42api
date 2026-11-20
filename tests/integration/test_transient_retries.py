"""Retry/backoff on transient 5xx and network errors (issue #3)."""

from __future__ import annotations

import httpx
import pytest

from intra42 import ClientConfig
from intra42._async.client import AsyncClient
from intra42._sync.client import Client
from intra42.exceptions import NetworkError, RateLimitError, ServerError

URL = "https://api.intra.42.fr/v2/users/1"
OK = httpx.Response(200, json={"id": 1})


def _config(**overrides) -> ClientConfig:
    return ClientConfig(**{"retry_backoff": 0.0, **overrides})


def _record_delays(client: Client | AsyncClient) -> list[float]:
    """Replace the cooldown gate with a recorder, so tests never really sleep."""
    delays: list[float] = []
    client._rate_limiter.notify_retry_after = delays.append  # type: ignore[method-assign]
    return delays


# --- 5xx -----------------------------------------------------------------------


@pytest.mark.parametrize("status", [502, 503, 504])
async def test_transient_5xx_is_retried_async(mock_token_route, status: int) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL)
    route.side_effect = [httpx.Response(status), OK]

    client = AsyncClient("id", "secret", config=_config())
    try:
        user = await client.users.get(1)
    finally:
        await client.aclose()

    assert user.id == 1
    assert route.call_count == 2


def test_transient_5xx_exhausts_budget_raises_server_error(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL).mock(return_value=httpx.Response(503))

    with Client("id", "secret", config=_config(max_retries=2)) as client:
        with pytest.raises(ServerError):
            client.users.get(1)

    assert route.call_count == 3  # initial + 2 retries


def test_500_is_not_retried(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL).mock(return_value=httpx.Response(500))

    with Client("id", "secret", config=_config()) as client:
        with pytest.raises(ServerError):
            client.users.get(1)

    assert route.call_count == 1


def test_5xx_on_non_idempotent_method_is_not_retried(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.post("https://api.intra.42.fr/v2/users").mock(return_value=httpx.Response(503))

    with Client("id", "secret", config=_config()) as client:
        with pytest.raises(ServerError):
            client.request("POST", "/users", json={"login": "x"})

    assert route.call_count == 1


def test_5xx_honors_retry_after(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL)
    route.side_effect = [httpx.Response(503, headers={"Retry-After": "7"}), OK]

    with Client("id", "secret", config=_config(retry_backoff=1.0)) as client:
        delays = _record_delays(client)
        client.users.get(1)

    assert delays == [7.0]


def test_backoff_grows_exponentially_with_jitter(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL)
    route.side_effect = [httpx.Response(502), httpx.Response(502), httpx.Response(502), OK]

    with Client("id", "secret", config=_config(retry_backoff=1.0)) as client:
        delays = _record_delays(client)
        client.users.get(1)

    caps = [1.0, 2.0, 4.0]
    assert len(delays) == 3
    assert all(0.0 <= d <= cap for d, cap in zip(delays, caps, strict=True))


# --- network errors ---------------------------------------------------------------


async def test_read_timeout_on_get_is_retried_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL)
    route.side_effect = [httpx.ReadTimeout("slow"), OK]

    client = AsyncClient("id", "secret", config=_config())
    try:
        user = await client.users.get(1)
    finally:
        await client.aclose()

    assert user.id == 1
    assert route.call_count == 2


def test_network_errors_exhaust_budget_raise_network_error(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL).mock(side_effect=httpx.RemoteProtocolError("reset"))

    with Client("id", "secret", config=_config(max_retries=2)) as client:
        with pytest.raises(NetworkError):
            client.users.get(1)

    assert route.call_count == 3


def test_read_timeout_on_post_is_not_retried(mock_token_route) -> None:
    """The server may already have processed the POST: resending could duplicate it."""
    mock, _ = mock_token_route
    route = mock.post("https://api.intra.42.fr/v2/users").mock(
        side_effect=httpx.ReadTimeout("slow")
    )

    with Client("id", "secret", config=_config()) as client:
        with pytest.raises(NetworkError):
            client.request("POST", "/users", json={"login": "x"})

    assert route.call_count == 1


def test_connect_error_on_post_is_retried(mock_token_route) -> None:
    """A failed connect means nothing was sent, so even a POST is safe to retry."""
    mock, _ = mock_token_route
    route = mock.post("https://api.intra.42.fr/v2/users")
    route.side_effect = [httpx.ConnectError("refused"), httpx.Response(201, json={"id": 2})]

    with Client("id", "secret", config=_config()) as client:
        response = client.request("POST", "/users", json={"login": "x"})

    assert response.status_code == 201
    assert route.call_count == 2


# --- shared budget -----------------------------------------------------------------


async def test_429_and_5xx_share_the_retry_budget(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL)
    route.side_effect = [
        httpx.Response(429, headers={"Retry-After": "0"}),
        httpx.Response(503),
        OK,
    ]

    client = AsyncClient("id", "secret", config=_config(max_retries=1))
    try:
        with pytest.raises(ServerError):
            await client.users.get(1)
    finally:
        await client.aclose()

    assert route.call_count == 2


def test_5xx_then_429_exhaustion_raises_rate_limit_error(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(URL)
    route.side_effect = [httpx.Response(503), httpx.Response(429, headers={"Retry-After": "0"})]

    with Client("id", "secret", config=_config(max_retries=1)) as client:
        with pytest.raises(RateLimitError):
            client.users.get(1)

    assert route.call_count == 2
