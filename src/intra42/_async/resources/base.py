"""Generic resource base class shared by all async resource managers.

Concrete resources (``AsyncUsersResource``, ``AsyncCampusesResource``, ...)
are thin subclasses that just set ``path`` and ``model``. ``.filter()``,
``.sort()``, ``.all()`` etc. delegate to :class:`AsyncQuerySet`, and the
resource itself is iterable (``async for x in client.users``) for the
unfiltered, unsorted case.

Resources whose model exposes nested sub-resources (e.g. ``User.events``,
``Campus.users``) override ``_bind_relations()`` to attach lazy accessor
factories to each freshly parsed instance.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast

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

    def _bind_relations(self, instance: ModelT) -> None:
        """Attach nested-resource accessors to a freshly parsed instance.

        No-op by default. Applied to instances from both ``.get()`` and
        queryset iteration, so relations work the same either way.
        """
        return

    async def get(self, id: int | str) -> ModelT:
        """Fetch a single resource by id: ``GET {path}/{id}``."""
        response = await self._client.request("GET", f"{self.path}/{id}")
        instance = cast(ModelT, self.model.model_validate(response.json()))
        self._bind_relations(instance)
        return instance

    def _queryset(self, path: str | None = None) -> AsyncQuerySet[ModelT]:
        return AsyncQuerySet(
            self._client,
            path or self.path,
            cast(type[ModelT], self.model),
            bind=self._bind_relations,
        )

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
