from urllib.parse import quote


class EndpointMixin:
    """High-level endpoint helpers. `_call` can be sync or async depending on client."""

    def get_current_user(self): return self._call("GET", "/users/@me")
    def get_user(self, user_id): return self._call("GET", f"/users/{user_id}")
    def get_current_application(self): return self._call("GET", "/oauth2/applications/@me")
    def get_gateway(self): return self._call("GET", "/gateway")
    def get_gateway_bot(self): return self._call("GET", "/gateway/bot")

    def get_channel(self, channel_id): return self._call("GET", f"/channels/{channel_id}")
    def modify_channel(self, channel_id, *, reason=None, **fields):
        return self._call("PATCH", f"/channels/{channel_id}", json=fields, reason=reason)
    def delete_channel(self, channel_id, *, reason=None):
        return self._call("DELETE", f"/channels/{channel_id}", reason=reason)
    def trigger_typing(self, channel_id): return self._call("POST", f"/channels/{channel_id}/typing")

    def get_messages(self, channel_id, *, limit=50, before=None, after=None, around=None):
        p = {"limit": max(1, min(int(limit), 100))}
        if before is not None: p["before"] = before
        if after is not None: p["after"] = after
        if around is not None: p["around"] = around
        return self._call("GET", f"/channels/{channel_id}/messages", params=p)

    def get_message(self, channel_id, message_id):
        return self._call("GET", f"/channels/{channel_id}/messages/{message_id}")

    def send_message(self, channel_id, content=None, **fields):
        payload = dict(fields)
        if content is not None: payload["content"] = str(content)
        return self._call("POST", f"/channels/{channel_id}/messages", json=payload)

    def send_components_v2(self, channel_id, *components, flags=0, **fields):
        payload = dict(fields)
        payload["flags"] = int(flags) | (1 << 15)
        payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        return self._call("POST", f"/channels/{channel_id}/messages", json=payload)

    def edit_message(self, channel_id, message_id, **fields):
        return self._call("PATCH", f"/channels/{channel_id}/messages/{message_id}", json=fields)
    def delete_message(self, channel_id, message_id, *, reason=None):
        return self._call("DELETE", f"/channels/{channel_id}/messages/{message_id}", reason=reason)
    def bulk_delete_messages(self, channel_id, message_ids, *, reason=None):
        return self._call("POST", f"/channels/{channel_id}/messages/bulk-delete",
                          json={"messages": [str(x) for x in message_ids]}, reason=reason)
    def crosspost_message(self, channel_id, message_id):
        return self._call("POST", f"/channels/{channel_id}/messages/{message_id}/crosspost")

    def add_reaction(self, channel_id, message_id, emoji):
        e = quote(str(emoji), safe="")
        return self._call("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/{e}/@me")
    def remove_own_reaction(self, channel_id, message_id, emoji):
        e = quote(str(emoji), safe="")
        return self._call("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{e}/@me")
    def clear_reactions(self, channel_id, message_id):
        return self._call("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions")

    def pin_message(self, channel_id, message_id, *, reason=None):
        return self._call("PUT", f"/channels/{channel_id}/messages/pins/{message_id}", reason=reason)
    def unpin_message(self, channel_id, message_id, *, reason=None):
        return self._call("DELETE", f"/channels/{channel_id}/messages/pins/{message_id}", reason=reason)
    def get_pinned_messages(self, channel_id):
        return self._call("GET", f"/channels/{channel_id}/messages/pins")

    def start_thread_from_message(self, channel_id, message_id, name, **fields):
        return self._call("POST", f"/channels/{channel_id}/messages/{message_id}/threads",
                          json={"name": name, **fields})
    def start_thread(self, channel_id, name, **fields):
        return self._call("POST", f"/channels/{channel_id}/threads", json={"name": name, **fields})
    def join_thread(self, thread_id): return self._call("PUT", f"/channels/{thread_id}/thread-members/@me")
    def leave_thread(self, thread_id): return self._call("DELETE", f"/channels/{thread_id}/thread-members/@me")
    def add_thread_member(self, thread_id, user_id):
        return self._call("PUT", f"/channels/{thread_id}/thread-members/{user_id}")
    def remove_thread_member(self, thread_id, user_id):
        return self._call("DELETE", f"/channels/{thread_id}/thread-members/{user_id}")
    def list_thread_members(self, thread_id, *, with_member=False, after=None, limit=100):
        p = {"with_member": str(bool(with_member)).lower(), "limit": max(1, min(int(limit), 100))}
        if after is not None: p["after"] = after
        return self._call("GET", f"/channels/{thread_id}/thread-members", params=p)
    def list_active_threads(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/threads/active")

    def get_guild(self, guild_id, *, with_counts=False):
        return self._call("GET", f"/guilds/{guild_id}",
                          params={"with_counts": str(bool(with_counts)).lower()})
    def get_guild_preview(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/preview")
    def modify_guild(self, guild_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}", json=fields, reason=reason)
    def get_guild_channels(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/channels")
    def create_guild_channel(self, guild_id, name, *, reason=None, **fields):
        return self._call("POST", f"/guilds/{guild_id}/channels",
                          json={"name": name, **fields}, reason=reason)

    def get_member(self, guild_id, user_id):
        return self._call("GET", f"/guilds/{guild_id}/members/{user_id}")
    def list_members(self, guild_id, *, limit=1000, after=None):
        p = {"limit": max(1, min(int(limit), 1000))}
        if after is not None: p["after"] = after
        return self._call("GET", f"/guilds/{guild_id}/members", params=p)
    def search_members(self, guild_id, query, *, limit=100):
        return self._call("GET", f"/guilds/{guild_id}/members/search",
                          params={"query": query, "limit": max(1, min(int(limit), 1000))})
    def modify_member(self, guild_id, user_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}/members/{user_id}", json=fields, reason=reason)
    def add_member_role(self, guild_id, user_id, role_id, *, reason=None):
        return self._call("PUT", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", reason=reason)
    def remove_member_role(self, guild_id, user_id, role_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", reason=reason)
    def kick_member(self, guild_id, user_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/members/{user_id}", reason=reason)

    def get_bans(self, guild_id, *, limit=1000, before=None, after=None):
        p = {"limit": max(1, min(int(limit), 1000))}
        if before is not None: p["before"] = before
        if after is not None: p["after"] = after
        return self._call("GET", f"/guilds/{guild_id}/bans", params=p)
    def get_ban(self, guild_id, user_id): return self._call("GET", f"/guilds/{guild_id}/bans/{user_id}")
    def ban_member(self, guild_id, user_id, *, delete_message_seconds=0, reason=None):
        return self._call("PUT", f"/guilds/{guild_id}/bans/{user_id}",
                          json={"delete_message_seconds": int(delete_message_seconds)}, reason=reason)
    def unban_member(self, guild_id, user_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/bans/{user_id}", reason=reason)

    def get_roles(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/roles")
    def get_role(self, guild_id, role_id): return self._call("GET", f"/guilds/{guild_id}/roles/{role_id}")
    def create_role(self, guild_id, *, reason=None, **fields):
        return self._call("POST", f"/guilds/{guild_id}/roles", json=fields, reason=reason)
    def modify_role(self, guild_id, role_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}/roles/{role_id}", json=fields, reason=reason)
    def delete_role(self, guild_id, role_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/roles/{role_id}", reason=reason)

    def create_invite(self, channel_id, *, reason=None, **fields):
        return self._call("POST", f"/channels/{channel_id}/invites", json=fields, reason=reason)
    def get_channel_invites(self, channel_id): return self._call("GET", f"/channels/{channel_id}/invites")
    def get_guild_invites(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/invites")
    def get_invite(self, code, **params): return self._call("GET", f"/invites/{code}", params=params)
    def delete_invite(self, code, *, reason=None): return self._call("DELETE", f"/invites/{code}", reason=reason)

    def create_webhook(self, channel_id, name, *, reason=None, avatar=None):
        p = {"name": name}
        if avatar is not None: p["avatar"] = avatar
        return self._call("POST", f"/channels/{channel_id}/webhooks", json=p, reason=reason)
    def get_channel_webhooks(self, channel_id): return self._call("GET", f"/channels/{channel_id}/webhooks")
    def get_guild_webhooks(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/webhooks")
    def get_webhook(self, webhook_id): return self._call("GET", f"/webhooks/{webhook_id}")
    def modify_webhook(self, webhook_id, *, reason=None, **fields):
        return self._call("PATCH", f"/webhooks/{webhook_id}", json=fields, reason=reason)
    def delete_webhook(self, webhook_id, *, reason=None):
        return self._call("DELETE", f"/webhooks/{webhook_id}", reason=reason)

    def list_guild_emojis(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/emojis")
    def get_guild_emoji(self, guild_id, emoji_id):
        return self._call("GET", f"/guilds/{guild_id}/emojis/{emoji_id}")
    def create_guild_emoji(self, guild_id, name, image_data, *, roles=None, reason=None):
        return self._call("POST", f"/guilds/{guild_id}/emojis",
                          json={"name": name, "image": image_data, "roles": roles or []}, reason=reason)
    def modify_guild_emoji(self, guild_id, emoji_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}/emojis/{emoji_id}", json=fields, reason=reason)
    def delete_guild_emoji(self, guild_id, emoji_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/emojis/{emoji_id}", reason=reason)

    def get_sticker(self, sticker_id): return self._call("GET", f"/stickers/{sticker_id}")
    def get_guild_stickers(self, guild_id): return self._call("GET", f"/guilds/{guild_id}/stickers")
    def get_guild_sticker(self, guild_id, sticker_id):
        return self._call("GET", f"/guilds/{guild_id}/stickers/{sticker_id}")
    def modify_guild_sticker(self, guild_id, sticker_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}/stickers/{sticker_id}", json=fields, reason=reason)
    def delete_guild_sticker(self, guild_id, sticker_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/stickers/{sticker_id}", reason=reason)

    def list_scheduled_events(self, guild_id, *, with_user_count=False):
        return self._call("GET", f"/guilds/{guild_id}/scheduled-events",
                          params={"with_user_count": str(bool(with_user_count)).lower()})
    def get_scheduled_event(self, guild_id, event_id, *, with_user_count=False):
        return self._call("GET", f"/guilds/{guild_id}/scheduled-events/{event_id}",
                          params={"with_user_count": str(bool(with_user_count)).lower()})
    def create_scheduled_event(self, guild_id, *, reason=None, **fields):
        return self._call("POST", f"/guilds/{guild_id}/scheduled-events", json=fields, reason=reason)
    def modify_scheduled_event(self, guild_id, event_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}/scheduled-events/{event_id}",
                          json=fields, reason=reason)
    def delete_scheduled_event(self, guild_id, event_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/scheduled-events/{event_id}", reason=reason)

    def list_automod_rules(self, guild_id):
        return self._call("GET", f"/guilds/{guild_id}/auto-moderation/rules")
    def get_automod_rule(self, guild_id, rule_id):
        return self._call("GET", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}")
    def create_automod_rule(self, guild_id, *, reason=None, **fields):
        return self._call("POST", f"/guilds/{guild_id}/auto-moderation/rules", json=fields, reason=reason)
    def modify_automod_rule(self, guild_id, rule_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
                          json=fields, reason=reason)
    def delete_automod_rule(self, guild_id, rule_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}", reason=reason)

    def get_global_commands(self, application_id, *, with_localizations=False):
        return self._call("GET", f"/applications/{application_id}/commands",
                          params={"with_localizations": str(bool(with_localizations)).lower()})
    def create_global_command(self, application_id, **command):
        return self._call("POST", f"/applications/{application_id}/commands", json=command)
    def edit_global_command(self, application_id, command_id, **command):
        return self._call("PATCH", f"/applications/{application_id}/commands/{command_id}", json=command)
    def delete_global_command(self, application_id, command_id):
        return self._call("DELETE", f"/applications/{application_id}/commands/{command_id}")
    def bulk_overwrite_global_commands(self, application_id, commands):
        return self._call("PUT", f"/applications/{application_id}/commands", json=commands)

    def get_guild_commands(self, application_id, guild_id, *, with_localizations=False):
        return self._call("GET", f"/applications/{application_id}/guilds/{guild_id}/commands",
                          params={"with_localizations": str(bool(with_localizations)).lower()})
    def create_guild_command(self, application_id, guild_id, **command):
        return self._call("POST", f"/applications/{application_id}/guilds/{guild_id}/commands", json=command)
    def edit_guild_command(self, application_id, guild_id, command_id, **command):
        return self._call("PATCH", f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                          json=command)
    def delete_guild_command(self, application_id, guild_id, command_id):
        return self._call("DELETE", f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}")
    def bulk_overwrite_guild_commands(self, application_id, guild_id, commands):
        return self._call("PUT", f"/applications/{application_id}/guilds/{guild_id}/commands", json=commands)

    def end_poll(self, channel_id, message_id):
        return self._call("POST", f"/channels/{channel_id}/polls/{message_id}/expire")

    def create_stage_instance(self, channel_id, topic, *, reason=None, **fields):
        return self._call("POST", "/stage-instances",
                          json={"channel_id": str(channel_id), "topic": topic, **fields}, reason=reason)
    def get_stage_instance(self, channel_id):
        return self._call("GET", f"/stage-instances/{channel_id}")
    def modify_stage_instance(self, channel_id, *, reason=None, **fields):
        return self._call("PATCH", f"/stage-instances/{channel_id}", json=fields, reason=reason)
    def delete_stage_instance(self, channel_id, *, reason=None):
        return self._call("DELETE", f"/stage-instances/{channel_id}", reason=reason)

    # Monetization / SKUs / Entitlements / Subscriptions
    def get_skus(self, application_id):
        return self._call("GET", f"/applications/{application_id}/skus")
    def get_entitlements(self, application_id, **params):
        return self._call("GET", f"/applications/{application_id}/entitlements", params=params)
    def create_test_entitlement(self, application_id, sku_id, owner_id, owner_type):
        return self._call("POST", f"/applications/{application_id}/entitlements",
                          json={"sku_id": str(sku_id), "owner_id": str(owner_id), "owner_type": int(owner_type)})
    def delete_test_entitlement(self, application_id, entitlement_id):
        return self._call("DELETE", f"/applications/{application_id}/entitlements/{entitlement_id}")
    def consume_entitlement(self, application_id, entitlement_id):
        return self._call("POST", f"/applications/{application_id}/entitlements/{entitlement_id}/consume")
    def list_sku_subscriptions(self, sku_id, **params):
        return self._call("GET", f"/skus/{sku_id}/subscriptions", params=params)
    def get_sku_subscription(self, sku_id, subscription_id):
        return self._call("GET", f"/skus/{sku_id}/subscriptions/{subscription_id}")

    # Soundboard
    def get_default_soundboard_sounds(self):
        return self._call("GET", "/soundboard-default-sounds")
    def get_guild_soundboard_sounds(self, guild_id):
        return self._call("GET", f"/guilds/{guild_id}/soundboard-sounds")
    def create_guild_soundboard_sound(self, guild_id, *, reason=None, **fields):
        return self._call("POST", f"/guilds/{guild_id}/soundboard-sounds", json=fields, reason=reason)
    def modify_guild_soundboard_sound(self, guild_id, sound_id, *, reason=None, **fields):
        return self._call("PATCH", f"/guilds/{guild_id}/soundboard-sounds/{sound_id}",
                          json=fields, reason=reason)
    def delete_guild_soundboard_sound(self, guild_id, sound_id, *, reason=None):
        return self._call("DELETE", f"/guilds/{guild_id}/soundboard-sounds/{sound_id}", reason=reason)


# ---------- Additional official discord.py routes (0.6.0) ----------

def get_current_user_guilds(self, *, limit=100, before=None, after=None, with_counts=True):
    p = {"limit": int(limit), "with_counts": int(bool(with_counts))}
    if before is not None: p["before"] = before
    if after is not None: p["after"] = after
    return self._call("GET", "/users/@me/guilds", params=p)

def leave_guild(self, guild_id):
    return self._call("DELETE", f"/users/@me/guilds/{guild_id}")

def edit_current_user(self, **fields):
    return self._call("PATCH", "/users/@me", json=fields)

def create_dm(self, user_id):
    return self._call("POST", "/users/@me/channels", json={"recipient_id": str(user_id)})

def create_guild(self, name, *, icon=None):
    p = {"name": name}
    if icon is not None: p["icon"] = icon
    return self._call("POST", "/guilds", json=p)

def delete_guild(self, guild_id):
    return self._call("DELETE", f"/guilds/{guild_id}")

def modify_guild_mfa_level(self, guild_id, level, *, reason=None):
    return self._call("POST", f"/guilds/{guild_id}/mfa", json={"level": int(level)}, reason=reason)

def get_guild_vanity_url(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/vanity-url")

def modify_guild_vanity_url(self, guild_id, code, *, reason=None):
    return self._call("PATCH", f"/guilds/{guild_id}/vanity-url", json={"code": code}, reason=reason)

def get_guild_widget(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/widget.json")

def modify_guild_widget(self, guild_id, *, reason=None, **fields):
    return self._call("PATCH", f"/guilds/{guild_id}/widget", json=fields, reason=reason)

def modify_incident_actions(self, guild_id, **fields):
    return self._call("PUT", f"/guilds/{guild_id}/incident-actions", json=fields)

def get_audit_log(self, guild_id, *, limit=100, before=None, after=None, user_id=None, action_type=None):
    p = {"limit": int(limit)}
    if before is not None: p["before"] = before
    if after is not None: p["after"] = after
    if user_id is not None: p["user_id"] = user_id
    if action_type is not None: p["action_type"] = action_type
    return self._call("GET", f"/guilds/{guild_id}/audit-logs", params=p)

def bulk_ban(self, guild_id, user_ids, *, delete_message_seconds=86400, reason=None):
    return self._call(
        "POST", f"/guilds/{guild_id}/bulk-ban",
        json={"user_ids": [str(x) for x in user_ids], "delete_message_seconds": int(delete_message_seconds)},
        reason=reason,
    )

def get_prune_count(self, guild_id, *, days=7, include_roles=None):
    p = {"days": int(days)}
    if include_roles: p["include_roles"] = ", ".join(map(str, include_roles))
    return self._call("GET", f"/guilds/{guild_id}/prune", params=p)

def begin_prune(self, guild_id, *, days=7, compute_prune_count=True, include_roles=None, reason=None):
    p = {"days": int(days), "compute_prune_count": bool(compute_prune_count)}
    if include_roles: p["include_roles"] = ", ".join(map(str, include_roles))
    return self._call("POST", f"/guilds/{guild_id}/prune", json=p, reason=reason)

def get_current_voice_state(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/voice-states/@me")

def modify_current_voice_state(self, guild_id, **fields):
    return self._call("PATCH", f"/guilds/{guild_id}/voice-states/@me", json=fields)

def get_voice_state(self, guild_id, user_id):
    return self._call("GET", f"/guilds/{guild_id}/voice-states/{user_id}")

def modify_voice_state(self, guild_id, user_id, **fields):
    return self._call("PATCH", f"/guilds/{guild_id}/voice-states/{user_id}", json=fields)

def edit_voice_channel_status(self, channel_id, status=None, *, reason=None):
    return self._call("PUT", f"/channels/{channel_id}/voice-status", json={"status": status}, reason=reason)

def get_role_member_counts(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/roles/member-counts")

def list_public_archived_threads(self, channel_id, *, before=None, limit=50):
    p = {"limit": int(limit)}
    if before is not None: p["before"] = before
    return self._call("GET", f"/channels/{channel_id}/threads/archived/public", params=p)

def list_private_archived_threads(self, channel_id, *, before=None, limit=50):
    p = {"limit": int(limit)}
    if before is not None: p["before"] = before
    return self._call("GET", f"/channels/{channel_id}/threads/archived/private", params=p)

def list_joined_private_archived_threads(self, channel_id, *, before=None, limit=50):
    p = {"limit": int(limit)}
    if before is not None: p["before"] = before
    return self._call("GET", f"/channels/{channel_id}/users/@me/threads/archived/private", params=p)

def get_template(self, template_code):
    return self._call("GET", f"/guilds/templates/{template_code}")

def create_guild_from_template(self, template_code, name, *, icon=None):
    p = {"name": name}
    if icon is not None: p["icon"] = icon
    return self._call("POST", f"/guilds/templates/{template_code}", json=p)

def get_guild_templates(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/templates")

def create_guild_template(self, guild_id, name, *, description=None):
    p = {"name": name}
    if description is not None: p["description"] = description
    return self._call("POST", f"/guilds/{guild_id}/templates", json=p)

def sync_guild_template(self, guild_id, template_code):
    return self._call("PUT", f"/guilds/{guild_id}/templates/{template_code}")

def modify_guild_template(self, guild_id, template_code, **fields):
    return self._call("PATCH", f"/guilds/{guild_id}/templates/{template_code}", json=fields)

def delete_guild_template(self, guild_id, template_code):
    return self._call("DELETE", f"/guilds/{guild_id}/templates/{template_code}")

def get_welcome_screen(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/welcome-screen")

def modify_welcome_screen(self, guild_id, *, reason=None, **fields):
    return self._call("PATCH", f"/guilds/{guild_id}/welcome-screen", json=fields, reason=reason)

def get_guild_onboarding(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/onboarding")

def modify_guild_onboarding(self, guild_id, *, reason=None, **fields):
    return self._call("PUT", f"/guilds/{guild_id}/onboarding", json=fields, reason=reason)

def get_guild_integrations(self, guild_id):
    return self._call("GET", f"/guilds/{guild_id}/integrations")

def create_guild_integration(self, guild_id, integration_type, integration_id):
    return self._call("POST", f"/guilds/{guild_id}/integrations",
                      json={"type": integration_type, "id": integration_id})

def modify_guild_integration(self, guild_id, integration_id, **fields):
    return self._call("PATCH", f"/guilds/{guild_id}/integrations/{integration_id}", json=fields)

def sync_guild_integration(self, guild_id, integration_id):
    return self._call("POST", f"/guilds/{guild_id}/integrations/{integration_id}/sync")

def delete_guild_integration(self, guild_id, integration_id, *, reason=None):
    return self._call("DELETE", f"/guilds/{guild_id}/integrations/{integration_id}", reason=reason)

def get_sticker_pack(self, sticker_pack_id):
    return self._call("GET", f"/sticker-packs/{sticker_pack_id}")

def list_sticker_packs(self):
    return self._call("GET", "/sticker-packs")

def get_global_command(self, application_id, command_id):
    return self._call("GET", f"/applications/{application_id}/commands/{command_id}")

def get_guild_command(self, application_id, guild_id, command_id):
    return self._call("GET", f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}")

def get_guild_command_permissions(self, application_id, guild_id):
    return self._call("GET", f"/applications/{application_id}/guilds/{guild_id}/commands/permissions")

def get_command_permissions(self, application_id, guild_id, command_id):
    return self._call("GET", f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions")

def edit_command_permissions(self, application_id, guild_id, command_id, permissions):
    return self._call(
        "PUT", f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
        json={"permissions": permissions},
    )

def list_application_emojis(self, application_id):
    return self._call("GET", f"/applications/{application_id}/emojis")

def get_application_emoji(self, application_id, emoji_id):
    return self._call("GET", f"/applications/{application_id}/emojis/{emoji_id}")

def create_application_emoji(self, application_id, name, image):
    return self._call("POST", f"/applications/{application_id}/emojis", json={"name": name, "image": image})

def modify_application_emoji(self, application_id, emoji_id, **fields):
    return self._call("PATCH", f"/applications/{application_id}/emojis/{emoji_id}", json=fields)

def delete_application_emoji(self, application_id, emoji_id):
    return self._call("DELETE", f"/applications/{application_id}/emojis/{emoji_id}")

def list_scheduled_event_users(self, guild_id, event_id, *, limit=100, with_member=False, before=None, after=None):
    p = {"limit": int(limit), "with_member": int(bool(with_member))}
    if before is not None: p["before"] = before
    if after is not None: p["after"] = after
    return self._call("GET", f"/guilds/{guild_id}/scheduled-events/{event_id}/users", params=p)

def get_entitlement(self, application_id, entitlement_id):
    return self._call("GET", f"/applications/{application_id}/entitlements/{entitlement_id}")

def get_poll_answer_voters(self, channel_id, message_id, answer_id, *, after=None, limit=None):
    p = {}
    if after is not None: p["after"] = after
    if limit is not None: p["limit"] = int(limit)
    return self._call("GET", f"/channels/{channel_id}/polls/{message_id}/answers/{answer_id}", params=p)

def send_soundboard_sound(self, channel_id, sound_id, *, source_guild_id=None):
    p = {"sound_id": str(sound_id)}
    if source_guild_id is not None: p["source_guild_id"] = str(source_guild_id)
    return self._call("POST", f"/channels/{channel_id}/send-soundboard-sound", json=p)

def get_gateway(self):
    return self._call("GET", "/gateway")

def get_gateway_bot(self):
    return self._call("GET", "/gateway/bot")
