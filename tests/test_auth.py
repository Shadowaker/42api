import httpx
import pytest

from intra42._auth import TOKEN_URL, TokenManager
from intra42.exceptions import AuthenticationError


def test_ensure_token_sync_fetches_and_caches(mock_token_route) -> None:
    _, route = mock_token_route
    manager = TokenManager("id", "secret")
    with httpx.Client() as http:
        token1 = manager.ensure_token(http)
        token2 = manager.ensure_token(http)

    assert token1 == "test-token"
    assert token2 == "test-token"
    assert route.call_count == 1


async def test_ensure_token_async_fetches_and_caches(mock_token_route) -> None:
    _, route = mock_token_route
    manager = TokenManager("id", "secret")
    async with httpx.AsyncClient() as http:
        token1 = await manager.aensure_token(http)
        token2 = await manager.aensure_token(http)

    assert token1 == "test-token"
    assert token2 == "test-token"
    assert route.call_count == 1


def test_ensure_token_refreshes_after_expiry(mock_token_route, monkeypatch) -> None:
    import intra42._auth as auth_module

    _, route = mock_token_route
    manager = TokenManager("id", "secret", leeway=0.0)

    now = [1000.0]
    monkeypatch.setattr(auth_module.time, "time", lambda: now[0])

    with httpx.Client() as http:
        manager.ensure_token(http)
        now[0] += 7300  # past the mocked expires_in=7200
        manager.ensure_token(http)

    assert route.call_count == 2


def test_ensure_token_raises_authentication_error_on_401() -> None:
    import respx

    with respx.mock(assert_all_called=False) as mock:
        mock.post(TOKEN_URL).mock(
            return_value=httpx.Response(401, json={"error": "invalid_client"})
        )
        manager = TokenManager("bad-id", "bad-secret")
        with httpx.Client() as http, pytest.raises(AuthenticationError):
            manager.ensure_token(http)
