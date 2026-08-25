from __future__ import annotations
import inspect
import re
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .limits import CooldownManager, CooldownError


@dataclass
class RouteEntry:
    pattern: re.Pattern
    callback: Callable
    check: Optional[Callable] = None
    cooldown: Optional[CooldownManager] = None
    key_func: Optional[Callable] = None


class ComponentRouter:
    def __init__(self):
        self.routes: list[RouteEntry] = []

    def route(self, pattern, *, check=None, cooldown=None, key_func=None):
        compiled = re.compile(pattern)
        def deco(fn):
            self.routes.append(RouteEntry(compiled, fn, check, cooldown, key_func))
            return fn
        return deco

    async def _call(self, fn, *args, **kwargs):
        value = fn(*args, **kwargs)
        if inspect.isawaitable(value):
            value = await value
        return value

    async def dispatch(self, custom_id: str, ctx):
        for route in self.routes:
            match = route.pattern.fullmatch(custom_id)
            if not match:
                continue
            if route.check is not None:
                allowed = await self._call(route.check, ctx)
                if not allowed:
                    raise PermissionError("component check failed")
            if route.cooldown is not None:
                key = route.key_func(ctx) if route.key_func else getattr(ctx, "user_id", "global")
                route.cooldown.check(key)
            return await self._call(route.callback, ctx, **match.groupdict())
        raise LookupError(f"No component route for custom_id={custom_id!r}")


class CommandRouter:
    def __init__(self):
        self.commands = {}

    def command(self, name, *, checks=None, cooldown=None, key_func=None):
        def deco(fn):
            self.commands[name] = {
                "callback": fn,
                "checks": list(checks or []),
                "cooldown": cooldown,
                "key_func": key_func,
            }
            return fn
        return deco

    async def _call(self, fn, *args, **kwargs):
        value = fn(*args, **kwargs)
        if inspect.isawaitable(value):
            value = await value
        return value

    async def dispatch(self, name, ctx, **options):
        entry = self.commands.get(name)
        if entry is None:
            raise LookupError(f"Unknown command: {name}")
        for check in entry["checks"]:
            if not await self._call(check, ctx):
                raise PermissionError("command check failed")
        cooldown = entry["cooldown"]
        if cooldown is not None:
            key_func = entry["key_func"]
            key = key_func(ctx) if key_func else getattr(ctx, "user_id", "global")
            cooldown.check(key)
        return await self._call(entry["callback"], ctx, **options)
