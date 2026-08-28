"""Client configuration knobs, shared by the sync and async clients."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_BASE_URL = "https://api.intra.42.fr/v2"


@dataclass(slots=True)
class ClientConfig:
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 10.0
    max_retries: int = 3
    rate: float = 2.0
    burst: int = 2
    hourly_quota: int = 1200
