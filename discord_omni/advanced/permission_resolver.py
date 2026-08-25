from __future__ import annotations
from .state import TTLCache
from ..permissions import ADMINISTRATOR


class PermissionResolver:
    def __init__(self, *, cache_ttl=60.0):
        self.cache = TTLCache(ttl=cache_ttl, max_size=5000)

    def guild_permissions(self, guild, member, roles):
        guild_id = str(guild["id"])
        user_id = str((member.get("user") or {}).get("id"))
        cache_key = ("guild", guild_id, user_id, tuple(sorted(map(str, member.get("roles") or []))))
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        if str(guild.get("owner_id")) == user_id:
            value = (1 << 53) - 1
            self.cache.set(cache_key, value)
            return value

        role_map = {str(r["id"]): r for r in roles}
        everyone = role_map.get(guild_id, {})
        value = int(everyone.get("permissions", 0))
        for role_id in member.get("roles") or []:
            role = role_map.get(str(role_id))
            if role:
                value |= int(role.get("permissions", 0))

        if value & ADMINISTRATOR:
            value = (1 << 53) - 1

        self.cache.set(cache_key, value)
        return value

    def channel_permissions(self, guild, member, roles, channel):
        base = self.guild_permissions(guild, member, roles)
        if base & ADMINISTRATOR:
            return (1 << 53) - 1

        guild_id = str(guild["id"])
        user_id = str((member.get("user") or {}).get("id"))
        role_ids = {str(x) for x in member.get("roles") or []}

        overwrites = channel.get("permission_overwrites") or []
        everyone = next((o for o in overwrites if str(o.get("id")) == guild_id), None)
        if everyone:
            base &= ~int(everyone.get("deny", 0))
            base |= int(everyone.get("allow", 0))

        allow = deny = 0
        for overwrite in overwrites:
            if str(overwrite.get("id")) in role_ids:
                deny |= int(overwrite.get("deny", 0))
                allow |= int(overwrite.get("allow", 0))
        base &= ~deny
        base |= allow

        member_ow = next((o for o in overwrites if str(o.get("id")) == user_id), None)
        if member_ow:
            base &= ~int(member_ow.get("deny", 0))
            base |= int(member_ow.get("allow", 0))
        return base
