import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

EXAM_JSON = {
    "id": 42,
    "ip_range": "10.11.0.0/16,10.12.0.0/16,10.13.0.0/16,10.42.0.0/16",
    "begin_at": "2015-07-17T15:00:00.000Z",
    "end_at": "2015-07-17T19:00:00.000Z",
    "location": "e1,e2,e3",
    "max_people": 780,
    "nbr_subscribers": 594,
    "name": "Piscine C - Exam 01",
    "created_at": "2015-07-15T13:05:26.006Z",
    "updated_at": "2018-08-27T16:56:15.032Z",
    "campus": {
        "id": 1,
        "name": "Paris",
        "time_zone": "Europe/Paris",
        "language": {"id": 1, "name": "Français", "identifier": "fr"},
        "users_count": 22319,
        "vogsphere_id": 1,
        "active": True,
    },
    "cursus": [
        {
            "id": 4,
            "created_at": "2015-05-01T17:46:08.433Z",
            "name": "Piscine C",
            "slug": "piscine-c",
        }
    ],
    "projects": [
        {
            "id": 405,
            "name": "Exam01",
            "slug": "piscine-c-exam01",
            "parent": None,
            "children": [],
            "attachments": [],
            "created_at": "2015-06-29T13:14:31.702Z",
            "updated_at": "2021-09-01T08:35:01.074Z",
            "exam": True,
            "git_id": None,
            "repository": None,
        }
    ],
}


async def test_get_exam_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/exams/42").mock(
        return_value=httpx.Response(200, json=EXAM_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        exam = await client.exams.get(42)
    finally:
        await client.aclose()

    assert exam.id == 42
    assert exam.name == "Piscine C - Exam 01"
    assert exam.max_people == 780
    assert exam.campus is not None
    assert exam.campus.name == "Paris"
    assert exam.cursus is not None
    assert exam.cursus[0].slug == "piscine-c"
    assert exam.projects is not None
    assert exam.projects[0].name == "Exam01"


def test_get_exam_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/exams/42").mock(
        return_value=httpx.Response(200, json=EXAM_JSON)
    )

    with Client("id", "secret") as client:
        exam = client.exams.get(42)

    assert exam.id == 42


async def test_filter_exams_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/exams").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.exams.filter(campus_id=1).sort("-begin_at").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[campus_id]"] == "1"
    assert request.url.params["sort"] == "-begin_at"


async def test_graph_bare(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/exams/graph").mock(
        return_value=httpx.Response(200, json={"2017-11": 2})
    )

    client = AsyncClient("id", "secret")
    try:
        counts = await client.exams.graph()
    finally:
        await client.aclose()

    assert counts == {"2017-11": 2}


async def test_graph_with_field_and_interval(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/exams/graph/on/created_at/by/day").mock(
        return_value=httpx.Response(200, json={"2017-11-22": 2})
    )

    client = AsyncClient("id", "secret")
    try:
        counts = await client.exams.graph(field="created_at", interval="day")
    finally:
        await client.aclose()

    assert counts == {"2017-11-22": 2}
    assert route.called


async def test_graph_interval_without_field_defaults_field(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/exams/graph/on/created_at/by/week").mock(
        return_value=httpx.Response(200, json={})
    )

    client = AsyncClient("id", "secret")
    try:
        await client.exams.graph(interval="week")
    finally:
        await client.aclose()

    assert route.called


def test_graph_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/exams/graph/on/end_at").mock(
        return_value=httpx.Response(200, json={"2017-11-19": 1})
    )

    with Client("id", "secret") as client:
        counts = client.exams.graph(field="end_at")

    assert counts == {"2017-11-19": 1}
