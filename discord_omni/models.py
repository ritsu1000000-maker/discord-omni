from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(slots=True)
class APIModel:
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]):
        return cls(raw=dict(data))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)

    def __getitem__(self, key):
        return self.raw[key]

    def get(self, key, default=None):
        return self.raw.get(key, default)


@dataclass(slots=True)
class User(APIModel):
    id: str = ""
    username: str = ""
    global_name: Optional[str] = None
    bot: bool = False

    @classmethod
    def from_dict(cls, data):
        return cls(
            raw=dict(data),
            id=str(data.get("id", "")),
            username=data.get("username", ""),
            global_name=data.get("global_name"),
            bot=bool(data.get("bot", False)),
        )


@dataclass(slots=True)
class Role(APIModel):
    id: str = ""
    name: str = ""
    permissions: str = "0"

    @classmethod
    def from_dict(cls, data):
        return cls(
            raw=dict(data),
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            permissions=str(data.get("permissions", "0")),
        )


@dataclass(slots=True)
class Channel(APIModel):
    id: str = ""
    guild_id: Optional[str] = None
    name: Optional[str] = None
    type: int = 0

    @classmethod
    def from_dict(cls, data):
        return cls(
            raw=dict(data),
            id=str(data.get("id", "")),
            guild_id=str(data["guild_id"]) if data.get("guild_id") is not None else None,
            name=data.get("name"),
            type=int(data.get("type", 0)),
        )


@dataclass(slots=True)
class Guild(APIModel):
    id: str = ""
    name: str = ""
    owner_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            raw=dict(data),
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            owner_id=str(data["owner_id"]) if data.get("owner_id") is not None else None,
        )


@dataclass(slots=True)
class Member(APIModel):
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        user = User.from_dict(data["user"]) if data.get("user") else None
        return cls(
            raw=dict(data),
            user=user,
            nick=data.get("nick"),
            roles=[str(x) for x in data.get("roles", [])],
        )


@dataclass(slots=True)
class Message(APIModel):
    id: str = ""
    channel_id: str = ""
    guild_id: Optional[str] = None
    content: str = ""
    author: Optional[User] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            raw=dict(data),
            id=str(data.get("id", "")),
            channel_id=str(data.get("channel_id", "")),
            guild_id=str(data["guild_id"]) if data.get("guild_id") is not None else None,
            content=data.get("content", ""),
            author=User.from_dict(data["author"]) if data.get("author") else None,
        )


MODEL_MAP = {
    "user": User,
    "role": Role,
    "channel": Channel,
    "guild": Guild,
    "member": Member,
    "message": Message,
}


def model(kind: str, data):
    cls = MODEL_MAP[kind]
    if isinstance(data, list):
        return [cls.from_dict(x) for x in data]
    return cls.from_dict(data)
