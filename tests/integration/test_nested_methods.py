"""Typed resource-level nested accessors: client.users.events(user), etc."""

from __future__ import annotations

import httpx
import pytest

from intra42._async.client import AsyncClient
from intra42._sync.client import Client
from intra42.models.campus import Campus
from intra42.models.user import User

BASE = "https://api.intra.42.fr/v2"

# (resource attribute, method name, nested path for parent id 7)
RELATIONS = [
    ("users", "events", "/users/7/events"),
    ("users", "campus_users", "/users/7/campus_users"),
    ("users", "locations", "/users/7/locations"),
    ("users", "projects_users", "/users/7/projects_users"),
    ("campuses", "users", "/campus/7/users"),
    ("campuses", "events", "/campus/7/events"),
    ("campuses", "locations", "/campus/7/locations"),
    ("cursus", "users", "/cursus/7/users"),
    ("cursus", "events", "/cursus/7/events"),
    ("cursus", "projects", "/cursus/7/projects"),
    ("accreditations", "users", "/accreditations/7/users"),
    ("projects", "projects_users", "/projects/7/projects_users"),
]


@pytest.mark.parametrize(("resource", "method", "path"), RELATIONS)
def test_nested_method_hits_scoped_endpoint_sync(
    mock_token_route, resource: str, method: str, path: str
) -> None:
    mock, _ = mock_token_route
    route = mock.get(f"{BASE}{path}").mock(return_value=httpx.Response(200, json=[{"id": 1}]))

    with Client("id", "secret") as client:
        items = getattr(getattr(client, resource), method)(7).all()

    assert [i.id for i in items] == [1]
    assert route.called


@pytest.mark.parametrize(("resource", "method", "path"), RELATIONS)
async def test_nested_method_hits_scoped_endpoint_async(
    mock_token_route, resource: str, method: str, path: str
) -> None:
    mock, _ = mock_token_route
    route = mock.get(f"{BASE}{path}").mock(return_value=httpx.Response(200, json=[{"id": 1}]))

    client = AsyncClient("id", "secret")
    try:
        items = await getattr(getattr(client, resource), method)(7).all()
    finally:
        await client.aclose()

    assert [i.id for i in items] == [1]
    assert route.called


def test_nested_method_accepts_login_without_fetching_user(mock_token_route) -> None:
    mock, _ = mock_token_route
    user_route = mock.get(f"{BASE}/users/jdoe")
    events = mock.get(f"{BASE}/users/jdoe/events").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "name": "Rush"}])
    )

    with Client("id", "secret") as client:
        result = client.users.events("jdoe").all()

    assert result[0].name == "Rush"
    assert events.called
    assert not user_route.called  # no extra request to fetch the parent


def test_nested_method_accepts_manually_constructed_instance(mock_token_route) -> None:
    """Unlike the model property, the method doesn't need a client-bound instance."""
    mock, _ = mock_token_route
    route = mock.get(f"{BASE}/campus/3/users").mock(return_value=httpx.Response(200, json=[]))

    with Client("id", "secret") as client:
        client.campuses.users(Campus.model_validate({"id": 3, "name": "X"})).all()

    assert route.called


def test_nested_method_encodes_parent_id(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(url__startswith=f"{BASE}/").mock(return_value=httpx.Response(200, json=[]))

    with Client("id", "secret") as client:
        client.users.events("../campus/1").all()

    raw_path = route.calls.last.request.url.raw_path.split(b"?", 1)[0]
    assert raw_path == b"/v2/users/..%2Fcampus%2F1/events"


def test_nested_method_supports_query_chaining(mock_token_route) -> None:
    mock, _ = mock_token_route
    route = mock.get(f"{BASE}/users/7/events").mock(return_value=httpx.Response(200, json=[]))

    with Client("id", "secret") as client:
        client.users.events(User.model_validate({"id": 7})).filter(kind="rush").sort("-id").all()

    params = route.calls.last.request.url.params
    assert params["filter[kind]"] == "rush"
    assert params["sort"] == "-id"
