"""Shared base model for all 42 API resource models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FortyTwoModel(BaseModel):
    """Base class for every typed resource returned by the API.

    ``extra="allow"`` is deliberate: 42's API has historically added fields
    over time, so unknown keys are kept (inspectable via ``.model_extra``)
    rather than raising a ``ValidationError`` or silently discarding them.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
