from __future__ import annotations
from .models import GuildSnapshot


def fetch_snapshot(client, guild_id, *, include_automod=True):
    official = client.official
    guild = official.get_guild(guild_id=guild_id)
    channels = official.get_guild_channels(guild_id=guild_id)
    roles = official.list_roles(guild_id=guild_id)

    automod = []
    if include_automod:
        try:
            automod = official.list_automod_rules(guild_id=guild_id)
        except Exception:
            automod = []

    return GuildSnapshot(
        guild_id=str(guild_id),
        guild=guild,
        channels=channels,
        roles=roles,
        automod_rules=automod,
    )


async def fetch_snapshot_async(client, guild_id, *, include_automod=True):
    official = client.official
    guild = await official.get_guild(guild_id=guild_id)
    channels = await official.get_guild_channels(guild_id=guild_id)
    roles = await official.list_roles(guild_id=guild_id)

    automod = []
    if include_automod:
        try:
            automod = await official.list_automod_rules(guild_id=guild_id)
        except Exception:
            automod = []

    return GuildSnapshot(
        guild_id=str(guild_id),
        guild=guild,
        channels=channels,
        roles=roles,
        automod_rules=automod,
    )
