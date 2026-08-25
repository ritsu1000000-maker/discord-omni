from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

def _iso(dt):
    return dt.isoformat() if isinstance(dt, datetime) else dt

@dataclass
class Embed:
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    color: Optional[int] = None
    timestamp: Optional[datetime | str] = None
    fields: list[dict[str, Any]] = field(default_factory=list)
    footer: Optional[dict[str, Any]] = None
    image: Optional[dict[str, Any]] = None
    thumbnail: Optional[dict[str, Any]] = None
    author: Optional[dict[str, Any]] = None

    def add_field(self, name, value, *, inline=False):
        self.fields.append({"name": str(name), "value": str(value), "inline": bool(inline)})
        return self

    def set_footer(self, text, *, icon_url=None):
        self.footer = {"text": str(text)}
        if icon_url is not None: self.footer["icon_url"] = str(icon_url)
        return self

    def set_image(self, url):
        self.image = {"url": str(url)}
        return self

    def set_thumbnail(self, url):
        self.thumbnail = {"url": str(url)}
        return self

    def set_author(self, name, *, url=None, icon_url=None):
        self.author = {"name": str(name)}
        if url is not None: self.author["url"] = str(url)
        if icon_url is not None: self.author["icon_url"] = str(icon_url)
        return self

    def to_dict(self):
        d = {}
        for key in ("title", "description", "url", "color"):
            value = getattr(self, key)
            if value is not None: d[key] = value
        if self.timestamp is not None: d["timestamp"] = _iso(self.timestamp)
        if self.fields: d["fields"] = list(self.fields)
        for key in ("footer", "image", "thumbnail", "author"):
            value = getattr(self, key)
            if value is not None: d[key] = value
        return d

@dataclass
class AllowedMentions:
    parse: list[str] = field(default_factory=list)
    users: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    replied_user: bool = False

    @classmethod
    def none(cls):
        return cls()

    @classmethod
    def all(cls):
        return cls(parse=["users", "roles", "everyone"])

    def to_dict(self):
        d = {"parse": list(self.parse), "replied_user": bool(self.replied_user)}
        if self.users: d["users"] = [str(x) for x in self.users]
        if self.roles: d["roles"] = [str(x) for x in self.roles]
        return d

@dataclass
class PollAnswer:
    text: str
    emoji: Optional[dict[str, Any]] = None

    def to_dict(self):
        media = {"text": self.text}
        if self.emoji is not None: media["emoji"] = self.emoji
        return {"poll_media": media}

@dataclass
class Poll:
    question: str
    answers: list[PollAnswer]
    duration: int = 24
    allow_multiselect: bool = False
    layout_type: int = 1

    def to_dict(self):
        return {
            "question": {"text": self.question},
            "answers": [x.to_dict() if hasattr(x, "to_dict") else x for x in self.answers],
            "duration": int(self.duration),
            "allow_multiselect": bool(self.allow_multiselect),
            "layout_type": int(self.layout_type),
        }

def message_payload(
    content=None, *,
    embeds=None,
    components=None,
    allowed_mentions=None,
    poll=None,
    flags=None,
    tts=False,
    nonce=None,
    message_reference=None,
):
    payload = {"tts": bool(tts)}
    if content is not None: payload["content"] = str(content)
    if embeds is not None:
        payload["embeds"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in embeds]
    if components is not None:
        payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
    if allowed_mentions is not None:
        payload["allowed_mentions"] = allowed_mentions.to_dict() if hasattr(allowed_mentions, "to_dict") else allowed_mentions
    if poll is not None:
        payload["poll"] = poll.to_dict() if hasattr(poll, "to_dict") else poll
    if flags is not None: payload["flags"] = int(flags)
    if nonce is not None:
        payload["nonce"] = str(nonce)
        payload["enforce_nonce"] = True
    if message_reference is not None:
        payload["message_reference"] = message_reference
    return payload
