# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

"""Lazy, chainable, auto-paginating query builder.

``AsyncQuerySet`` is returned by a resource's ``.filter()``/``.sort()``/etc.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .._pagination import parse_link_header
from .._query_params import build_query_params
from ..models.base import FortyTwoModel

if TYPE_CHECKING:
    from .client import Client

ModelT = TypeVar("ModelT", bound=FortyTwoModel)


class QuerySet(Generic[ModelT]):
    def __init__(self, client: Client, path: str, model: type[ModelT]) -> None:
        self._client = client
        self._path = path
        self._model = model
        self._filters: dict[str, Any] = {}
        self._sort_fields: list[str] = []
        self._page_size: int | None = None
        self._ranges: dict[str, tuple[Any, Any]] = {}

    def _clone(self) -> QuerySet[ModelT]:
        clone = QuerySet(self._client, self._path, self._model)
        clone._filters = dict(self._filters)
        clone._sort_fields = list(self._sort_fields)
        clone._page_size = self._page_size
        clone._ranges = dict(self._ranges)
        return clone

    def filter(self, **kwargs: Any) -> QuerySet[ModelT]:
        """Add ``filter[field]=value`` constraints. Chainable, non-mutating."""
        clone = self._clone()
        clone._filters.update(kwargs)
        return clone

    def sort(self, *fields: str) -> QuerySet[ModelT]:
        """Set the ``sort`` param, e.g. ``.sort('-level', 'login')``."""
        clone = self._clone()
        clone._sort_fields = list(fields)
        return clone

    def page_size(self, n: int) -> QuerySet[ModelT]:
        clone = self._clone()
        clone._page_size = n
        return clone

    def range(self, field: str, start: Any, end: Any) -> QuerySet[ModelT]:
        clone = self._clone()
        clone._ranges[field] = (start, end)
        return clone

    def _initial_params(self) -> dict[str, str]:
        return build_query_params(
            filters=self._filters,
            sort=self._sort_fields,
            page_size=self._page_size,
            ranges=self._ranges,
        )

    def __iter__(self) -> Iterator[ModelT]:
        url: str | None = self._path
        params: dict[str, str] | None = self._initial_params()
        while url is not None:
            response = self._client.request("GET", url, params=params)
            for item in response.json():
                yield self._model.model_validate(item)
            url = parse_link_header(response.headers.get("Link")).get("next")
            params = None  # the next URL already carries its full query string

    def all(self) -> list[ModelT]:
        return [item for item in self]

    def first(self) -> ModelT | None:
        for item in self:
            return item
        return None
