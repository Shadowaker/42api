"""Fixtures for tests that hit the real 42 API.

Credentials come from ``INTRA42_UID`` / ``INTRA42_SECRET`` environment
variables, falling back to ``UID`` / ``SECRET`` in the (gitignored) ``.env``
at the repo root. Without credentials every test here is skipped, so CI
stays offline. Skip them explicitly with ``pytest --ignore=tests/live``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip("'\"")
    return values


def _credentials() -> tuple[str, str] | None:
    uid = os.environ.get("INTRA42_UID")
    secret = os.environ.get("INTRA42_SECRET")
    if not (uid and secret):
        env = _read_env_file(ENV_FILE)
        uid, secret = env.get("UID"), env.get("SECRET")
    return (uid, secret) if uid and secret else None


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    live_dir = Path(__file__).resolve().parent
    have_creds = _credentials() is not None
    for item in items:
        if live_dir in item.path.resolve().parents:
            if not have_creds:
                item.add_marker(pytest.mark.skip(reason="no 42 API credentials"))


@pytest.fixture(scope="session")
def credentials() -> tuple[str, str]:
    creds = _credentials()
    if creds is None:
        pytest.skip("no 42 API credentials")
    return creds
