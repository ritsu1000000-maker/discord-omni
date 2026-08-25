from __future__ import annotations
from .models import GuildSnapshot
from .operations import EditPlan, Operation


_GUILD_FIELDS = {
    "name", "verification_level", "default_message_notifications",
    "explicit_content_filter", "afk_timeout", "system_channel_flags",
    "preferred_locale", "description",
}

_CHANNEL_FIELDS = {
    "name", "type", "position", "topic", "nsfw", "rate_limit_per_user",
    "bitrate", "user_limit", "parent_id", "rtc_region", "video_quality_mode",
    "default_auto_archive_duration", "default_thread_rate_limit_per_user",
    "flags",
}

_ROLE_FIELDS = {
    "name", "permissions", "color", "hoist", "icon", "unicode_emoji",
    "mentionable", "position",
}


def _changed(before, after, fields):
    out = {}
    for field in fields:
        if before.get(field) != after.get(field):
            out[field] = after.get(field)
    return out


def build_plan(current: GuildSnapshot, desired: GuildSnapshot) -> EditPlan:
    if str(current.guild_id) != str(desired.guild_id):
        raise ValueError("snapshot guild_id mismatch")

    plan = EditPlan(str(current.guild_id))

    guild_changes = _changed(current.guild, desired.guild, _GUILD_FIELDS)
    if guild_changes:
        plan.add(Operation(
            "update", "guild", str(current.guild_id),
            before=current.guild,
            after=guild_changes,
            metadata={"name": desired.guild.get("name")},
        ))

    current_channels = {str(x["id"]): x for x in current.channels if x.get("id") is not None}
    desired_channels = {str(x["id"]): x for x in desired.channels if x.get("id") is not None}

    for ch in desired.channels:
        if ch.get("id") is None:
            payload = {k: v for k, v in ch.items() if k in _CHANNEL_FIELDS and v is not None}
            plan.add(Operation(
                "create", "channel", None, after=payload,
                metadata={"name": ch.get("name"), "local_id": ch.get("_local_id")},
            ))

    for cid, before in current_channels.items():
        after = desired_channels.get(cid)
        if after is None:
            plan.add(Operation("delete", "channel", cid, before=before,
                               metadata={"name": before.get("name")}))
            continue
        changes = _changed(before, after, _CHANNEL_FIELDS)
        if changes:
            plan.add(Operation("update", "channel", cid, before=before, after=changes,
                               metadata={"name": after.get("name")}))

    current_roles = {str(x["id"]): x for x in current.roles if x.get("id") is not None}
    desired_roles = {str(x["id"]): x for x in desired.roles if x.get("id") is not None}

    for role in desired.roles:
        if role.get("id") is None:
            payload = {k: v for k, v in role.items() if k in _ROLE_FIELDS and k != "position" and v is not None}
            plan.add(Operation(
                "create", "role", None, after=payload,
                metadata={"name": role.get("name"), "local_id": role.get("_local_id")},
            ))

    for rid, before in current_roles.items():
        if rid == str(current.guild_id):
            after = desired_roles.get(rid, before)
        else:
            after = desired_roles.get(rid)

        if after is None:
            plan.add(Operation("delete", "role", rid, before=before,
                               metadata={"name": before.get("name")}))
            continue

        changes = _changed(before, after, _ROLE_FIELDS - {"position"})
        if changes:
            plan.add(Operation("update", "role", rid, before=before, after=changes,
                               metadata={"name": after.get("name")}))

        if before.get("position") != after.get("position"):
            plan.add(Operation(
                "move", "role", rid,
                before={"position": before.get("position")},
                after={"position": after.get("position")},
                metadata={"name": after.get("name")},
            ))

    return plan
