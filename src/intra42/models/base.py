"""Shared base model for all 42 API resource models."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, PrivateAttr


class FortyTwoModel(BaseModel):
    """Base class for every typed resource returned by the API.

    ``extra="allow"`` is deliberate: 42's API has historically added fields
    over time, so unknown keys are kept (inspectable via ``.model_extra``)
    rather than raising a ``ValidationError`` or silently discarding them.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # Nested-resource accessors (e.g. User.events) are not
    # hardcoded, they're bound per-instance by whichever resource
    # fetched this object, as a lazily invoked factory.
    _relations: dict[str, Callable[[], Any]] = PrivateAttr(default_factory=dict)

    def _bind_relation(self, name: str, factory: Callable[[], Any]) -> None:
        """Attach a lazily-invoked nested-resource accessor to this instance.

        Called internally by Client/AsyncClient resources right after
        parsing a response; not meant to be called directly.
        """
        self._relations[name] = factory

    def _relation(self, name: str) -> Any:
        """Resolve a nested-resource accessor bound via ``_bind_relation``.

        Raises ``RuntimeError`` with a clear message if this instance wasn't
        fetched through a Client/AsyncClient
        """
        try:
            factory = self._relations[name]
        except KeyError:
            raise RuntimeError(
                f"'{name}' is only available on a {type(self).__name__} instance "
                "fetched via Client/AsyncClient, not one constructed manually."
            ) from None
        return factory()
