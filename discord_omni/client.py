from .rest import DiscordREST
from .endpoints import EndpointMixin
from .models import model
from .official_api import OfficialAPI
from .builders import message_payload


class DiscordClient(EndpointMixin):
    def __init__(self, token=None, *, auth_scheme="Bot", timeout=25.0):
        self.rest = DiscordREST(token=token, auth_scheme=auth_scheme, timeout=timeout)
        self.official = OfficialAPI(self.rest)

    def official_request(self, route_name, **kwargs):
        """Call a whitelisted official route by registry name."""
        return self.official.call(route_name, **kwargs)

    def get_message_model(self, channel_id, message_id):
        return model("message", self.get_message(channel_id, message_id))

    def get_channel_model(self, channel_id):
        return model("channel", self.get_channel(channel_id))

    def get_guild_model(self, guild_id):
        return model("guild", self.get_guild(guild_id))

    def get_member_model(self, guild_id, user_id):
        return model("member", self.get_member(guild_id, user_id))

    def send(self, channel_id, content=None, *, embeds=None, components=None,
             allowed_mentions=None, poll=None, flags=None, tts=False,
             nonce=None, message_reference=None):
        """Convenient message sender using structured builders."""
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
        return self.official.create_message(channel_id=channel_id, json=payload)

    def fetch(self, route_name, **kwargs):
        """Alias for official_request; only the official route registry is accepted."""
        return self.official_request(route_name, **kwargs)

    def editor(self, guild_id):
        """Return a high-level declarative GuildEditor."""
        from .editor import GuildEditor
        return GuildEditor(self, guild_id)
