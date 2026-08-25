from __future__ import annotations
import inspect
from typing import Callable


class MiddlewarePipeline:
    def __init__(self):
        self.before = []
        self.after = []
        self.errors = []

    def before_request(self, fn):
        self.before.append(fn)
        return fn

    def after_response(self, fn):
        self.after.append(fn)
        return fn

    def on_error(self, fn):
        self.errors.append(fn)
        return fn

    async def _call(self, fn, *args):
        value = fn(*args)
        if inspect.isawaitable(value):
            value = await value
        return value

    async def run(self, request, handler):
        try:
            current = request
            for fn in self.before:
                value = await self._call(fn, current)
                if value is not None:
                    current = value

            result = await self._call(handler, current)

            for fn in reversed(self.after):
                value = await self._call(fn, current, result)
                if value is not None:
                    result = value
            return result
        except Exception as exc:
            for fn in self.errors:
                value = await self._call(fn, request, exc)
                if value is not None:
                    return value
            raise
