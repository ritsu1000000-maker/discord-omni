from __future__ import annotations
import importlib
import inspect
from dataclasses import dataclass
from typing import Any


@dataclass
class PluginInfo:
    name: str
    module: str
    instance: Any


class PluginManager:
    def __init__(self, app=None):
        self.app = app
        self.plugins = {}

    async def _maybe(self, value):
        if inspect.isawaitable(value):
            return await value
        return value

    async def load(self, module_name: str, *, name=None):
        module = importlib.import_module(module_name)
        setup = getattr(module, "setup", None)
        if setup is None:
            raise AttributeError(f"{module_name} has no setup(app) function")
        instance = await self._maybe(setup(self.app))
        key = name or module_name
        self.plugins[key] = PluginInfo(key, module_name, instance)
        return instance

    async def unload(self, name: str):
        info = self.plugins.pop(name)
        teardown = getattr(info.instance, "teardown", None) if info.instance is not None else None
        if teardown is not None:
            await self._maybe(teardown())

    def get(self, name, default=None):
        info = self.plugins.get(name)
        return default if info is None else info.instance

    def names(self):
        return sorted(self.plugins)
