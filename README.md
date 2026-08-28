# 42api

An object-oriented Python client for the [42 School API](https://api.intra.42.fr)
(`api.intra.42.fr`) that handles OAuth2 authentication, request pacing, and
pagination for you, so you can work with typed resources instead of raw JSON
and HTTP plumbing.

- **Sync and async** — `Client` and `AsyncClient` share one codebase and the
  same interface.
- **Typed models** — resources are [Pydantic v2](https://docs.pydantic.dev/)
  models with IDE-friendly autocomplete.
- **Automatic rate limiting** — requests are paced to stay under 42's limits;
  `429`s are retried with backoff automatically.
- **Lazy pagination** — iterate a query and it walks every page for you.

## Install

```bash
uv add 42api
# or: pip install 42api
```

## Usage

```python
from intra42 import Client

with Client(client_id="...", client_secret="...") as client:
    user = client.users.get("jdoe")
    print(user.login, user.email)

    for user in client.users.filter(campus_id=1).sort("-level"):
        print(user.login)
```

Async is the same shape:

```python
import asyncio
from intra42 import AsyncClient


async def main() -> None:
    async with AsyncClient(client_id="...", client_secret="...") as client:
        user = await client.users.get("jdoe")
        async for user in client.users.filter(campus_id=1).sort("-level"):
            print(user.login)


asyncio.run(main())
```

Get your `client_id`/`client_secret` by registering an app at
https://profile.intra.42.fr/oauth/applications. This library uses the
**client credentials** flow, so it accesses the API as your app rather than
as a specific logged-in user.

## Errors

All errors subclass `intra42.FortyTwoAPIError`, with subclasses for common
HTTP statuses: `AuthenticationError` (401), `PermissionDeniedError` (403),
`NotFoundError` (404), `ValidationError` (422), `RateLimitError` (429, only
raised once the built-in retry budget is exhausted), `ServerError` (5xx),
and `NetworkError` (connection/timeout failures).

## Development

Uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync                                               # install dependencies
uv run pytest                                         # run tests
uv run ruff check . && uv run ruff format --check .   # lint
uv run mypy                                           # type check
```

The sync client (`intra42._sync`) is generated from the async client
(`intra42._async`) via [`unasync`](https://github.com/python-trio/unasync) —
edit the async source and regenerate:

```bash
uv run python scripts/unasync_generate.py            # regenerate
uv run python scripts/unasync_generate.py --check    # verify no drift (CI)
```

## License

MIT
