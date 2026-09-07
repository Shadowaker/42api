import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client


async def test_get_campus_user_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/campus_users/126").mock(
        return_value=httpx.Response(
            200, json={"id": 126, "user_id": 126, "campus_id": 1, "is_primary": True}
        )
    )

    client = AsyncClient("id", "secret")
    try:
        campus_user = await client.campus_users.get(126)
    finally:
        await client.aclose()

    assert campus_user.id == 126
    assert campus_user.user_id == 126
    assert campus_user.campus_id == 1
    assert campus_user.is_primary is True


def test_get_campus_user_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/campus_users/126").mock(
        return_value=httpx.Response(
            200, json={"id": 126, "user_id": 126, "campus_id": 1, "is_primary": True}
        )
    )

    with Client("id", "secret") as client:
        campus_user = client.campus_users.get(126)

    assert campus_user.id == 126
    assert campus_user.is_primary is True


async def test_list_campus_users_filtered_by_user(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/campus_users").mock(
        return_value=httpx.Response(
            200, json=[{"id": 126, "user_id": 126, "campus_id": 1, "is_primary": True}]
        )
    )

    client = AsyncClient("id", "secret")
    try:
        results = await client.campus_users.filter(user_id=126).all()
    finally:
        await client.aclose()

    assert [cu.id for cu in results] == [126]
    assert route.calls.last.request.url.params["filter[user_id]"] == "126"
