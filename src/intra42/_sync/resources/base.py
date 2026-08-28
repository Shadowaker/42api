# GENERATED FILE — DO NOT EDIT BY HAND.
#
# Generated from the corresponding module under intra42._async by
# scripts/unasync_generate.py (via the `unasync` library). Edit the
# async source and re-run that script instead.

"""Generic resource base class shared by all async resource managers.

Concrete resources (``AsyncUsersResource``, ``AsyncCampusesResource``, ...)
are thin subclasses that just set ``path`` and ``model``. ``.filter()``,
``.sort()``, ``.all()`` etc. delegate to :class:`AsyncQuerySet`, and the
resource itself is iterable (``async for x in client.users``) for the
unfiltered, unsorted case.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from ...models.base import FortyTwoModel
from ..query import QuerySet

if TYPE_CHECKING:
    from ..client import Client

ModelT = TypeVar("ModelT", bound=FortyTwoModel)


class Resource(Generic[ModelT]):
    path: ClassVar[str]
    model: ClassVar[type[FortyTwoModel]]

    def __init__(self, client: Client) -> None:
        self._client = client

    def get(self, id: int | str) -> ModelT:
        """Fetch a single resource by id: ``GET {path}/{id}``."""
        response = self._client.request("GET", f"{self.path}/{id}")
        return self.model.model_validate(response.json())  # type: ignore[return-value]

    def _queryset(self) -> QuerySet[ModelT]:
        return QuerySet(self._client, self.path, self.model)  # type: ignore[arg-type]

    def filter(self, **kwargs: Any) -> QuerySet[ModelT]:
        return self._queryset().filter(**kwargs)

    def sort(self, *fields: str) -> QuerySet[ModelT]:
        return self._queryset().sort(*fields)

    def page_size(self, n: int) -> QuerySet[ModelT]:
        return self._queryset().page_size(n)

    def range(self, field: str, start: Any, end: Any) -> QuerySet[ModelT]:
        return self._queryset().range(field, start, end)

    def all(self) -> list[ModelT]:
        return self._queryset().all()

    def first(self) -> ModelT | None:
        return self._queryset().first()

    def __iter__(self) -> Iterator[ModelT]:
        return self._queryset().__iter__()
