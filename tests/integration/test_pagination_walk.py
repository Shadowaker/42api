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
        await client.users.filter(primary_campus_id=1).sort("-pool_year").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[primary_campus_id]"] == "1"
    assert request.url.params["sort"] == "-pool_year"


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


async def test_next_link_missing_page_size_is_restored(mock_token_route) -> None:
    """Regression test, confirmed against the live API: 42's `next` link
    uses a bare `page=N` cursor — a different, incompatible pagination
    scheme from the bracketed `page[size]` this library sends, and the
    server returns 400 if both appear on the same request. Forwarding the
    link's query string as-is therefore either silently drops page_size
    (producing duplicate/missing rows) or, if merged naively, breaks the
    request outright. The fix extracts just the page number from the link
    and reissues it as `page[number]`, never forwarding the bare `page`
    key, alongside page_size/filter/sort/range re-applied on every page."""
    mock, _ = mock_token_route
    page_1 = httpx.Response(
        200,
        json=[{"id": 1}, {"id": 2}],
        headers={"Link": '<https://api.intra.42.fr/v2/users?page=2>; rel="next"'},
    )
    page_2 = httpx.Response(200, json=[{"id": 3}])
    route = mock.get("https://api.intra.42.fr/v2/users").mock(side_effect=[page_1, page_2])

    client = AsyncClient("id", "secret")
    try:
        users = await client.users.filter(primary_campus_id=1).page_size(2).all()
    finally:
        await client.aclose()

    assert [u.id for u in users] == [1, 2, 3]
    assert route.call_count == 2

    first_request, second_request = (call.request for call in route.calls)
    assert first_request.url.params["page[size]"] == "2"
    assert first_request.url.params["filter[primary_campus_id]"] == "1"
    # The fix: these must survive onto the second page too, even though the
    # `next` link's own query string didn't carry them.
    assert second_request.url.params["page[size]"] == "2"
    assert second_request.url.params["filter[primary_campus_id]"] == "1"
    # The link's cursor (bare `page=2`) must come through as `page[number]`,
    # not the bare key — mixing the two schemes is what causes the 400.
    assert second_request.url.params["page[number]"] == "2"
    assert "page" not in second_request.url.params


def test_next_link_missing_page_size_is_restored_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    page_1 = httpx.Response(
        200,
        json=[{"id": 1}, {"id": 2}],
        headers={"Link": '<https://api.intra.42.fr/v2/users?page=2>; rel="next"'},
    )
    page_2 = httpx.Response(200, json=[{"id": 3}])
    route = mock.get("https://api.intra.42.fr/v2/users").mock(side_effect=[page_1, page_2])

    with Client("id", "secret") as client:
        users = client.users.page_size(2).all()

    assert [u.id for u in users] == [1, 2, 3]
    second_request = route.calls[1].request
    assert second_request.url.params["page[size]"] == "2"
