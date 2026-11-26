import json

import httpx
import pytest

from intra42._async.client import AsyncClient
from intra42._sync.client import Client
from intra42.exceptions import AuthenticationError

EVENTS_USER_JSON = {
    "id": 42,
    "event_id": 3,
    "user_id": 25,
    "created_at": "2017-11-22T13:42:10.037Z",
    "updated_at": "2017-11-22T13:42:10.082Z",
}


async def test_get_events_user_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/events_users/42").mock(
        return_value=httpx.Response(200, json=EVENTS_USER_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        eu = await client.events_users.get(42)
    finally:
        await client.aclose()

    assert eu.id == 42
    assert eu.event_id == 3
    assert eu.user_id == 25


async def test_filter_events_users_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/events_users").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.events_users.filter(event_id=3).sort("-created_at").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[event_id]"] == "3"
    assert request.url.params["sort"] == "-created_at"


async def test_subscribe_posts_wrapped_payload_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.post("https://api.intra.42.fr/v2/events_users").mock(
        return_value=httpx.Response(201, json=EVENTS_USER_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        eu = await client.events_users.subscribe(event_id=3, user_id=25)
    finally:
        await client.aclose()

    assert eu.id == 42
    assert eu.event_id == 3
    body = json.loads(route.calls.last.request.content)
    assert body == {"events_user": {"event_id": 3, "user_id": 25}}


def test_subscribe_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.post("https://api.intra.42.fr/v2/events_users").mock(
        return_value=httpx.Response(201, json=EVENTS_USER_JSON)
    )

    with Client("id", "secret") as client:
        eu = client.events_users.subscribe(event_id=3, user_id=25)

    assert eu.user_id == 25
    assert route.called


async def test_unsubscribe_deletes_by_id_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.delete("https://api.intra.42.fr/v2/events_users/42").mock(
        return_value=httpx.Response(204)
    )

    client = AsyncClient("id", "secret")
    try:
        result = await client.events_users.unsubscribe(42)
    finally:
        await client.aclose()

    assert result is None
    assert route.called
    assert route.calls.last.request.method == "DELETE"


def test_unsubscribe_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.delete("https://api.intra.42.fr/v2/events_users/42").mock(
        return_value=httpx.Response(204)
    )

    with Client("id", "secret") as client:
        client.events_users.unsubscribe(42)

    assert route.called


async def test_subscribe_with_user_token_uses_bearer_and_skips_token_endpoint(
    mock_token_route,
) -> None:
    mock, token_route = mock_token_route
    post = mock.post("https://api.intra.42.fr/v2/events_users").mock(
        return_value=httpx.Response(201, json=EVENTS_USER_JSON)
    )

    client = AsyncClient.from_access_token("user-token-abc")
    try:
        await client.events_users.subscribe(event_id=3, user_id=25)
    finally:
        await client.aclose()

    # The caller's user token is sent verbatim; no client-credentials exchange.
    assert post.calls.last.request.headers["authorization"] == "Bearer user-token-abc"
    assert token_route.called is False


async def test_user_token_401_raises_auth_error_without_token_exchange(
    mock_token_route,
) -> None:
    mock, token_route = mock_token_route
    post = mock.post("https://api.intra.42.fr/v2/events_users").mock(
        return_value=httpx.Response(401, json={"error": "unauthorized"})
    )

    client = AsyncClient.from_access_token("revoked-token")
    try:
        with pytest.raises(AuthenticationError):
            await client.events_users.subscribe(event_id=3, user_id=25)
    finally:
        await client.aclose()

    # The 401 handler invalidates (a no-op for a static token, not an
    # AttributeError) and retries once with the same token; the second 401
    # surfaces as AuthenticationError. No client-credentials exchange happens.
    assert len(post.calls) == 2
    assert token_route.called is False
