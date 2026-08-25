from __future__ import annotations
import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl: float = 60.0, max_size: int = 1000):
        self.ttl = float(ttl)
        self.max_size = int(max_size)
        self._data: OrderedDict[Any, tuple[float, Any]] = OrderedDict()

    def _expired(self, expires: float) -> bool:
        return expires <= time.monotonic()

    def set(self, key, value, *, ttl: Optional[float] = None):
        expires = time.monotonic() + (self.ttl if ttl is None else float(ttl))
        self._data.pop(key, None)
        self._data[key] = (expires, value)
        while len(self._data) > self.max_size:
            self._data.popitem(last=False)

    def get(self, key, default=None):
        item = self._data.get(key)
        if item is None:
            return default
        expires, value = item
        if self._expired(expires):
            self._data.pop(key, None)
            return default
        self._data.move_to_end(key)
        return value

    def pop(self, key, default=None):
        item = self._data.pop(key, None)
        if item is None:
            return default
        expires, value = item
        return default if self._expired(expires) else value

    def has(self, key) -> bool:
        marker = object()
        return self.get(key, marker) is not marker

    def clear(self):
        self._data.clear()

    def cleanup(self) -> int:
        removed = 0
        now = time.monotonic()
        for key, (expires, _) in list(self._data.items()):
            if expires <= now:
                self._data.pop(key, None)
                removed += 1
        return removed

    def __len__(self):
        self.cleanup()
        return len(self._data)


class AsyncStateStore:
    def __init__(self, *, ttl: float = 900.0, max_size: int = 5000):
        self.cache = TTLCache(ttl=ttl, max_size=max_size)
        self.lock = asyncio.Lock()

    async def set(self, key, value, *, ttl=None):
        async with self.lock:
            self.cache.set(key, value, ttl=ttl)

    async def get(self, key, default=None):
        async with self.lock:
            return self.cache.get(key, default)

    async def delete(self, key):
        async with self.lock:
            return self.cache.pop(key, None)

    async def update(self, key, **fields):
        async with self.lock:
            value = dict(self.cache.get(key, {}))
            value.update(fields)
            self.cache.set(key, value)
            return value


@dataclass(slots=True)
class InteractionSession:
    user_id: str
    custom_id: str
    data: dict
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
