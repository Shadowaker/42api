from intra42._rate_limit import RateLimiter


class FakeClock:
    """Injectable monotonic clock + sleep that advances time instantly."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds

    async def asleep(self, seconds: float) -> None:
        self.sleep(seconds)


def test_burst_capacity_allows_immediate_requests() -> None:
    clock = FakeClock()
    limiter = RateLimiter(rate=2.0, burst=2, monotonic=clock.monotonic, sleep=clock.sleep)

    limiter.acquire()
    limiter.acquire()

    assert clock.sleeps == []  # both within burst capacity, no waiting


def test_exceeding_burst_paces_requests() -> None:
    clock = FakeClock()
    limiter = RateLimiter(rate=2.0, burst=2, monotonic=clock.monotonic, sleep=clock.sleep)

    limiter.acquire()
    limiter.acquire()
    limiter.acquire()  # bucket empty, must wait ~0.5s for 1 token at rate=2/s

    assert clock.sleeps == [0.5]


async def test_aacquire_paces_requests(monkeypatch) -> None:
    import intra42._rate_limit as rl_module

    clock = FakeClock()

    async def fake_asyncio_sleep(seconds: float) -> None:
        clock.sleep(seconds)

    monkeypatch.setattr(rl_module.asyncio, "sleep", fake_asyncio_sleep)
    limiter = RateLimiter(rate=2.0, burst=1, monotonic=clock.monotonic, sleep=clock.sleep)

    await limiter.aacquire()
    await limiter.aacquire()

    assert clock.sleeps == [0.5]


def test_hourly_quota_forces_wait_until_window_reset() -> None:
    clock = FakeClock()
    limiter = RateLimiter(
        rate=1000.0, burst=1000, hourly_quota=1, monotonic=clock.monotonic, sleep=clock.sleep
    )

    limiter.acquire()  # consumes the only hourly slot
    limiter.acquire()  # must wait for the hourly window to roll over

    assert clock.sleeps == [3600.0]


def test_notify_retry_after_delays_next_acquire() -> None:
    clock = FakeClock()
    limiter = RateLimiter(rate=1000.0, burst=1000, monotonic=clock.monotonic, sleep=clock.sleep)

    limiter.notify_retry_after(5.0)
    limiter.acquire()

    assert clock.sleeps == [5.0]


def test_notify_retry_after_does_not_shrink_existing_cooldown() -> None:
    clock = FakeClock()
    limiter = RateLimiter(rate=1000.0, burst=1000, monotonic=clock.monotonic, sleep=clock.sleep)

    limiter.notify_retry_after(5.0)
    limiter.notify_retry_after(1.0)  # shorter — should not override the longer cooldown
    limiter.acquire()

    assert clock.sleeps == [5.0]
