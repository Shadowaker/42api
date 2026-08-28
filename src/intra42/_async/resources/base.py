"""Generic resource base class shared by all async resource managers.

Concrete resources (``AsyncUsersResource``, ``AsyncCampusesResource``, ...)
are thin subclasses that just set ``path`` and ``model``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from ...models.base import FortyTwoModel

if TYPE_CHECKING:
    from ..client import AsyncClient

ModelT = TypeVar("ModelT", bound=FortyTwoModel)


class AsyncResource(Generic[ModelT]):
    path: ClassVar[str]
    model: ClassVar[type[FortyTwoModel]]

    def __init__(self, client: "AsyncClient") -> None:
        self._client = client

    async def get(self, id: int | str) -> ModelT:
        """Fetch a single resource by id: ``GET {path}/{id}``."""
        response = await self._client.request("GET", f"{self.path}/{id}")
        return self.model.model_validate(response.json())  # type: ignore[return-value]
