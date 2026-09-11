import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

PROJECT_JSON = {
    "id": 2,
    "name": "Ordinary Wizarding Levels",
    "slug": "ordinary-wizarding-levels",
    "difficulty": 5000,
    "description": "OWL exam.",
    "parent": None,
    "children": [],
    "objectives": ["Wizarding"],
    "attachments": [],
    "created_at": "2017-11-22T13:41:26.356Z",
    "updated_at": "2017-11-22T13:41:26.441Z",
    "exam": True,
    "cursus": [
        {
            "id": 1,
            "created_at": "2017-11-22T13:41:00.750Z",
            "name": "Piscine C",
            "slug": "piscine-c",
        }
    ],
    "campus": [{"id": 1, "name": "Cluj", "time_zone": "Europe/Bucharest"}],
    "skills": [{"id": 6, "name": "Basics", "created_at": "2017-11-22T13:41:00.448Z"}],
    "videos": [],
    "tags": [{"id": 13, "name": "Ordinary Wizarding Levels", "kind": "general"}],
    "project_sessions": [
        {
            "id": 2,
            "solo": True,
            "difficulty": 5000,
            "project_id": 2,
            "is_subscriptable": True,
            "scales": [{"id": 2, "correction_number": 3, "is_primary": True}],
            "uploads": [],
            "team_behaviour": "user",
        }
    ],
}


async def test_get_project_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects/2").mock(
        return_value=httpx.Response(200, json=PROJECT_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        project = await client.projects.get(2)
    finally:
        await client.aclose()

    assert project.id == 2
    assert project.name == "Ordinary Wizarding Levels"
    assert project.exam is True
    assert project.cursus is not None
    assert project.cursus[0].name == "Piscine C"
    assert project.campus is not None
    assert project.campus[0].name == "Cluj"
    assert project.tags is not None
    assert project.tags[0].kind == "general"
    assert project.project_sessions is not None
    assert project.project_sessions[0].scales[0].is_primary is True


def test_get_project_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects/2").mock(
        return_value=httpx.Response(200, json=PROJECT_JSON)
    )

    with Client("id", "secret") as client:
        project = client.projects.get(2)

    assert project.id == 2


async def test_project_session_estimate_time_accepts_string_or_int(mock_token_route) -> None:
    """Confirmed against a real account: estimate_time is sometimes a
    free-form duration string ("1 day") rather than an int of seconds, as
    the apidoc's own example (2592000) suggested."""
    payload = dict(
        PROJECT_JSON,
        id=9,
        project_sessions=[
            {"id": 9, "estimate_time": "1 day"},
            {"id": 10, "estimate_time": 2592000},
        ],
    )
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects/9").mock(
        return_value=httpx.Response(200, json=payload)
    )

    client = AsyncClient("id", "secret")
    try:
        project = await client.projects.get(9)
    finally:
        await client.aclose()

    assert project.project_sessions is not None
    assert project.project_sessions[0].estimate_time == "1 day"
    assert project.project_sessions[1].estimate_time == 2592000


async def test_project_with_parent_and_children(mock_token_route) -> None:
    payload = dict(
        PROJECT_JSON,
        id=4,
        parent=None,
        children=[
            {
                "name": "Quarter Finals",
                "id": 5,
                "slug": "hogwarts-quidditch-cup-quarter-finals",
                "url": "https://projects.intra.42.fr/hogwarts-quidditch-cup-quarter-finals/mine",
            }
        ],
    )
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects/4").mock(
        return_value=httpx.Response(200, json=payload)
    )

    client = AsyncClient("id", "secret")
    try:
        project = await client.projects.get(4)
    finally:
        await client.aclose()

    assert project.parent is None
    assert project.children is not None
    assert project.children[0].name == "Quarter Finals"


async def test_filter_projects_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/projects").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.projects.filter(exam=True).sort("-difficulty").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[exam]"] == "true"
    assert request.url.params["sort"] == "-difficulty"


async def test_project_nested_projects_users(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects/2").mock(
        return_value=httpx.Response(200, json=PROJECT_JSON)
    )
    mock.get("https://api.intra.42.fr/v2/projects/2/projects_users").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "status": "in_progress"}])
    )

    client = AsyncClient("id", "secret")
    try:
        project = await client.projects.get(2)
        projects_users = await project.projects_users.all()
    finally:
        await client.aclose()

    assert projects_users[0].status == "in_progress"


async def test_cursus_nested_projects(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/cursus/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "42"})
    )
    mock.get("https://api.intra.42.fr/v2/cursus/1/projects").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "name": "Libft"}])
    )

    client = AsyncClient("id", "secret")
    try:
        cursus = await client.cursus.get(1)
        projects = await cursus.projects.all()
    finally:
        await client.aclose()

    assert projects[0].name == "Libft"
