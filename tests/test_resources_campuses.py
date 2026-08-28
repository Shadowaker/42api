import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client


async def test_get_campus_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/campuses/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Paris"})
    )

    client = AsyncClient("id", "secret")
    try:
        campus = await client.campuses.get(1)
    finally:
        await client.aclose()

    assert campus.id == 1
    assert campus.name == "Paris"


def test_get_campus_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/campuses/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Paris"})
    )

    with Client("id", "secret") as client:
        campus = client.campuses.get(1)

    assert campus.id == 1
    assert campus.name == "Paris"
