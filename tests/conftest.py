import httpx
import pytest
import respx

from intra42._auth import TOKEN_URL

DEFAULT_TOKEN_PAYLOAD = {"access_token": "test-token", "expires_in": 7200}


@pytest.fixture
def mock_token_route():
    """Mock the OAuth token endpoint with respx.

    Yields the respx route so tests can assert call counts or override the
    response (``route.side_effect = ...``).
    """
    with respx.mock(assert_all_called=False) as mock:
        route = mock.post(TOKEN_URL).mock(
            return_value=httpx.Response(200, json=DEFAULT_TOKEN_PAYLOAD)
        )
        yield mock, route
