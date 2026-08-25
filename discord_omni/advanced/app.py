from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any

from .events import EventBus
from .router import ComponentRouter, CommandRouter
from .plugins import PluginManager
from .state import AsyncStateStore
from .metrics import Metrics
from .permission_resolver import PermissionResolver
from ..app import DiscordApp


@dataclass(slots=True)
class AdvancedContext:
    payload: dict[str, Any]

    @property
    def user(self):
        return (self.payload.get("member") or {}).get("user") or self.payload.get("user") or {}

    @property
    def user_id(self):
        return str(self.user.get("id", ""))

    @property
    def guild_id(self):
        value = self.payload.get("guild_id")
        return None if value is None else str(value)

    @property
    def channel_id(self):
        value = self.payload.get("channel_id")
        return None if value is None else str(value)


class AdvancedDiscordApp(DiscordApp):
    """
    High-level orchestration layer on top of DiscordApp.
    Adds event bus, component/command routers, state, metrics, plugins,
    and permission resolution.
    """

    def __init__(self, token, *, application_id=None, intents=0, compress=True):
        super().__init__(token, application_id=application_id, intents=intents, compress=compress)
        self.bus = EventBus()
        self.components = ComponentRouter()
        self.commands_router = CommandRouter()
        self.state = AsyncStateStore()
        self.metrics = Metrics()
        self.permissions = PermissionResolver()
        self.plugins = PluginManager(self)

        @self.gateway.event("*")
        async def _forward(data):
            # Gateway wildcard callback receives data only in current gateway.
            self.metrics.inc("gateway.events")
            await self.bus.emit("gateway", data)

    def component(self, pattern, **kwargs):
        return self.components.route(pattern, **kwargs)

    def routed_command(self, name, **kwargs):
        return self.commands_router.command(name, **kwargs)

    async def dispatch_component(self, custom_id, payload):
        self.metrics.inc("interaction.components")
        return await self.components.dispatch(custom_id, AdvancedContext(payload))

    async def dispatch_command(self, name, payload, **options):
        self.metrics.inc("interaction.commands")
        return await self.commands_router.dispatch(name, AdvancedContext(payload), **options)
