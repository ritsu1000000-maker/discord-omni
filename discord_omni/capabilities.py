from __future__ import annotations
from collections import Counter, defaultdict
from .official_routes import OFFICIAL_ROUTES

CATEGORY_PREFIXES = [
    ("messages", "/channels/"),
    ("guilds", "/guilds/"),
    ("applications", "/applications/"),
    ("webhooks", "/webhooks/"),
    ("interactions", "/interactions/"),
    ("users", "/users/"),
    ("oauth2", "/oauth2/"),
    ("stage", "/stage-instances"),
    ("stickers", "/sticker"),
    ("soundboard", "/soundboard"),
    ("voice", "/voice/"),
    ("gateway", "/gateway"),
]

def route_summary():
    counts = Counter()
    for spec in OFFICIAL_ROUTES.values():
        category = "other"
        for name, prefix in CATEGORY_PREFIXES:
            if spec.path.startswith(prefix):
                category = name
                break
        counts[category] += 1
    return dict(sorted(counts.items()))

def capabilities():
    return {
        "official_route_count": len(OFFICIAL_ROUTES),
        "categories": route_summary(),
        "supports": [
            "sync REST",
            "async REST",
            "Gateway v10",
            "Gateway resume/reconnect",
            "zlib-stream",
            "sharding",
            "webhooks",
            "interactions HTTP server",
            "application commands",
            "Components V2",
            "OAuth2",
            "guild/member/role/channel moderation",
            "threads",
            "scheduled events",
            "AutoMod",
            "soundboard",
            "polls",
            "stickers/emojis",
            "monetization endpoints",
            "typed models",
            "Snowflake helpers",
            "permission helpers",
            "message/embed/poll builders",
            "community extensions",
        ],
    }
