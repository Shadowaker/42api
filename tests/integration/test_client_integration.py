import httpx
import pytest

from intra42._async.client import AsyncClient
from intra42._sync.client import Client
from intra42.exceptions import NotFoundError, RateLimitError


async def test_get_user_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "jdoe"})
    )

    client = AsyncClient("id", "secret")
    try:
        user = await client.users.get(1)
    finally:
        await client.aclose()

    assert user.id == 1
    assert user.login == "jdoe"


async def test_get_user_sends_bearer_token(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )

    client = AsyncClient("id", "secret")
    try:
        await client.users.get(1)
    finally:
        await client.aclose()

    assert route.calls.last.request.headers["Authorization"] == "Bearer test-token"


async def test_404_raises_not_found_error(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/999").mock(
        return_value=httpx.Response(404, json={"error": "Not Found"})
    )

    client = AsyncClient("id", "secret")
    try:
        with pytest.raises(NotFoundError):
            await client.users.get(999)
    finally:
        await client.aclose()


async def test_429_retries_then_succeeds(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users/1")
    route.side_effect = [
        httpx.Response(429, headers={"Retry-After": "0"}, json={"error": "rate limited"}),
        httpx.Response(200, json={"id": 1}),
    ]

    client = AsyncClient("id", "secret")
    try:
        user = await client.users.get(1)
    finally:
        await client.aclose()

    assert user.id == 1
    assert route.call_count == 2


async def test_429_exhausts_retries_raises_rate_limit_error(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users/1").mock(
        return_value=httpx.Response(
            429, headers={"Retry-After": "0"}, json={"error": "rate limited"}
        )
    )

    client = AsyncClient("id", "secret", max_retries=1)
    try:
        with pytest.raises(RateLimitError):
            await client.users.get(1)
    finally:
        await client.aclose()

    assert route.call_count == 2  # initial attempt + 1 retry


def test_get_user_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "jdoe"})
    )

    client = Client("id", "secret")
    try:
        user = client.users.get(1)
    finally:
        client.close()

    assert user.id == 1
    assert user.login == "jdoe"


def test_404_raises_not_found_error_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/999").mock(
        return_value=httpx.Response(404, json={"error": "Not Found"})
    )

    client = Client("id", "secret")
    try:
        with pytest.raises(NotFoundError):
            client.users.get(999)
    finally:
        client.close()


def test_client_as_context_manager_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )

    with Client("id", "secret") as client:
        user = client.users.get(1)

    assert user.id == 1
