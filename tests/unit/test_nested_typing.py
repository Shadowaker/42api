"""Static-typing check: nested resource methods return exactly-typed querysets.

Runs mypy on a small snippet, since a runtime test can't catch a
regression back to the ``AsyncQuerySet[X] | QuerySet[X]`` union.
"""

from __future__ import annotations

from pathlib import Path

import pytest

mypy_api = pytest.importorskip("mypy.api")

SNIPPET = """
from intra42 import AsyncClient, Client

def sync_usage(client: Client) -> None:
    reveal_type(client.users.events("jdoe"))
    reveal_type(client.campuses.users(1))
    for event in client.users.events(1):
        reveal_type(event)

async def async_usage(client: AsyncClient) -> None:
    reveal_type(client.users.projects_users(1))
    async for user in client.cursus.users(21):
        reveal_type(user)
"""

EXPECTED = [
    "intra42._sync.query.QuerySet[intra42.models.event.Event]",
    "intra42._sync.query.QuerySet[intra42.models.user.User]",
    "intra42.models.event.Event",
    "intra42._async.query.AsyncQuerySet[intra42.models.project_user.ProjectUser]",
    "intra42.models.user.User",
]


def test_nested_methods_are_exactly_typed(tmp_path: Path) -> None:
    snippet = tmp_path / "snippet.py"
    snippet.write_text(SNIPPET)
    # An empty config keeps the repo's [tool.mypy] (packages=..., strict
    # flags) from applying to this throwaway snippet.
    config = tmp_path / "mypy.ini"
    config.write_text("[mypy]\n")

    stdout, stderr, _ = mypy_api.run(
        [str(snippet), "--config-file", str(config), "--no-incremental", "--python-version", "3.11"]
    )

    revealed = [
        line.split('Revealed type is "', 1)[1].rstrip('"')
        for line in stdout.splitlines()
        if "Revealed type is" in line
    ]
    errors = [line for line in stdout.splitlines() if ": error:" in line]

    assert not errors, stdout + stderr
    assert revealed == EXPECTED, stdout
