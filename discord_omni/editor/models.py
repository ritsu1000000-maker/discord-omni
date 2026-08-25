from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from typing import Any


@dataclass(slots=True)
class GuildSnapshot:
    guild_id: str
    guild: dict[str, Any]
    channels: list[dict[str, Any]] = field(default_factory=list)
    roles: list[dict[str, Any]] = field(default_factory=list)
    automod_rules: list[dict[str, Any]] = field(default_factory=list)

    def copy(self) -> "GuildSnapshot":
        return deepcopy(self)

    def channel_by_id(self, channel_id):
        sid = str(channel_id)
        return next((x for x in self.channels if str(x.get("id")) == sid), None)

    def role_by_id(self, role_id):
        sid = str(role_id)
        return next((x for x in self.roles if str(x.get("id")) == sid), None)

    def channel_by_name(self, name):
        return next((x for x in self.channels if x.get("name") == name), None)

    def role_by_name(self, name):
        return next((x for x in self.roles if x.get("name") == name), None)

    def to_dict(self):
        return {
            "guild_id": self.guild_id,
            "guild": deepcopy(self.guild),
            "channels": deepcopy(self.channels),
            "roles": deepcopy(self.roles),
            "automod_rules": deepcopy(self.automod_rules),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            guild_id=str(data["guild_id"]),
            guild=deepcopy(data.get("guild") or {}),
            channels=deepcopy(data.get("channels") or []),
            roles=deepcopy(data.get("roles") or []),
            automod_rules=deepcopy(data.get("automod_rules") or []),
        )
