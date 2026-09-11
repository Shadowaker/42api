import httpx

from intra42._async.client import AsyncClient
from intra42._sync.client import Client

PROJECT_USER_JSON = {
    "id": 18,
    "occurrence": 0,
    "final_mark": None,
    "status": "waiting_for_correction",
    "validated?": None,
    "current_team_id": 18,
    "project": {"id": 1, "name": "Libft", "slug": "libft", "parent_id": None},
    "cursus_ids": [1],
    "user": {"id": 25, "login": "bhutt", "url": "https://api.intra.42.fr/v2/users/bhutt"},
    "teams": [
        {
            "id": 18,
            "name": "bhutt's group",
            "url": "https://api.intra.42.fr/v2/teams/18",
            "final_mark": None,
            "project_id": 1,
            "status": "waiting_for_correction",
            "users": [
                {
                    "id": 25,
                    "login": "bhutt",
                    "url": "https://api.intra.42.fr/v2/users/bhutt",
                    "leader": True,
                    "occurrence": 0,
                    "validated": True,
                    "projects_user_id": 18,
                }
            ],
            "locked?": True,
            "validated?": None,
            "closed?": True,
            "repo_url": None,
            "repo_uuid": "intra-uuid-0d4153cd-18",
            "project_session_id": 1,
        }
    ],
}


async def test_get_projects_user_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects_users/18").mock(
        return_value=httpx.Response(200, json=PROJECT_USER_JSON)
    )

    client = AsyncClient("id", "secret")
    try:
        pu = await client.projects_users.get(18)
    finally:
        await client.aclose()

    assert pu.id == 18
    assert pu.status == "waiting_for_correction"
    assert pu.validated is None
    assert pu.project is not None
    assert pu.project.name == "Libft"
    assert pu.user is not None
    assert pu.user.login == "bhutt"
    assert pu.teams is not None
    team = pu.teams[0]
    assert team.locked is True
    assert team.closed is True
    assert team.users is not None
    assert team.users[0].leader is True


def test_get_projects_user_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects_users/18").mock(
        return_value=httpx.Response(200, json=PROJECT_USER_JSON)
    )

    with Client("id", "secret") as client:
        pu = client.projects_users.get(18)

    assert pu.id == 18


async def test_filter_projects_users_sends_query_params(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/projects_users").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        await client.projects_users.filter(status="finished").sort("-created_at").all()
    finally:
        await client.aclose()

    request = route.calls.last.request
    assert request.url.params["filter[status]"] == "finished"
    assert request.url.params["sort"] == "-created_at"


async def test_graph_bare(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects_users/graph").mock(
        return_value=httpx.Response(200, json={"2017-11": 68})
    )

    client = AsyncClient("id", "secret")
    try:
        counts = await client.projects_users.graph()
    finally:
        await client.aclose()

    assert counts == {"2017-11": 68}


async def test_graph_with_field_and_interval(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/projects_users/graph/on/created_at/by/day").mock(
        return_value=httpx.Response(200, json={"2017-11-22": 68})
    )

    client = AsyncClient("id", "secret")
    try:
        counts = await client.projects_users.graph(field="created_at", interval="day")
    finally:
        await client.aclose()

    assert counts == {"2017-11-22": 68}
    assert route.called


async def test_graph_interval_without_field_defaults_field(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get("https://api.intra.42.fr/v2/projects_users/graph/on/created_at/by/week").mock(
        return_value=httpx.Response(200, json={})
    )

    client = AsyncClient("id", "secret")
    try:
        await client.projects_users.graph(interval="week")
    finally:
        await client.aclose()

    assert route.called


def test_graph_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/projects_users/graph/on/updated_at").mock(
        return_value=httpx.Response(200, json={"2017-11-19": 2})
    )

    with Client("id", "secret") as client:
        counts = client.projects_users.graph(field="updated_at")

    assert counts == {"2017-11-19": 2}


async def test_user_nested_projects_users(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/25").mock(
        return_value=httpx.Response(200, json={"id": 25, "login": "bhutt"})
    )
    mock.get("https://api.intra.42.fr/v2/users/25/projects_users").mock(
        return_value=httpx.Response(200, json=[PROJECT_USER_JSON])
    )

    client = AsyncClient("id", "secret")
    try:
        user = await client.users.get(25)
        pus = await user.projects_users.all()
    finally:
        await client.aclose()

    assert pus[0].id == 18
