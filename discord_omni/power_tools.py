from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional
from urllib.parse import urlencode, urlparse

from .official_routes import OFFICIAL_ROUTES, get_route
from .snowflake import snowflake_time
from .permissions import Permissions, NAME_TO_BIT
from .components import (
    ActionRow, Button, StringSelect, TextInput, UserSelect, RoleSelect,
    MentionableSelect, ChannelSelect, Section, TextDisplay, Thumbnail,
    MediaGallery, FileComponent, Separator, Container, Label, FileUpload,
    RadioGroup, CheckboxGroup, Checkbox,
)

DISCORD_EPOCH_MS = 1420070400000
OAUTH_AUTHORIZE = "https://discord.com/oauth2/authorize"
CDN = "https://cdn.discordapp.com"
WEBHOOK_RE = re.compile(r"https?://(?:canary\.|ptb\.)?discord(?:app)?\.com/api(?:/v\d+)?/webhooks/(\d+)/([^/?#]+)")


# ---------------------------------------------------------------------------
# Text / mention / timestamp helpers
# ---------------------------------------------------------------------------

def mention_user(user_id): return f"<@{int(user_id)}>"
def mention_channel(channel_id): return f"<#{int(channel_id)}>"
def mention_role(role_id): return f"<@&{int(role_id)}>"
def mention_command(name, command_id): return f"</{name}:{int(command_id)}>"
def timestamp_unix(value):
    if isinstance(value, datetime):
        return int(value.timestamp())
    return int(value)
def timestamp_default(value): return f"<t:{timestamp_unix(value)}>"
def timestamp_short_time(value): return f"<t:{timestamp_unix(value)}:t>"
def timestamp_long_time(value): return f"<t:{timestamp_unix(value)}:T>"
def timestamp_short_date(value): return f"<t:{timestamp_unix(value)}:d>"
def timestamp_long_date(value): return f"<t:{timestamp_unix(value)}:D>"
def timestamp_short_datetime(value): return f"<t:{timestamp_unix(value)}:f>"
def timestamp_long_datetime(value): return f"<t:{timestamp_unix(value)}:F>"
def timestamp_relative(value): return f"<t:{timestamp_unix(value)}:R>"

def escape_markdown(text: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>~])", r"\\\1", str(text))

def remove_markdown(text: str) -> str:
    return re.sub(r"[*_~`>|]", "", str(text))

def escape_mentions(text: str) -> str:
    return str(text).replace("@", "@\u200b")

def split_message(text: str, limit: int = 2000) -> list[str]:
    text = str(text)
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if len(text) <= limit:
        return [text]
    out = []
    while text:
        chunk = text[:limit]
        if len(text) > limit:
            cut = max(chunk.rfind("\n"), chunk.rfind(" "))
            if cut > limit // 2:
                chunk = chunk[:cut]
        out.append(chunk)
        text = text[len(chunk):].lstrip()
    return out

def truncate(text: str, limit: int, suffix: str = "…") -> str:
    text = str(text)
    if len(text) <= limit:
        return text
    if limit <= len(suffix):
        return suffix[:limit]
    return text[:limit - len(suffix)] + suffix

def code_inline(text: str) -> str:
    return "`" + str(text).replace("`", "\\`") + "`"

def code_block(text: str, language: str = "") -> str:
    safe = str(text).replace("```", "``\u200b`")
    return f"```{language}\n{safe}\n```"

def quote_block(text: str) -> str:
    return "\n".join("> " + line for line in str(text).splitlines())

def spoiler(text: str) -> str:
    return f"||{text}||"


# ---------------------------------------------------------------------------
# Snowflake / ID helpers
# ---------------------------------------------------------------------------

def normalize_snowflake(value) -> str:
    value = str(value).strip()
    if not value.isdigit():
        raise ValueError("Discord snowflake must contain digits only")
    return str(int(value))

def is_snowflake(value) -> bool:
    try:
        n = int(str(value))
        return n > 0 and len(str(n)) >= 15
    except Exception:
        return False

def snowflake_created_at(value):
    return snowflake_time(value)

def snowflake_age_seconds(value, now: Optional[datetime] = None) -> float:
    now = now or datetime.now(timezone.utc)
    return max(0.0, (now - snowflake_time(value)).total_seconds())

def snowflake_sort(values: Iterable[int | str]) -> list[str]:
    return [str(x) for x in sorted(map(int, values))]

def snowflake_min(values: Iterable[int | str]) -> str:
    return str(min(map(int, values)))

def snowflake_max(values: Iterable[int | str]) -> str:
    return str(max(map(int, values)))

def make_nonce(bits: int = 63) -> str:
    return str(secrets.randbits(bits))

def id_or_none(value):
    return None if value is None else normalize_snowflake(value)


# ---------------------------------------------------------------------------
# Permission helpers
# ---------------------------------------------------------------------------

def permission_value(*names: str) -> int:
    return Permissions.from_names(*names).to_int()

def permission_has(value: int, permission: int | str) -> bool:
    return Permissions(int(value)).has(permission)

def permission_add(value: int, *permissions: int | str) -> int:
    return Permissions(int(value)).add(*permissions).to_int()

def permission_remove(value: int, *permissions: int | str) -> int:
    return Permissions(int(value)).remove(*permissions).to_int()

def permission_names(value: int) -> list[str]:
    p = Permissions(int(value))
    return [name for name, bit in NAME_TO_BIT.items() if p.has(bit)]

def permission_overwrite(*, target_id, target_type, allow=0, deny=0) -> dict[str, Any]:
    return {
        "id": str(target_id),
        "type": int(target_type),
        "allow": str(int(allow)),
        "deny": str(int(deny)),
    }

def apply_permission_overwrite(base: int, *, allow: int = 0, deny: int = 0) -> int:
    base = int(base)
    base &= ~int(deny)
    base |= int(allow)
    return base

def administrator_permissions() -> int:
    return NAME_TO_BIT["ADMINISTRATOR"]

def basic_text_permissions() -> int:
    return permission_value("VIEW_CHANNEL", "SEND_MESSAGES", "READ_MESSAGE_HISTORY")

def moderator_permissions() -> int:
    return permission_value("VIEW_CHANNEL", "MANAGE_MESSAGES", "KICK_MEMBERS", "BAN_MEMBERS", "MODERATE_MEMBERS")

def webhook_manager_permissions() -> int:
    return permission_value("VIEW_CHANNEL", "MANAGE_WEBHOOKS")

def command_user_permissions() -> int:
    return permission_value("VIEW_CHANNEL", "USE_APPLICATION_COMMANDS")


# ---------------------------------------------------------------------------
# OAuth2 / install / PKCE helpers
# ---------------------------------------------------------------------------

def scope_string(scopes: Iterable[str]) -> str:
    return " ".join(dict.fromkeys(str(x) for x in scopes))

def generate_oauth_state(bytes_length: int = 32) -> str:
    return secrets.token_urlsafe(bytes_length)

def generate_pkce_verifier(bytes_length: int = 64) -> str:
    return secrets.token_urlsafe(bytes_length)[:128]

def pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

def build_oauth_url(
    client_id,
    scopes,
    *,
    redirect_uri=None,
    state=None,
    permissions=None,
    guild_id=None,
    disable_guild_select=False,
    prompt=None,
    integration_type=None,
    code_challenge=None,
    code_challenge_method="S256",
):
    p = {
        "client_id": str(client_id),
        "response_type": "code",
        "scope": scope_string(scopes),
    }
    if redirect_uri is not None: p["redirect_uri"] = redirect_uri
    if state is not None: p["state"] = state
    if permissions is not None: p["permissions"] = str(int(permissions))
    if guild_id is not None: p["guild_id"] = str(guild_id)
    if disable_guild_select: p["disable_guild_select"] = "true"
    if prompt is not None: p["prompt"] = prompt
    if integration_type is not None: p["integration_type"] = str(integration_type)
    if code_challenge is not None:
        p["code_challenge"] = code_challenge
        p["code_challenge_method"] = code_challenge_method
    return OAUTH_AUTHORIZE + "?" + urlencode(p)

def build_bot_invite_url(client_id, permissions=0, *, guild_id=None, disable_guild_select=False):
    return build_oauth_url(
        client_id, ["bot", "applications.commands"],
        permissions=permissions,
        guild_id=guild_id,
        disable_guild_select=disable_guild_select,
    )

def build_commands_only_install_url(client_id, *, integration_type=None):
    return build_oauth_url(client_id, ["applications.commands"], integration_type=integration_type)

def build_identify_login_url(client_id, redirect_uri, *, state=None):
    return build_oauth_url(client_id, ["identify"], redirect_uri=redirect_uri, state=state)

def build_guilds_login_url(client_id, redirect_uri, *, state=None):
    return build_oauth_url(client_id, ["identify", "guilds"], redirect_uri=redirect_uri, state=state)

def oauth_pkce_bundle(client_id, scopes, redirect_uri, *, state=None):
    verifier = generate_pkce_verifier()
    challenge = pkce_challenge(verifier)
    state = state or generate_oauth_state()
    return {
        "verifier": verifier,
        "challenge": challenge,
        "state": state,
        "url": build_oauth_url(
            client_id, scopes,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=challenge,
        ),
    }


# ---------------------------------------------------------------------------
# Application command builders
# ---------------------------------------------------------------------------

def command_choice(name, value, *, name_localizations=None):
    d = {"name": str(name), "value": value}
    if name_localizations is not None: d["name_localizations"] = dict(name_localizations)
    return d

def _option(option_type, name, description, **kwargs):
    d = {"type": int(option_type), "name": name, "description": description}
    d.update({k: v for k, v in kwargs.items() if v is not None})
    return d

def string_option(name, description, **kwargs): return _option(3, name, description, **kwargs)
def integer_option(name, description, **kwargs): return _option(4, name, description, **kwargs)
def boolean_option(name, description, **kwargs): return _option(5, name, description, **kwargs)
def user_option(name, description, **kwargs): return _option(6, name, description, **kwargs)
def channel_option(name, description, **kwargs): return _option(7, name, description, **kwargs)
def role_option(name, description, **kwargs): return _option(8, name, description, **kwargs)
def mentionable_option(name, description, **kwargs): return _option(9, name, description, **kwargs)
def number_option(name, description, **kwargs): return _option(10, name, description, **kwargs)
def attachment_option(name, description, **kwargs): return _option(11, name, description, **kwargs)

def subcommand(name, description, *, options=None, name_localizations=None, description_localizations=None):
    return _option(
        1, name, description,
        options=options,
        name_localizations=name_localizations,
        description_localizations=description_localizations,
    )

def subcommand_group(name, description, *, options=None, name_localizations=None, description_localizations=None):
    return _option(
        2, name, description,
        options=options,
        name_localizations=name_localizations,
        description_localizations=description_localizations,
    )

def slash_command(name, description, *, options=None, contexts=None, integration_types=None,
                  default_member_permissions=None, nsfw=None, name_localizations=None,
                  description_localizations=None):
    d = {"type": 1, "name": name, "description": description}
    if options is not None: d["options"] = list(options)
    if contexts is not None: d["contexts"] = list(contexts)
    if integration_types is not None: d["integration_types"] = list(integration_types)
    if default_member_permissions is not None: d["default_member_permissions"] = str(default_member_permissions)
    if nsfw is not None: d["nsfw"] = bool(nsfw)
    if name_localizations is not None: d["name_localizations"] = dict(name_localizations)
    if description_localizations is not None: d["description_localizations"] = dict(description_localizations)
    return d

def user_command(name, **kwargs):
    d = {"type": 2, "name": name}
    d.update({k: v for k, v in kwargs.items() if v is not None})
    return d

def message_command(name, **kwargs):
    d = {"type": 3, "name": name}
    d.update({k: v for k, v in kwargs.items() if v is not None})
    return d

def command_permission(target_id, target_type, permission=True):
    return {"id": str(target_id), "type": int(target_type), "permission": bool(permission)}

def localization_map(**locales):
    return {k.replace("_", "-"): v for k, v in locales.items() if v is not None}

def autocomplete_choice(name, value, *, name_localizations=None):
    return command_choice(name, value, name_localizations=name_localizations)


# ---------------------------------------------------------------------------
# Message / flag / poll helpers
# ---------------------------------------------------------------------------

def reply_reference(message_id, *, channel_id=None, guild_id=None, fail_if_not_exists=True):
    d = {"message_id": str(message_id), "fail_if_not_exists": bool(fail_if_not_exists)}
    if channel_id is not None: d["channel_id"] = str(channel_id)
    if guild_id is not None: d["guild_id"] = str(guild_id)
    return d

def poll_answer(text, *, emoji_id=None, emoji_name=None):
    media = {"text": str(text)}
    if emoji_id is not None or emoji_name is not None:
        media["emoji"] = {"id": None if emoji_id is None else str(emoji_id), "name": emoji_name}
    return {"poll_media": media}

def poll_payload(question, answers, *, duration=24, allow_multiselect=False, layout_type=1):
    return {
        "question": {"text": str(question)},
        "answers": [x if isinstance(x, dict) else poll_answer(x) for x in answers],
        "duration": int(duration),
        "allow_multiselect": bool(allow_multiselect),
        "layout_type": int(layout_type),
    }

def flag_ephemeral(): return 1 << 6
def flag_suppress_embeds(): return 1 << 2
def flag_suppress_notifications(): return 1 << 12
def flag_components_v2(): return 1 << 15
def combine_flags(*flags): return sum(set(map(int, flags)))

def allowed_mentions_none():
    return {"parse": [], "users": [], "roles": [], "replied_user": False}

def allowed_mentions_all():
    return {"parse": ["users", "roles", "everyone"]}

def allowed_mentions_users(*user_ids):
    return {"parse": [], "users": [str(x) for x in user_ids]}

def allowed_mentions_roles(*role_ids):
    return {"parse": [], "roles": [str(x) for x in role_ids]}

def validate_message_content(content):
    if content is not None and len(str(content)) > 2000:
        raise ValueError("message content exceeds 2000 characters")
    return True

def chunk_embeds(embeds, size=10):
    embeds = list(embeds)
    return [embeds[i:i + size] for i in range(0, len(embeds), size)]


# ---------------------------------------------------------------------------
# Components V2 builders
# ---------------------------------------------------------------------------

def button(label=None, *, custom_id=None, style=1, emoji=None, disabled=False):
    return Button(label=label, custom_id=custom_id, style=style, emoji=emoji, disabled=disabled)

def link_button(label, url, *, emoji=None, disabled=False):
    return Button(label=label, style=5, url=url, emoji=emoji, disabled=disabled)

def premium_button(sku_id):
    return Button(style=6, sku_id=str(sku_id))

def action_row(*components):
    return ActionRow(list(components))

def select_option(label, value, *, description=None, emoji=None, default=False):
    d = {"label": label, "value": str(value), "default": bool(default)}
    if description is not None: d["description"] = description
    if emoji is not None: d["emoji"] = emoji
    return d

def string_select(custom_id, options, **kwargs):
    return StringSelect(custom_id=custom_id, options=list(options), **kwargs)

def user_select(custom_id, **kwargs): return UserSelect(custom_id, **kwargs)
def role_select(custom_id, **kwargs): return RoleSelect(custom_id, **kwargs)
def mentionable_select(custom_id, **kwargs): return MentionableSelect(custom_id, **kwargs)
def channel_select(custom_id, **kwargs): return ChannelSelect(custom_id, **kwargs)

def text_input(custom_id, *, style=1, label=None, min_length=None, max_length=None,
               required=True, value=None, placeholder=None):
    return TextInput(
        custom_id=custom_id, style=style, label=label, min_length=min_length,
        max_length=max_length, required=required, value=value, placeholder=placeholder,
    )

def text_display(content): return TextDisplay(str(content))
def section(components, accessory): return Section(list(components), accessory)
def thumbnail(url, *, description=None, spoiler=False):
    return Thumbnail({"url": str(url)}, description=description, spoiler=spoiler)
def media_gallery_item(url, *, description=None, spoiler=False):
    d = {"media": {"url": str(url)}, "spoiler": bool(spoiler)}
    if description is not None: d["description"] = description
    return d
def media_gallery(*items): return MediaGallery(list(items))
def file_component(attachment_name, *, spoiler=False):
    return FileComponent({"url": f"attachment://{attachment_name}"}, spoiler=spoiler)
def separator(*, divider=True, spacing=1): return Separator(divider=divider, spacing=spacing)
def container(*components, accent_color=None, spoiler=False):
    return Container(list(components), accent_color=accent_color, spoiler=spoiler)
def label(text, component, *, description=None):
    return Label(label=str(text), component=component, description=description)
def file_upload(custom_id, *, min_values=1, max_values=1, required=True):
    return FileUpload(custom_id=custom_id, min_values=min_values, max_values=max_values, required=required)

def radio_option(label, value, *, description=None, emoji=None, default=False):
    d = {"label": label, "value": str(value), "default": bool(default)}
    if description is not None: d["description"] = description
    if emoji is not None: d["emoji"] = emoji
    return d

def radio_group(custom_id, options, *, required=True):
    return RadioGroup(custom_id=custom_id, options=list(options), required=required)

def checkbox_option(label, value, *, description=None, default=False):
    d = {"label": label, "value": str(value), "default": bool(default)}
    if description is not None: d["description"] = description
    return d

def checkbox_group(custom_id, options, *, min_values=1, max_values=None, required=True):
    return CheckboxGroup(
        custom_id=custom_id, options=list(options), min_values=min_values,
        max_values=max_values, required=required,
    )

def checkbox(custom_id, label_text, *, description=None, required=True):
    return Checkbox(custom_id=custom_id, label=label_text, description=description, required=required)

def component_tree_count(component) -> int:
    if hasattr(component, "to_dict"):
        component = component.to_dict()
    if not isinstance(component, dict):
        return 0
    count = 1
    children = component.get("components") or []
    for child in children:
        count += component_tree_count(child)
    nested = component.get("component")
    if nested is not None:
        count += component_tree_count(nested)
    return count

def component_custom_ids(component) -> list[str]:
    if hasattr(component, "to_dict"):
        component = component.to_dict()
    found = []
    def walk(x):
        if not isinstance(x, dict): return
        if x.get("custom_id") is not None:
            found.append(str(x["custom_id"]))
        for child in x.get("components") or []:
            walk(child)
        if x.get("component") is not None:
            walk(x["component"])
    walk(component)
    return found

def validate_custom_id(custom_id: str) -> bool:
    n = len(str(custom_id))
    if not 1 <= n <= 100:
        raise ValueError("custom_id must be 1..100 characters")
    return True

def validate_component_custom_ids(component) -> bool:
    ids = component_custom_ids(component)
    for value in ids:
        validate_custom_id(value)
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate custom_id found in component tree")
    return True


# ---------------------------------------------------------------------------
# Webhook helpers
# ---------------------------------------------------------------------------

def parse_webhook_url(url: str) -> tuple[str, str]:
    m = WEBHOOK_RE.search(str(url))
    if not m:
        raise ValueError("invalid Discord webhook URL")
    return m.group(1), m.group(2)

def build_webhook_url(webhook_id, token) -> str:
    return f"https://discord.com/api/webhooks/{int(webhook_id)}/{token}"

def is_webhook_url(url: str) -> bool:
    return WEBHOOK_RE.search(str(url)) is not None

def webhook_execute_params(*, wait=False, thread_id=None, with_components=False):
    d = {"wait": int(bool(wait)), "with_components": int(bool(with_components))}
    if thread_id is not None: d["thread_id"] = str(thread_id)
    return d

def webhook_message_path(webhook_id, token, message_id):
    return f"/webhooks/{webhook_id}/{token}/messages/{message_id}"

def original_interaction_path(application_id, token):
    return f"/webhooks/{application_id}/{token}/messages/@original"


# ---------------------------------------------------------------------------
# CDN helpers
# ---------------------------------------------------------------------------

def _animated_ext(hash_value, preferred=None):
    if preferred: return preferred
    return "gif" if str(hash_value).startswith("a_") else "png"

def user_avatar_url(user_id, avatar_hash, *, size=1024, extension=None):
    return f"{CDN}/avatars/{user_id}/{avatar_hash}.{_animated_ext(avatar_hash, extension)}?size={int(size)}"

def default_user_avatar_url(index):
    return f"{CDN}/embed/avatars/{int(index) % 6}.png"

def guild_icon_url(guild_id, icon_hash, *, size=1024, extension=None):
    return f"{CDN}/icons/{guild_id}/{icon_hash}.{_animated_ext(icon_hash, extension)}?size={int(size)}"

def guild_splash_url(guild_id, splash_hash, *, size=1024, extension="png"):
    return f"{CDN}/splashes/{guild_id}/{splash_hash}.{extension}?size={int(size)}"

def guild_discovery_splash_url(guild_id, splash_hash, *, size=1024, extension="png"):
    return f"{CDN}/discovery-splashes/{guild_id}/{splash_hash}.{extension}?size={int(size)}"

def guild_banner_url(guild_id, banner_hash, *, size=1024, extension=None):
    return f"{CDN}/banners/{guild_id}/{banner_hash}.{_animated_ext(banner_hash, extension)}?size={int(size)}"

def user_banner_url(user_id, banner_hash, *, size=1024, extension=None):
    return f"{CDN}/banners/{user_id}/{banner_hash}.{_animated_ext(banner_hash, extension)}?size={int(size)}"

def role_icon_url(role_id, icon_hash, *, size=256, extension="png"):
    return f"{CDN}/role-icons/{role_id}/{icon_hash}.{extension}?size={int(size)}"

def application_icon_url(application_id, icon_hash, *, size=1024, extension="png"):
    return f"{CDN}/app-icons/{application_id}/{icon_hash}.{extension}?size={int(size)}"

def application_cover_url(application_id, cover_hash, *, size=1024, extension="png"):
    return f"{CDN}/app-assets/{application_id}/store/{cover_hash}.{extension}?size={int(size)}"

def application_asset_url(application_id, asset_id, *, size=1024, extension="png"):
    return f"{CDN}/app-assets/{application_id}/{asset_id}.{extension}?size={int(size)}"

def emoji_cdn_url(emoji_id, *, animated=False, size=128):
    return f"{CDN}/emojis/{emoji_id}.{'gif' if animated else 'png'}?size={int(size)}"

def sticker_cdn_url(sticker_id, *, extension="png"):
    return f"{CDN}/stickers/{sticker_id}.{extension}"

def scheduled_event_cover_url(event_id, image_hash, *, size=1024, extension="png"):
    return f"{CDN}/guild-events/{event_id}/{image_hash}.{extension}?size={int(size)}"

def avatar_decoration_url(asset_hash, *, size=96):
    return f"{CDN}/avatar-decoration-presets/{asset_hash}.png?size={int(size)}"


# ---------------------------------------------------------------------------
# Route discovery / introspection
# ---------------------------------------------------------------------------

def list_route_names() -> list[str]:
    return sorted(OFFICIAL_ROUTES)

def route_exists(name: str) -> bool:
    return name in OFFICIAL_ROUTES

def route_spec(name: str) -> dict[str, Any]:
    spec = get_route(name)
    return {"method": spec.method, "path": spec.path, "auth": spec.auth, "source": spec.source}

def find_routes(text: str) -> list[str]:
    q = text.lower()
    return sorted(
        name for name, spec in OFFICIAL_ROUTES.items()
        if q in name.lower() or q in spec.path.lower() or q in spec.method.lower()
    )

def routes_by_method(method: str) -> list[str]:
    method = method.upper()
    return sorted(name for name, spec in OFFICIAL_ROUTES.items() if spec.method == method)

def routes_by_prefix(prefix: str) -> list[str]:
    return sorted(name for name, spec in OFFICIAL_ROUTES.items() if spec.path.startswith(prefix))

def route_methods() -> dict[str, int]:
    out = {}
    for spec in OFFICIAL_ROUTES.values():
        out[spec.method] = out.get(spec.method, 0) + 1
    return dict(sorted(out.items()))

def route_prefix_stats() -> dict[str, int]:
    out = {}
    for spec in OFFICIAL_ROUTES.values():
        parts = [p for p in spec.path.split("/") if p]
        key = parts[0] if parts else "/"
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))

def route_catalog() -> list[dict[str, Any]]:
    return [{"name": name, **route_spec(name)} for name in list_route_names()]


# ---------------------------------------------------------------------------
# Interaction payload helpers
# ---------------------------------------------------------------------------

def interaction_type(payload): return int(payload.get("type", 0))
def interaction_id(payload): return payload.get("id")
def interaction_token(payload): return payload.get("token")
def interaction_application_id(payload): return payload.get("application_id")
def interaction_guild_id(payload): return payload.get("guild_id")
def interaction_channel_id(payload): return payload.get("channel_id")

def interaction_user(payload):
    member = payload.get("member") or {}
    return member.get("user") or payload.get("user")

def interaction_user_id(payload):
    user = interaction_user(payload) or {}
    return user.get("id")

def interaction_data(payload):
    return payload.get("data") or {}

def interaction_command_name(payload):
    return interaction_data(payload).get("name")

def interaction_command_type(payload):
    return interaction_data(payload).get("type")

def interaction_custom_id(payload):
    return interaction_data(payload).get("custom_id")

def interaction_values(payload):
    return list(interaction_data(payload).get("values") or [])

def interaction_options(payload):
    return list(interaction_data(payload).get("options") or [])

def flatten_command_options(payload):
    out = {}
    def walk(items):
        for item in items or []:
            if "value" in item:
                out[item["name"]] = item["value"]
            walk(item.get("options"))
    walk(interaction_options(payload))
    return out

def interaction_option(payload, name, default=None):
    return flatten_command_options(payload).get(name, default)

def interaction_resolved(payload):
    return interaction_data(payload).get("resolved") or {}

def interaction_target_id(payload):
    return interaction_data(payload).get("target_id")

def interaction_locale(payload):
    return payload.get("locale")

def interaction_guild_locale(payload):
    return payload.get("guild_locale")

def interaction_is_ping(payload): return interaction_type(payload) == 1
def interaction_is_command(payload): return interaction_type(payload) == 2
def interaction_is_component(payload): return interaction_type(payload) == 3
def interaction_is_autocomplete(payload): return interaction_type(payload) == 4
def interaction_is_modal_submit(payload): return interaction_type(payload) == 5


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

COMMAND_NAME_RE = re.compile(r"^[\w-]{1,32}$", re.UNICODE)

def validate_command_name(name: str) -> bool:
    if not COMMAND_NAME_RE.fullmatch(str(name)):
        raise ValueError("invalid application command name")
    return True

def validate_command_description(description: str) -> bool:
    if not 1 <= len(str(description)) <= 100:
        raise ValueError("command description must be 1..100 characters")
    return True

def validate_embed_dict(embed: Mapping[str, Any]) -> bool:
    if len(str(embed.get("title", ""))) > 256:
        raise ValueError("embed title exceeds 256 characters")
    if len(str(embed.get("description", ""))) > 4096:
        raise ValueError("embed description exceeds 4096 characters")
    if len(embed.get("fields") or []) > 25:
        raise ValueError("embed has more than 25 fields")
    return True

def validate_embeds(embeds: Iterable[Mapping[str, Any]]) -> bool:
    embeds = list(embeds)
    if len(embeds) > 10:
        raise ValueError("a message can contain at most 10 embeds")
    for embed in embeds:
        validate_embed_dict(embed.to_dict() if hasattr(embed, "to_dict") else embed)
    return True

def validate_poll_payload(poll: Mapping[str, Any]) -> bool:
    answers = poll.get("answers") or []
    if not 2 <= len(answers) <= 10:
        raise ValueError("poll must contain 2..10 answers")
    return True

def validate_webhook_username(username: str) -> bool:
    if len(str(username)) > 80:
        raise ValueError("webhook username exceeds 80 characters")
    return True

def validate_role_name(name: str) -> bool:
    if not 1 <= len(str(name)) <= 100:
        raise ValueError("role name must be 1..100 characters")
    return True

def validate_channel_name(name: str) -> bool:
    if not 1 <= len(str(name)) <= 100:
        raise ValueError("channel name must be 1..100 characters")
    return True

def validate_thread_name(name: str) -> bool:
    if not 1 <= len(str(name)) <= 100:
        raise ValueError("thread name must be 1..100 characters")
    return True

def validate_reason(reason: Optional[str]) -> bool:
    if reason is not None and len(str(reason)) > 512:
        raise ValueError("audit-log reason exceeds 512 characters")
    return True


# ---------------------------------------------------------------------------
# Guild / channel / thread / forum builders
# ---------------------------------------------------------------------------

def channel_position(channel_id, position, *, lock_permissions=None, parent_id=None):
    d = {"id": str(channel_id), "position": int(position)}
    if lock_permissions is not None: d["lock_permissions"] = bool(lock_permissions)
    if parent_id is not None: d["parent_id"] = str(parent_id)
    return d

def role_position(role_id, position):
    return {"id": str(role_id), "position": int(position)}

def forum_tag(name, *, moderated=False, emoji_id=None, emoji_name=None, tag_id=None):
    d = {"name": str(name), "moderated": bool(moderated)}
    if emoji_id is not None: d["emoji_id"] = str(emoji_id)
    if emoji_name is not None: d["emoji_name"] = emoji_name
    if tag_id is not None: d["id"] = str(tag_id)
    return d

def default_reaction(*, emoji_id=None, emoji_name=None):
    return {"emoji_id": None if emoji_id is None else str(emoji_id), "emoji_name": emoji_name}

def text_channel_payload(name, **kwargs):
    return {"name": name, "type": 0, **kwargs}

def voice_channel_payload(name, **kwargs):
    return {"name": name, "type": 2, **kwargs}

def category_channel_payload(name, **kwargs):
    return {"name": name, "type": 4, **kwargs}

def announcement_channel_payload(name, **kwargs):
    return {"name": name, "type": 5, **kwargs}

def forum_channel_payload(name, **kwargs):
    return {"name": name, "type": 15, **kwargs}

def media_channel_payload(name, **kwargs):
    return {"name": name, "type": 16, **kwargs}

def thread_payload(name, *, auto_archive_duration=1440, rate_limit_per_user=None,
                   thread_type=None, invitable=None):
    d = {"name": str(name), "auto_archive_duration": int(auto_archive_duration)}
    if rate_limit_per_user is not None: d["rate_limit_per_user"] = int(rate_limit_per_user)
    if thread_type is not None: d["type"] = int(thread_type)
    if invitable is not None: d["invitable"] = bool(invitable)
    return d

def invite_payload(*, max_age=0, max_uses=0, temporary=False, unique=True,
                   target_type=None, target_user_id=None, target_application_id=None):
    d = {
        "max_age": int(max_age), "max_uses": int(max_uses),
        "temporary": bool(temporary), "unique": bool(unique),
    }
    if target_type is not None: d["target_type"] = int(target_type)
    if target_user_id is not None: d["target_user_id"] = str(target_user_id)
    if target_application_id is not None: d["target_application_id"] = str(target_application_id)
    return d


# ---------------------------------------------------------------------------
# Scheduled event / AutoMod builders
# ---------------------------------------------------------------------------

def external_event_metadata(location):
    return {"location": str(location)}

def scheduled_event_payload(
    name, scheduled_start_time, *,
    privacy_level=2,
    entity_type=None,
    channel_id=None,
    scheduled_end_time=None,
    description=None,
    entity_metadata=None,
    image=None,
):
    d = {
        "name": str(name),
        "scheduled_start_time": scheduled_start_time.isoformat() if isinstance(scheduled_start_time, datetime) else scheduled_start_time,
        "privacy_level": int(privacy_level),
    }
    if entity_type is not None: d["entity_type"] = int(entity_type)
    if channel_id is not None: d["channel_id"] = str(channel_id)
    if scheduled_end_time is not None:
        d["scheduled_end_time"] = scheduled_end_time.isoformat() if isinstance(scheduled_end_time, datetime) else scheduled_end_time
    if description is not None: d["description"] = description
    if entity_metadata is not None: d["entity_metadata"] = entity_metadata
    if image is not None: d["image"] = image
    return d

def automod_action_block_message(*, custom_message=None):
    d = {"type": 1, "metadata": {}}
    if custom_message is not None: d["metadata"]["custom_message"] = custom_message
    return d

def automod_action_send_alert(channel_id):
    return {"type": 2, "metadata": {"channel_id": str(channel_id)}}

def automod_action_timeout(duration_seconds):
    return {"type": 3, "metadata": {"duration_seconds": int(duration_seconds)}}

def automod_keyword_trigger(*, keyword_filter=None, regex_patterns=None, allow_list=None):
    d = {}
    if keyword_filter is not None: d["keyword_filter"] = list(keyword_filter)
    if regex_patterns is not None: d["regex_patterns"] = list(regex_patterns)
    if allow_list is not None: d["allow_list"] = list(allow_list)
    return d

def automod_spam_trigger():
    return {}

def automod_mention_spam_trigger(mention_total_limit, *, mention_raid_protection_enabled=False):
    return {
        "mention_total_limit": int(mention_total_limit),
        "mention_raid_protection_enabled": bool(mention_raid_protection_enabled),
    }

def automod_rule_payload(
    name, trigger_type, actions, *,
    event_type=1,
    trigger_metadata=None,
    enabled=True,
    exempt_roles=None,
    exempt_channels=None,
):
    return {
        "name": str(name),
        "event_type": int(event_type),
        "trigger_type": int(trigger_type),
        "trigger_metadata": trigger_metadata or {},
        "actions": list(actions),
        "enabled": bool(enabled),
        "exempt_roles": [str(x) for x in (exempt_roles or [])],
        "exempt_channels": [str(x) for x in (exempt_channels or [])],
    }


# ---------------------------------------------------------------------------
# Miscellaneous object helpers
# ---------------------------------------------------------------------------

def guild_has_feature(guild: Mapping[str, Any], feature: str) -> bool:
    return str(feature) in (guild.get("features") or [])

def member_role_ids(member: Mapping[str, Any]) -> list[str]:
    return [str(x) for x in member.get("roles") or []]

def display_name(user: Mapping[str, Any]) -> str:
    return user.get("global_name") or user.get("username") or str(user.get("id", "Unknown"))

def user_tag(user: Mapping[str, Any]) -> str:
    username = user.get("username") or ""
    discriminator = user.get("discriminator")
    return f"{username}#{discriminator}" if discriminator and discriminator != "0" else username

def is_bot_user(user: Mapping[str, Any]) -> bool:
    return bool(user.get("bot"))

def is_system_user(user: Mapping[str, Any]) -> bool:
    return bool(user.get("system"))

def avatar_hash(user: Mapping[str, Any]):
    return user.get("avatar")

def guild_member_count(guild: Mapping[str, Any]) -> Optional[int]:
    value = guild.get("approximate_member_count", guild.get("member_count"))
    return None if value is None else int(value)

def guild_presence_count(guild: Mapping[str, Any]) -> Optional[int]:
    value = guild.get("approximate_presence_count")
    return None if value is None else int(value)

def channel_is_thread(channel: Mapping[str, Any]) -> bool:
    return int(channel.get("type", -1)) in {10, 11, 12}

def channel_is_text(channel: Mapping[str, Any]) -> bool:
    return int(channel.get("type", -1)) in {0, 5}

def channel_is_voice(channel: Mapping[str, Any]) -> bool:
    return int(channel.get("type", -1)) in {2, 13}

def channel_is_forum(channel: Mapping[str, Any]) -> bool:
    return int(channel.get("type", -1)) == 15

def channel_is_media(channel: Mapping[str, Any]) -> bool:
    return int(channel.get("type", -1)) == 16

def json_pretty(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)

def compact_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
