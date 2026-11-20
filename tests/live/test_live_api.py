"""Tests against the real api.intra.42.fr (see conftest.py for credentials)."""

from __future__ import annotations

import pytest

from intra42 import AsyncClient, Client
from intra42.exceptions import AuthenticationError, NotFoundError


async def test_live_get_campus(credentials: tuple[str, str]) -> None:
    async with AsyncClient(*credentials) as client:
        campus = await client.campuses.get(1)
    assert campus.id == 1


async def test_live_pagination_follows_same_origin_link(credentials: tuple[str, str]) -> None:
    """Crossing a page boundary follows the real absolute ``Link`` URL,
    which must pass the base_url origin check."""
    ids: list[int] = []
    async with AsyncClient(*credentials) as client:
        async for campus in client.campuses.page_size(2):
            ids.append(campus.id)
            if len(ids) == 3:
                break
    assert len(set(ids)) == 3


async def test_live_401_refreshes_token_async(credentials: tuple[str, str]) -> None:
    async with AsyncClient(*credentials) as client:
        await client.campuses.get(1)  # obtain a real token
        # Simulate a server-side revocation: the cache still thinks the
        # token is valid, but the API will reject it with a real 401.
        client._token_manager._access_token = "revoked-token"

        campus = await client.campuses.get(1)

        assert campus.id == 1
        assert client._token_manager._access_token not in (None, "revoked-token")


def test_live_401_refreshes_token_sync(credentials: tuple[str, str]) -> None:
    with Client(*credentials) as client:
        client.campuses.get(1)
        client._token_manager._access_token = "revoked-token"

        campus = client.campuses.get(1)

        assert campus.id == 1
        assert client._token_manager._access_token not in (None, "revoked-token")


def test_live_traversal_id_does_not_escape_resource(credentials: tuple[str, str]) -> None:
    """Unencoded, this would resolve to GET /campus/1 and return a campus."""
    with Client(*credentials) as client:
        with pytest.raises(NotFoundError):
            client.users.get("../campus/1")


def test_live_bad_credentials_raise_authentication_error(credentials: tuple[str, str]) -> None:
    with Client("not-a-real-uid", "not-a-real-secret") as client:
        with pytest.raises(AuthenticationError):
            client.campuses.get(1)
