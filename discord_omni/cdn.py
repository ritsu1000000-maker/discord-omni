CDN_BASE = "https://cdn.discordapp.com"

def user_avatar_url(user_id, avatar_hash, *, size=1024, extension=None):
    ext = extension or ("gif" if str(avatar_hash).startswith("a_") else "png")
    return f"{CDN_BASE}/avatars/{user_id}/{avatar_hash}.{ext}?size={int(size)}"

def guild_icon_url(guild_id, icon_hash, *, size=1024, extension=None):
    ext = extension or ("gif" if str(icon_hash).startswith("a_") else "png")
    return f"{CDN_BASE}/icons/{guild_id}/{icon_hash}.{ext}?size={int(size)}"

def emoji_url(emoji_id, *, animated=False, size=128):
    return f"{CDN_BASE}/emojis/{emoji_id}.{'gif' if animated else 'png'}?size={int(size)}"
