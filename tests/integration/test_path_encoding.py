"""Caller-supplied values must stay inside their own URL path segment."""

import httpx
import pytest

from intra42._async.client import AsyncClient
from intra42._sync.client import Client
from intra42.exceptions import NotFoundError


async def test_get_encodes_traversal_id_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(url__startswith="https://api.intra.42.fr/v2/").mock(
        return_value=httpx.Response(404, json={"error": "Not Found"})
    )

    client = AsyncClient("id", "secret")
    try:
        with pytest.raises(NotFoundError):
            await client.users.get("../campus/1")
    finally:
        await client.aclose()

    assert route.calls.last.request.url.raw_path == b"/v2/users/..%2Fcampus%2F1"


def test_get_encodes_traversal_id_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(url__startswith="https://api.intra.42.fr/v2/").mock(
        return_value=httpx.Response(404, json={"error": "Not Found"})
    )

    with Client("id", "secret") as client:
        with pytest.raises(NotFoundError):
            client.users.get("jdoe?filter[x]=1")

    assert route.calls.last.request.url.raw_path == b"/v2/users/jdoe%3Ffilter%5Bx%5D%3D1"


def test_get_plain_login_unchanged(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users/jdoe").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "jdoe"})
    )

    with Client("id", "secret") as client:
        assert client.users.get("jdoe").login == "jdoe"

    assert route.called


@pytest.mark.parametrize("bad", ["", ".", ".."])
def test_get_rejects_dot_and_empty_ids_without_request(mock_token_route, bad: str) -> None:
    mock, token_route = mock_token_route
    route = mock.get(url__startswith="https://api.intra.42.fr/v2/")

    with Client("id", "secret") as client:
        with pytest.raises(ValueError, match="Invalid path segment"):
            client.users.get(bad)

    assert not route.called
    assert not token_route.called


def test_graph_encodes_field_and_interval(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(url__startswith="https://api.intra.42.fr/v2/").mock(
        return_value=httpx.Response(200, json={})
    )

    with Client("id", "secret") as client:
        client.locations.graph(field="begin_at/../x", interval="day")

    expected = b"/v2/locations/graph/on/begin_at%2F..%2Fx/by/day"
    assert route.calls.last.request.url.raw_path == expected
