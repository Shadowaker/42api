"""Integration tests for the auto-paginating query builder against respx."""

import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

PAGE_1 = httpx.Response(
    200,
    json=[{"id": 1, "login": "a"}, {"id": 2, "login": "b"}],
    headers={"Link": '<https://api.intra.42.fr/v2/users?page=2>; rel="next"'},
)
PAGE_2 = httpx.Response(200, json=[{"id": 3, "login": "c"}])


async def test_all_walks_every_page_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users").mock(side_effect=[PAGE_1, PAGE_2])

    client = AsyncClient("id", "secret")
    try:
        users = await client.users.all()
    finally:
        await client.aclose()

    assert [u.id for u in users] == [1, 2, 3]
    assert route.call_count == 2


async def test_async_for_walks_every_page(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users").mock(side_effect=[PAGE_1, PAGE_2])

    client = AsyncClient("id", "secret")
    try:
        seen = []
        async for user in client.users:
            seen.append(user.id)
    finally:
        await client.aclose()

    assert seen == [1, 2, 3]
    assert route.call_count == 2


async def test_filter_and_sort_are_sent_as_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.users.filter(campus_id=1).sort("-level").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[campus_id]"] == "1"
    assert request.url.params["sort"] == "-level"


def test_all_walks_every_page_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users").mock(side_effect=[PAGE_1, PAGE_2])

    with Client("id", "secret") as client:
        users = client.users.all()

    assert [u.id for u in users] == [1, 2, 3]
    assert route.call_count == 2


def test_for_loop_walks_every_page_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/users").mock(side_effect=[PAGE_1, PAGE_2])

    with Client("id", "secret") as client:
        seen = [user.id for user in client.users]

    assert seen == [1, 2, 3]
    assert route.call_count == 2
