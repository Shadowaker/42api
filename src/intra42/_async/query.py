"""Lazy, chainable, auto-paginating query builder.

``AsyncQuerySet`` is returned by a resource's ``.filter()``/``.sort()``/etc.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .._pagination import parse_link_header
from .._query_params import build_query_params
from ..models.base import FortyTwoModel

if TYPE_CHECKING:
    from .client import AsyncClient

ModelT = TypeVar("ModelT", bound=FortyTwoModel)


class AsyncQuerySet(Generic[ModelT]):
    def __init__(
        self,
        client: AsyncClient,
        path: str,
        model: type[ModelT],
        *,
        bind: Callable[[ModelT], None] | None = None,
    ) -> None:
        self._client = client
        self._path = path
        self._model = model
        # Set by the owning resource to attach nested-resource accessors
        # (e.g. User.events) to each instance as it's parsed. See
        # AsyncResource._bind_relations / FortyTwoModel._bind_relation.
        self._bind = bind
        self._filters: dict[str, Any] = {}
        self._sort_fields: list[str] = []
        self._page_size: int | None = None
        self._ranges: dict[str, tuple[Any, Any]] = {}

    def _clone(self) -> AsyncQuerySet[ModelT]:
        clone = AsyncQuerySet(self._client, self._path, self._model, bind=self._bind)
        clone._filters = dict(self._filters)
        clone._sort_fields = list(self._sort_fields)
        clone._page_size = self._page_size
        clone._ranges = dict(self._ranges)
        return clone

    def filter(self, **kwargs: Any) -> AsyncQuerySet[ModelT]:
        """Add ``filter[field]=value`` constraints. Chainable, non-mutating."""
        clone = self._clone()
        clone._filters.update(kwargs)
        return clone

    def sort(self, *fields: str) -> AsyncQuerySet[ModelT]:
        """Set the ``sort`` param, e.g. ``.sort('-level', 'login')``."""
        clone = self._clone()
        clone._sort_fields = list(fields)
        return clone

    def page_size(self, n: int) -> AsyncQuerySet[ModelT]:
        clone = self._clone()
        clone._page_size = n
        return clone

    def range(self, field: str, start: Any, end: Any) -> AsyncQuerySet[ModelT]:
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

    async def __aiter__(self) -> AsyncIterator[ModelT]:
        url: str | None = self._path
        params: dict[str, str] | None = self._initial_params()
        while url is not None:
            response = await self._client.request("GET", url, params=params)
            for item in response.json():
                instance = self._model.model_validate(item)
                if self._bind is not None:
                    self._bind(instance)
                yield instance
            url = parse_link_header(response.headers.get("Link")).get("next")
            params = None  # the next URL already carries its full query string

    async def all(self) -> list[ModelT]:
        return [item async for item in self]

    async def first(self) -> ModelT | None:
        async for item in self:
            return item
        return None
