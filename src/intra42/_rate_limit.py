"""Automatic request pacing to stay under the 42 API's rate limits.

Combines a token bucket (per-second pacing) with an hourly quota counter and
a ``Retry-After`` cooldown gate shared by both the sync and async
acquire paths.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable

DEFAULT_RATE = 2.0  # requests per second
DEFAULT_BURST = 2  # bucket capacity
DEFAULT_HOURLY_QUOTA = 1200
HOUR_SECONDS = 3600.0


class RateLimiter:
    def __init__(
        self,
        *,
        rate: float = DEFAULT_RATE,
        burst: int = DEFAULT_BURST,
        hourly_quota: int = DEFAULT_HOURLY_QUOTA,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
    
        self._rate = rate
        self._capacity = float(burst)
        self._hourly_quota = hourly_quota
        self._monotonic = monotonic
        self._sleep = sleep

        now = monotonic()
        self._tokens = self._capacity
        self._last_refill = now

        self._hour_window_start = now
        self._hour_count = 0

        self._retry_after_until = 0.0

        self._lock = threading.Lock()
        self._alock = asyncio.Lock()

    def _refill(self, now: float) -> None:
        elapsed = now - self._last_refill
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
            self._last_refill = now

        if now - self._hour_window_start >= HOUR_SECONDS:
            self._hour_window_start = now
            self._hour_count = 0

    def _compute_wait(self, now: float) -> float:
        self._refill(now)

        waits = [0.0]

        if self._tokens < 1.0:
            waits.append((1.0 - self._tokens) / self._rate)

        if self._hour_count >= self._hourly_quota:
            waits.append(self._hour_window_start + HOUR_SECONDS - now)

        if self._retry_after_until > now:
            waits.append(self._retry_after_until - now)

        return max(waits)

    def _consume(self) -> None:
        # Called immediately after the wait, while still holding the lock.
        now = self._monotonic()
        self._refill(now)
        self._tokens = max(0.0, self._tokens - 1.0)
        self._hour_count += 1


    # No lock needed: monotonically extending a float is safe to race,
    # and only ever makes the next acquire() wait *more*, never less.
    def notify_retry_after(self, seconds: float) -> None:
        until = self._monotonic() + max(0.0, seconds)
        if until > self._retry_after_until:
            self._retry_after_until = until

    def acquire(self) -> None:
        with self._lock:
            wait = self._compute_wait(self._monotonic())
            if wait > 0:
                self._sleep(wait)
            self._consume()

    async def aacquire(self) -> None:
        async with self._alock:
            wait = self._compute_wait(self._monotonic())
            if wait > 0:
                await asyncio.sleep(wait)
            self._consume()
