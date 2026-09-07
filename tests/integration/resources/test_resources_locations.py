import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

LOCATION_JSON = {
    "id": 4,
    "begin_at": "2017-11-19T13:42:09.511Z",
    "end_at": "2017-11-19T16:42:09.511Z",
    "primary": True,
    "floor": None,
    "row": None,
    "post": None,
    "host": "oberon",
    "campus_id": 1,
    "user": {"id": 59, "login": "davader", "url": "https://api.intra.42.fr/v2/users/davader"},
}


async def test_get_location_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/locations/4").mock(
        return_value=httpx.Response(200, json=LOCATION_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        location = await client.locations.get(4)
    finally:
        await client.aclose()

    assert location.id == 4
    assert location.host == "oberon"
    assert location.primary is True
    assert location.user is not None
    assert location.user.login == "davader"


def test_get_location_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/locations/4").mock(
        return_value=httpx.Response(200, json=LOCATION_JSON)
    )

    with Client("id", "secret") as client:
        location = client.locations.get(4)

    assert location.id == 4


async def test_filter_locations_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/locations").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.locations.filter(active=True).sort("-begin_at").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[active]"] == "true"
    assert request.url.params["sort"] == "-begin_at"


async def test_user_locations_nested_access(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/42").mock(
        return_value=httpx.Response(200, json={"id": 42})
    )
    mock.get("https://api.intra.42.fr/v2/users/42/locations").mock(
        return_value=httpx.Response(200, json=[LOCATION_JSON])
    )

    client = AsyncClient("id", "secret")
    try:
        user = await client.users.get(42)
        locations = await user.locations.all()
    finally:
        await client.aclose()

    assert locations[0].id == 4


async def test_campus_locations_nested_access(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/campus/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Paris"})
    )
    mock.get("https://api.intra.42.fr/v2/campus/1/locations").mock(
        return_value=httpx.Response(200, json=[LOCATION_JSON])
    )

    client = AsyncClient("id", "secret")
    try:
        campus = await client.campuses.get(1)
        locations = await campus.locations.all()
    finally:
        await client.aclose()

    assert locations[0].id == 4


async def test_graph_bare(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/locations/graph").mock(
        return_value=httpx.Response(200, json={"2017-11": 3})
    )

    client = AsyncClient("id", "secret")
    try:
        counts = await client.locations.graph()
    finally:
        await client.aclose()

    assert counts == {"2017-11": 3}


async def test_graph_with_field_and_interval(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/locations/graph/on/begin_at/by/day").mock(
        return_value=httpx.Response(200, json={"2017-11-13": 1})
    )

    client = AsyncClient("id", "secret")
    try:
        counts = await client.locations.graph(field="begin_at", interval="day")
    finally:
        await client.aclose()

    assert counts == {"2017-11-13": 1}
    assert route.called


async def test_graph_interval_without_field_defaults_field(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/locations/graph/on/begin_at/by/week").mock(
        return_value=httpx.Response(200, json={})
    )

    client = AsyncClient("id", "secret")
    try:
        await client.locations.graph(interval="week")
    finally:
        await client.aclose()

    assert route.called


def test_graph_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/locations/graph/on/end_at").mock(
        return_value=httpx.Response(200, json={"2017-11-19": 2})
    )

    with Client("id", "secret") as client:
        counts = client.locations.graph(field="end_at")

    assert counts == {"2017-11-19": 2}
