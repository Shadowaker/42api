"""Exception hierarchy for the intra42 client."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


class FortyTwoAPIError(Exception):
    """Base class for all errors raised by this library."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code!r}, message={self.message!r})"


class AuthenticationError(FortyTwoAPIError):
    """Raised on any 401"""


class PermissionDeniedError(FortyTwoAPIError):
    """Raised on any 403"""


class NotFoundError(FortyTwoAPIError):
    """Raised on any 404."""


class ValidationError(FortyTwoAPIError):
    """Raised on any 422"""


class RateLimitError(FortyTwoAPIError):
    """Raised on any 429 after the built-in retry/backoff budget is exhausted."""


class ServerError(FortyTwoAPIError):
    """Raised on any 5xx"""


class NetworkError(FortyTwoAPIError):
    """Wraps a transport-level failure (DNS, connect, timeout) from httpx."""


_STATUS_MAP: dict[int, type[FortyTwoAPIError]] = {
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
}


def raise_for_status(response: httpx.Response) -> None:
    """Raise the mapped :class:`FortyTwoAPIError` subclass for a non-2xx response.

    Does nothing for successful responses.
    """
    if response.is_success:
        return

    status = response.status_code
    try:
        payload = response.json()
        detail = payload.get("error_description") or payload.get("message") or payload.get("error")
    except Exception:
        detail = None
    message = detail or f"Request failed with status {status}"

    if status >= 500:
        error_cls: type[FortyTwoAPIError] = ServerError
    else:
        error_cls = _STATUS_MAP.get(status, FortyTwoAPIError)

    raise error_cls(message, status_code=status, response=response)
