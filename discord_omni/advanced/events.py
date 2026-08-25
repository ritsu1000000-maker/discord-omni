from __future__ import annotations
import asyncio
import inspect
from dataclasses import dataclass
from collections import defaultdict
from typing import Any, Callable, Optional


@dataclass
class Handler:
    callback: Callable
    priority: int = 0
    once: bool = False
    predicate: Optional[Callable] = None


class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
        self._waiters = defaultdict(list)
        self._middleware = []

    def use(self, middleware):
        self._middleware.append(middleware)
        return middleware

    def on(self, event, *, priority=0, once=False, predicate=None):
        def deco(fn):
            self._handlers[event].append(
                Handler(fn, priority=int(priority), once=bool(once), predicate=predicate)
            )
            self._handlers[event].sort(key=lambda h: h.priority, reverse=True)
            return fn
        return deco

    def once(self, event, *, priority=0, predicate=None):
        return self.on(event, priority=priority, once=True, predicate=predicate)

    async def _call(self, fn, *args, **kwargs):
        value = fn(*args, **kwargs)
        if inspect.isawaitable(value):
            value = await value
        return value

    async def emit(self, event, *args, **kwargs):
        context = {"event": event, "args": args, "kwargs": kwargs}
        for mw in self._middleware:
            allowed = await self._call(mw, context)
            if allowed is False:
                return []

        results = []
        remove = []
        for handler in list(self._handlers.get(event, [])):
            if handler.predicate is not None:
                ok = await self._call(handler.predicate, *args, **kwargs)
                if not ok:
                    continue
            results.append(await self._call(handler.callback, *args, **kwargs))
            if handler.once:
                remove.append(handler)
        for handler in remove:
            self._handlers[event].remove(handler)

        for fut, check in list(self._waiters.get(event, [])):
            if fut.done():
                continue
            try:
                ok = True if check is None else await self._call(check, *args, **kwargs)
                if ok:
                    fut.set_result((args, kwargs))
            except Exception as exc:
                fut.set_exception(exc)
        self._waiters[event] = [(f, c) for f, c in self._waiters[event] if not f.done()]
        return results

    async def wait_for(self, event, *, check=None, timeout=None):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self._waiters[event].append((fut, check))
        return await asyncio.wait_for(fut, timeout=timeout)

    def remove(self, event, callback):
        self._handlers[event] = [h for h in self._handlers[event] if h.callback is not callback]

    def clear(self, event=None):
        if event is None:
            self._handlers.clear()
            self._waiters.clear()
        else:
            self._handlers.pop(event, None)
            self._waiters.pop(event, None)
