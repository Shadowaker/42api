"""Tests for the object-oriented nested-access style: campus.events,
user.campus_users, etc. — properties on a fetched model instance that
transparently issue a scoped, lazily-paginating nested request.
"""

import httpx
import pytest

from intra42._async.client import AsyncClient
from intra42._sync.client import Client
from intra42.models.user import User


async def test_user_events_hits_nested_endpoint_async(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/42").mock(
        return_value=httpx.Response(200, json={"id": 42, "login": "jdoe"})
    )
    mock.get("https://api.intra.42.fr/v2/users/42/events").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "name": "Rush"}])
    )

    client = AsyncClient("id", "secret")
    try:
        user = await client.users.get(42)
        events = await user.events.all()
    finally:
        await client.aclose()

    assert [e.id for e in events] == [1]
    assert events[0].name == "Rush"


def test_user_events_hits_nested_endpoint_sync(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/42").mock(
        return_value=httpx.Response(200, json={"id": 42, "login": "jdoe"})
    )
    mock.get("https://api.intra.42.fr/v2/users/42/events").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "name": "Rush"}])
    )

    with Client("id", "secret") as client:
        user = client.users.get(42)
        events = user.events.all()

    assert [e.id for e in events] == [1]


async def test_user_campus_users_hits_nested_endpoint(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users/42").mock(
        return_value=httpx.Response(200, json={"id": 42})
    )
    mock.get("https://api.intra.42.fr/v2/users/42/campus_users").mock(
        return_value=httpx.Response(
            200, json=[{"id": 1, "user_id": 42, "campus_id": 1, "is_primary": True}]
        )
    )

    client = AsyncClient("id", "secret")
    try:
        user = await client.users.get(42)
        campus_users = await user.campus_users.all()
    finally:
        await client.aclose()

    assert campus_users[0].campus_id == 1


async def test_campus_users_and_events_hit_nested_endpoints(mock_token_route) -> None:
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/campus/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Paris"})
    )
    mock.get("https://api.intra.42.fr/v2/campus/1/users").mock(
        return_value=httpx.Response(200, json=[{"id": 42, "login": "jdoe"}])
    )
    mock.get("https://api.intra.42.fr/v2/campus/1/events").mock(
        return_value=httpx.Response(200, json=[{"id": 7, "name": "Meetup"}])
    )

    client = AsyncClient("id", "secret")
    try:
        campus = await client.campuses.get(1)
        users = await campus.users.all()
        events = await campus.events.all()
    finally:
        await client.aclose()

    assert users[0].login == "jdoe"
    assert events[0].name == "Meetup"


async def test_relation_composes_through_list_iteration(mock_token_route) -> None:
    """Relations must also be bound on instances from queryset iteration,
    not just `.get()` — e.g. `for u in client.users: u.events` should work."""
    mock, _ = mock_token_route
    mock.get("https://api.intra.42.fr/v2/users").mock(
        return_value=httpx.Response(200, json=[{"id": 1}, {"id": 2}])
    )
    mock.get("https://api.intra.42.fr/v2/users/1/events").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = AsyncClient("id", "secret")
    try:
        users = await client.users.all()
        events = await users[0].events.all()
    finally:
        await client.aclose()

    assert events == []


def test_manually_constructed_instance_raises_clear_error() -> None:
    user = User.model_validate({"id": 1})

    with pytest.raises(RuntimeError, match="fetched via Client/AsyncClient"):
        _ = user.events
