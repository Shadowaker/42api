"""Pure helpers for building 42 API query strings."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def _stringify(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _join(value: Any) -> str:
    if isinstance(value, (list, tuple, set)):
        return ",".join(_stringify(v) for v in value)
    return _stringify(value)


def build_query_params(
    *,
    filters: Mapping[str, Any] | None = None,
    sort: Sequence[str] | None = None,
    page_size: int | None = None,
    page_number: int | None = None,
    ranges: Mapping[str, tuple[Any, Any]] | None = None,
) -> dict[str, str]:
    """Assemble a flat ``{param_name: value}`` dict ready to pass to httpx.

    - ``filters={"campus_id": 1}`` -> ``{"filter[campus_id]": "1"}``
    - ``filters={"campus_id": [1, 2]}`` -> ``{"filter[campus_id]": "1,2"}``
    - ``sort=["-level", "login"]`` -> ``{"sort": "-level,login"}``
    - ``page_size=30`` -> ``{"page[size]": "30"}``
    - ``ranges={"id": (1, 100)}`` -> ``{"range[id]": "1,100"}``
    """
    params: dict[str, str] = {}

    for key, value in (filters or {}).items():
        params[f"filter[{key}]"] = _join(value)

    if sort:
        params["sort"] = ",".join(sort)

    if page_size is not None:
        params["page[size]"] = str(page_size)

    if page_number is not None:
        params["page[number]"] = str(page_number)

    for key, (start, end) in (ranges or {}).items():
        params[f"range[{key}]"] = f"{_stringify(start)},{_stringify(end)}"

    return params
