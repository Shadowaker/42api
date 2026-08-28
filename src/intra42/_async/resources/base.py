"""Generic resource base class shared by all async resource managers.

Concrete resources (``AsyncUsersResource``, ``AsyncCampusesResource``, ...)
are thin subclasses that just set ``path`` and ``model``. ``.filter()``,
``.sort()``, ``.all()`` etc. delegate to :class:`AsyncQuerySet`, and the
resource itself is iterable (``async for x in client.users``) for the
unfiltered, unsorted case.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from ...models.base import FortyTwoModel
from ..query import AsyncQuerySet

if TYPE_CHECKING:
    from ..client import AsyncClient

ModelT = TypeVar("ModelT", bound=FortyTwoModel)


class AsyncResource(Generic[ModelT]):
    path: ClassVar[str]
    model: ClassVar[type[FortyTwoModel]]

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get(self, id: int | str) -> ModelT:
        """Fetch a single resource by id: ``GET {path}/{id}``."""
        response = await self._client.request("GET", f"{self.path}/{id}")
        return self.model.model_validate(response.json())  # type: ignore[return-value]

    def _queryset(self) -> AsyncQuerySet[ModelT]:
        return AsyncQuerySet(self._client, self.path, self.model)  # type: ignore[arg-type]

    def filter(self, **kwargs: Any) -> AsyncQuerySet[ModelT]:
        return self._queryset().filter(**kwargs)

    def sort(self, *fields: str) -> AsyncQuerySet[ModelT]:
        return self._queryset().sort(*fields)

    def page_size(self, n: int) -> AsyncQuerySet[ModelT]:
        return self._queryset().page_size(n)

    def range(self, field: str, start: Any, end: Any) -> AsyncQuerySet[ModelT]:
        return self._queryset().range(field, start, end)

    async def all(self) -> list[ModelT]:
        return await self._queryset().all()

    async def first(self) -> ModelT | None:
        return await self._queryset().first()

    def __aiter__(self) -> AsyncIterator[ModelT]:
        return self._queryset().__aiter__()
