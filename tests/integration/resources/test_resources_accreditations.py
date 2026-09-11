import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

ACCREDITATION_JSON = {
    "id": 2,
    "name": "Endor",
    "user_id": 71,
    "cursus_id": 2,
    "validated": False,
}


async def test_get_accreditation_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/accreditations/2").mock(
        return_value=httpx.Response(200, json=ACCREDITATION_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        accreditation = await client.accreditations.get(2)
    finally:
        await client.aclose()

    assert accreditation.id == 2
    assert accreditation.name == "Endor"
    assert accreditation.user_id == 71
    assert accreditation.validated is False


def test_get_accreditation_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/accreditations/2").mock(
        return_value=httpx.Response(200, json=ACCREDITATION_JSON)
    )

    with Client("id", "secret") as client:
        accreditation = client.accreditations.get(2)

    assert accreditation.id == 2


async def test_filter_accreditations_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/accreditations").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.accreditations.filter(validated=False).sort("-created_at").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[validated]"] == "false"
    assert request.url.params["sort"] == "-created_at"


async def test_accreditation_nested_users(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/accreditations/2").mock(
        return_value=httpx.Response(200, json=ACCREDITATION_JSON)
    )
    mock.get("https://api.intra.42.fr/v2/accreditations/2/users").mock(
        return_value=httpx.Response(200, json=[{"id": 71, "login": "obkenobi"}])
    )

    client = AsyncClient("id", "secret")
    try:
        accreditation = await client.accreditations.get(2)
        users = await accreditation.users.all()
    finally:
        await client.aclose()

    assert users[0].login == "obkenobi"
