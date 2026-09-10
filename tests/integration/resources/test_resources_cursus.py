import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

CURSUS_JSON = {
    "id": 2,
    "created_at": "2017-11-22T13:41:00.825Z",
    "name": "42",
    "slug": "42",
}


async def test_get_cursus_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/cursus/2").mock(
        return_value=httpx.Response(200, json=CURSUS_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        cursus = await client.cursus.get(2)
    finally:
        await client.aclose()

    assert cursus.id == 2
    assert cursus.name == "42"
    assert cursus.slug == "42"


def test_get_cursus_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/cursus/2").mock(
        return_value=httpx.Response(200, json=CURSUS_JSON)
    )

    with Client("id", "secret") as client:
        cursus = client.cursus.get(2)

    assert cursus.id == 2


async def test_filter_cursus_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/cursus").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.cursus.filter(kind="main").sort("-name").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[kind]"] == "main"
    assert request.url.params["sort"] == "-name"


async def test_cursus_nested_users_and_events(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/cursus/2").mock(
        return_value=httpx.Response(200, json=CURSUS_JSON)
    )
    mock.get("https://api.intra.42.fr/v2/cursus/2/users").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "login": "jdoe"}])
    )
    mock.get("https://api.intra.42.fr/v2/cursus/2/events").mock(
        return_value=httpx.Response(200, json=[{"id": 9, "name": "Hackathon"}])
    )

    client = AsyncClient("id", "secret")
    try:
        cursus = await client.cursus.get(2)
        users = await cursus.users.all()
        events = await cursus.events.all()
    finally:
        await client.aclose()

    assert users[0].login == "jdoe"
    assert events[0].name == "Hackathon"
