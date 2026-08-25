from __future__ import annotations
import asyncio
import inspect
from typing import Any, Optional

from .async_client import AsyncDiscordClient
from .gateway import DiscordGateway
from .builders import message_payload

class DiscordApp:
    """
    One object for the common bot workflow:
    Gateway events + async REST + command registration helpers.
    """

    def __init__(self, token: str, *, application_id=None, intents=0, compress=True):
        self.token = token
        self.application_id = str(application_id) if application_id is not None else None
        self.http = AsyncDiscordClient(token)
        self.gateway = DiscordGateway(token, intents=intents, compress=compress)
        self._commands: list[dict[str, Any]] = []

    def event(self, name=None):
        return self.gateway.event(name)

    def command(self, name, description, *, options=None, dm_permission=None,
                default_member_permissions=None, nsfw=None):
        def deco(fn):
            command = {
                "type": 1,
                "name": name,
                "description": description,
            }
            if options is not None: command["options"] = options
            if dm_permission is not None: command["dm_permission"] = bool(dm_permission)
            if default_member_permissions is not None:
                command["default_member_permissions"] = str(default_member_permissions)
            if nsfw is not None: command["nsfw"] = bool(nsfw)
            command["_handler"] = fn
            self._commands.append(command)
            return fn
        return deco

    def command_payloads(self):
        return [
            {k: v for k, v in item.items() if not k.startswith("_")}
            for item in self._commands
        ]

    async def sync_commands(self, *, guild_id=None):
        if self.application_id is None:
            raise ValueError("application_id is required to sync commands")
        payload = self.command_payloads()
        if guild_id is None:
            return await self.http.official.bulk_overwrite_global_commands(
                application_id=self.application_id,
                json=payload,
            )
        return await self.http.official.bulk_overwrite_guild_commands(
            application_id=self.application_id,
            guild_id=str(guild_id),
            json=payload,
        )

    async def send(self, channel_id, content=None, **kwargs):
        return await self.http.send(channel_id, content, **kwargs)

    async def start(self):
        await self.http.rest.open()
        try:
            await self.gateway.connect()
        finally:
            await self.http.rest.close()

    async def close(self):
        await self.gateway.close()
        await self.http.rest.close()

    def run(self):
        asyncio.run(self.start())
