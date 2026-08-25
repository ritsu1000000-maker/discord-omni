from .async_rest import AsyncDiscordREST
from .endpoints import EndpointMixin
from .models import model
from .official_api import AsyncOfficialAPI
from .builders import message_payload


class AsyncDiscordClient(EndpointMixin):
    def __init__(self, token=None, *, auth_scheme="Bot", timeout=25.0):
        self.rest = AsyncDiscordREST(token=token, auth_scheme=auth_scheme, timeout=timeout)
        self.official = AsyncOfficialAPI(self.rest)

    async def __aenter__(self):
        await self.rest.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.rest.close()

    def _call(self, method, path, **kwargs):
        return self.rest.request(method, path, **kwargs)

    async def official_request(self, route_name, **kwargs):
        """Call a whitelisted official route by registry name."""
        return await self.official.call(route_name, **kwargs)

    async def get_message_model(self, channel_id, message_id):
        return model("message", await self.get_message(channel_id, message_id))

    async def get_channel_model(self, channel_id):
        return model("channel", await self.get_channel(channel_id))

    async def get_guild_model(self, guild_id):
        return model("guild", await self.get_guild(guild_id))

    async def get_member_model(self, guild_id, user_id):
        return model("member", await self.get_member(guild_id, user_id))

    async def iter_members(self, guild_id, *, page_size=1000):
        after = None
        while True:
            page = await self.list_members(guild_id, limit=page_size, after=after)
            if not page:
                return
            for item in page:
                yield model("member", item)
            if len(page) < page_size:
                return
            last = page[-1].get("user", {}).get("id")
            if not last:
                return
            after = last

    async def iter_messages(self, channel_id, *, page_size=100, before=None):
        cursor = before
        while True:
            page = await self.get_messages(channel_id, limit=page_size, before=cursor)
            if not page:
                return
            for item in page:
                yield model("message", item)
            if len(page) < page_size:
                return
            cursor = page[-1].get("id")
            if not cursor:
                return

async def send(self, channel_id, content=None, *, embeds=None, components=None,
               allowed_mentions=None, poll=None, flags=None, tts=False,
               nonce=None, message_reference=None):
    """Convenient async message sender using structured builders."""
    payload = message_payload(
        content,
        embeds=embeds,
        components=components,
        allowed_mentions=allowed_mentions,
        poll=poll,
        flags=flags,
        tts=tts,
        nonce=nonce,
        message_reference=message_reference,
    )
    return await self.official.create_message(channel_id=channel_id, json=payload)

async def fetch(self, route_name, **kwargs):
    return await self.official_request(route_name, **kwargs)
