from __future__ import annotations
import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass


class CooldownError(RuntimeError):
    def __init__(self, retry_after: float):
        super().__init__(f"Cooldown active for {retry_after:.2f}s")
        self.retry_after = retry_after


class CooldownManager:
    def __init__(self, rate: int = 1, per: float = 5.0):
        self.rate = max(1, int(rate))
        self.per = float(per)
        self._buckets = defaultdict(deque)

    def check(self, key) -> float:
        now = time.monotonic()
        bucket = self._buckets[key]
        while bucket and now - bucket[0] >= self.per:
            bucket.popleft()
        if len(bucket) >= self.rate:
            retry_after = self.per - (now - bucket[0])
            raise CooldownError(max(0.0, retry_after))
        bucket.append(now)
        return 0.0

    def reset(self, key):
        self._buckets.pop(key, None)

    def retry_after(self, key) -> float:
        now = time.monotonic()
        bucket = self._buckets.get(key)
        if not bucket or len(bucket) < self.rate:
            return 0.0
        return max(0.0, self.per - (now - bucket[0]))


class KeyedConcurrency:
    def __init__(self, limit: int = 1):
        self.limit = max(1, int(limit))
        self._semaphores = defaultdict(lambda: asyncio.Semaphore(self.limit))

    def for_key(self, key):
        return self._semaphores[key]


@dataclass(slots=True)
class RetryPolicy:
    attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 10.0
    jitter: float = 0.25

    def delay_for(self, attempt: int) -> float:
        import random
        base = min(self.max_delay, self.base_delay * (2 ** max(0, attempt)))
        return max(0.0, base + random.uniform(-self.jitter, self.jitter))


class CircuitBreakerOpen(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30.0):
        self.failure_threshold = int(failure_threshold)
        self.recovery_timeout = float(recovery_timeout)
        self.failures = 0
        self.opened_at = None

    def before_call(self):
        if self.opened_at is None:
            return
        if time.monotonic() - self.opened_at >= self.recovery_timeout:
            self.opened_at = None
            self.failures = 0
            return
        raise CircuitBreakerOpen("Circuit breaker is open")

    def success(self):
        self.failures = 0
        self.opened_at = None

    def failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.monotonic()
