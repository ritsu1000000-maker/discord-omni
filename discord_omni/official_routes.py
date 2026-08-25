from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True, slots=True)
class RouteSpec:
    method: str
    path: str
    auth: bool = True
    source: str = "discord.py"

# Public Discord API routes mirrored from the route usage in
# Rapptz/discord.py (master), primarily discord/http.py and
# discord/webhook/async_.py.  No private client/self-bot endpoints are added.
OFFICIAL_ROUTES: Mapping[str, RouteSpec] = {
    # Gateway / application / users
    "get_gateway": RouteSpec("GET", "/gateway"),
    "get_gateway_bot": RouteSpec("GET", "/gateway/bot"),
    "get_current_user": RouteSpec("GET", "/users/@me"),
    "edit_current_user": RouteSpec("PATCH", "/users/@me"),
    "get_user": RouteSpec("GET", "/users/{user_id}"),
    "create_dm": RouteSpec("POST", "/users/@me/channels"),
    "get_current_user_guilds": RouteSpec("GET", "/users/@me/guilds"),
    "leave_guild": RouteSpec("DELETE", "/users/@me/guilds/{guild_id}"),
    "get_current_application": RouteSpec("GET", "/oauth2/applications/@me"),
    "edit_current_application": RouteSpec("PATCH", "/applications/@me"),

    # Messages / channels
    "get_channel": RouteSpec("GET", "/channels/{channel_id}"),
    "modify_channel": RouteSpec("PATCH", "/channels/{channel_id}"),
    "delete_channel": RouteSpec("DELETE", "/channels/{channel_id}"),
    "get_messages": RouteSpec("GET", "/channels/{channel_id}/messages"),
    "get_message": RouteSpec("GET", "/channels/{channel_id}/messages/{message_id}"),
    "create_message": RouteSpec("POST", "/channels/{channel_id}/messages"),
    "edit_message": RouteSpec("PATCH", "/channels/{channel_id}/messages/{message_id}"),
    "delete_message": RouteSpec("DELETE", "/channels/{channel_id}/messages/{message_id}"),
    "bulk_delete_messages": RouteSpec("POST", "/channels/{channel_id}/messages/bulk-delete"),
    "crosspost_message": RouteSpec("POST", "/channels/{channel_id}/messages/{message_id}/crosspost"),
    "trigger_typing": RouteSpec("POST", "/channels/{channel_id}/typing"),
    "pin_message": RouteSpec("PUT", "/channels/{channel_id}/messages/pins/{message_id}"),
    "unpin_message": RouteSpec("DELETE", "/channels/{channel_id}/messages/pins/{message_id}"),
    "get_pins": RouteSpec("GET", "/channels/{channel_id}/messages/pins"),
    "edit_voice_channel_status": RouteSpec("PUT", "/channels/{channel_id}/voice-status"),
    "follow_announcement_channel": RouteSpec("POST", "/channels/{channel_id}/followers"),

    # Reactions
    "add_reaction": RouteSpec("PUT", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"),
    "remove_own_reaction": RouteSpec("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"),
    "remove_user_reaction": RouteSpec("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}"),
    "get_reactions": RouteSpec("GET", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}"),
    "clear_reactions": RouteSpec("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions"),
    "clear_emoji_reactions": RouteSpec("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}"),

    # Channel permission overwrites
    "edit_channel_permissions": RouteSpec("PUT", "/channels/{channel_id}/permissions/{target_id}"),
    "delete_channel_permissions": RouteSpec("DELETE", "/channels/{channel_id}/permissions/{target_id}"),

    # Threads
    "start_thread_from_message": RouteSpec("POST", "/channels/{channel_id}/messages/{message_id}/threads"),
    "start_thread": RouteSpec("POST", "/channels/{channel_id}/threads"),
    "join_thread": RouteSpec("PUT", "/channels/{channel_id}/thread-members/@me"),
    "leave_thread": RouteSpec("DELETE", "/channels/{channel_id}/thread-members/@me"),
    "add_thread_member": RouteSpec("PUT", "/channels/{channel_id}/thread-members/{user_id}"),
    "remove_thread_member": RouteSpec("DELETE", "/channels/{channel_id}/thread-members/{user_id}"),
    "get_thread_member": RouteSpec("GET", "/channels/{channel_id}/thread-members/{user_id}"),
    "list_thread_members": RouteSpec("GET", "/channels/{channel_id}/thread-members"),
    "list_public_archived_threads": RouteSpec("GET", "/channels/{channel_id}/threads/archived/public"),
    "list_private_archived_threads": RouteSpec("GET", "/channels/{channel_id}/threads/archived/private"),
    "list_joined_private_archived_threads": RouteSpec("GET", "/channels/{channel_id}/users/@me/threads/archived/private"),
    "list_active_guild_threads": RouteSpec("GET", "/guilds/{guild_id}/threads/active"),

    # Guilds
    "create_guild": RouteSpec("POST", "/guilds"),
    "get_guild": RouteSpec("GET", "/guilds/{guild_id}"),
    "get_guild_preview": RouteSpec("GET", "/guilds/{guild_id}/preview"),
    "modify_guild": RouteSpec("PATCH", "/guilds/{guild_id}"),
    "delete_guild": RouteSpec("DELETE", "/guilds/{guild_id}"),
    "modify_guild_mfa_level": RouteSpec("POST", "/guilds/{guild_id}/mfa"),
    "get_guild_channels": RouteSpec("GET", "/guilds/{guild_id}/channels"),
    "create_guild_channel": RouteSpec("POST", "/guilds/{guild_id}/channels"),
    "modify_guild_channel_positions": RouteSpec("PATCH", "/guilds/{guild_id}/channels"),
    "get_guild_vanity_url": RouteSpec("GET", "/guilds/{guild_id}/vanity-url"),
    "modify_guild_vanity_url": RouteSpec("PATCH", "/guilds/{guild_id}/vanity-url"),
    "get_guild_widget": RouteSpec("GET", "/guilds/{guild_id}/widget.json"),
    "modify_guild_widget": RouteSpec("PATCH", "/guilds/{guild_id}/widget"),
    "modify_incident_actions": RouteSpec("PUT", "/guilds/{guild_id}/incident-actions"),
    "get_audit_log": RouteSpec("GET", "/guilds/{guild_id}/audit-logs"),

    # Members / bans / prune / voice state
    "list_members": RouteSpec("GET", "/guilds/{guild_id}/members"),
    "get_member": RouteSpec("GET", "/guilds/{guild_id}/members/{user_id}"),
    "modify_member": RouteSpec("PATCH", "/guilds/{guild_id}/members/{user_id}"),
    "modify_current_member": RouteSpec("PATCH", "/guilds/{guild_id}/members/@me"),
    "remove_member": RouteSpec("DELETE", "/guilds/{guild_id}/members/{user_id}"),
    "add_member_role": RouteSpec("PUT", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}"),
    "remove_member_role": RouteSpec("DELETE", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}"),
    "list_bans": RouteSpec("GET", "/guilds/{guild_id}/bans"),
    "get_ban": RouteSpec("GET", "/guilds/{guild_id}/bans/{user_id}"),
    "create_ban": RouteSpec("PUT", "/guilds/{guild_id}/bans/{user_id}"),
    "remove_ban": RouteSpec("DELETE", "/guilds/{guild_id}/bans/{user_id}"),
    "bulk_ban": RouteSpec("POST", "/guilds/{guild_id}/bulk-ban"),
    "begin_prune": RouteSpec("POST", "/guilds/{guild_id}/prune"),
    "get_prune_count": RouteSpec("GET", "/guilds/{guild_id}/prune"),
    "get_current_voice_state": RouteSpec("GET", "/guilds/{guild_id}/voice-states/@me"),
    "modify_current_voice_state": RouteSpec("PATCH", "/guilds/{guild_id}/voice-states/@me"),
    "get_voice_state": RouteSpec("GET", "/guilds/{guild_id}/voice-states/{user_id}"),
    "modify_voice_state": RouteSpec("PATCH", "/guilds/{guild_id}/voice-states/{user_id}"),

    # Roles
    "list_roles": RouteSpec("GET", "/guilds/{guild_id}/roles"),
    "get_role": RouteSpec("GET", "/guilds/{guild_id}/roles/{role_id}"),
    "get_role_member_counts": RouteSpec("GET", "/guilds/{guild_id}/roles/member-counts"),
    "create_role": RouteSpec("POST", "/guilds/{guild_id}/roles"),
    "modify_role_positions": RouteSpec("PATCH", "/guilds/{guild_id}/roles"),
    "modify_role": RouteSpec("PATCH", "/guilds/{guild_id}/roles/{role_id}"),
    "delete_role": RouteSpec("DELETE", "/guilds/{guild_id}/roles/{role_id}"),

    # Invites
    "create_invite": RouteSpec("POST", "/channels/{channel_id}/invites"),
    "get_channel_invites": RouteSpec("GET", "/channels/{channel_id}/invites"),
    "get_guild_invites": RouteSpec("GET", "/guilds/{guild_id}/invites"),
    "get_invite": RouteSpec("GET", "/invites/{invite_code}"),
    "delete_invite": RouteSpec("DELETE", "/invites/{invite_code}"),

    # Guild templates
    "get_template": RouteSpec("GET", "/guilds/templates/{template_code}"),
    "create_guild_from_template": RouteSpec("POST", "/guilds/templates/{template_code}"),
    "get_guild_templates": RouteSpec("GET", "/guilds/{guild_id}/templates"),
    "create_guild_template": RouteSpec("POST", "/guilds/{guild_id}/templates"),
    "sync_guild_template": RouteSpec("PUT", "/guilds/{guild_id}/templates/{template_code}"),
    "modify_guild_template": RouteSpec("PATCH", "/guilds/{guild_id}/templates/{template_code}"),
    "delete_guild_template": RouteSpec("DELETE", "/guilds/{guild_id}/templates/{template_code}"),

    # Welcome screen / onboarding
    "get_welcome_screen": RouteSpec("GET", "/guilds/{guild_id}/welcome-screen"),
    "modify_welcome_screen": RouteSpec("PATCH", "/guilds/{guild_id}/welcome-screen"),
    "get_guild_onboarding": RouteSpec("GET", "/guilds/{guild_id}/onboarding"),
    "modify_guild_onboarding": RouteSpec("PUT", "/guilds/{guild_id}/onboarding"),

    # Integrations
    "get_guild_integrations": RouteSpec("GET", "/guilds/{guild_id}/integrations"),
    "create_guild_integration": RouteSpec("POST", "/guilds/{guild_id}/integrations"),
    "modify_guild_integration": RouteSpec("PATCH", "/guilds/{guild_id}/integrations/{integration_id}"),
    "delete_guild_integration": RouteSpec("DELETE", "/guilds/{guild_id}/integrations/{integration_id}"),
    "sync_guild_integration": RouteSpec("POST", "/guilds/{guild_id}/integrations/{integration_id}/sync"),

    # Emojis / stickers
    "list_guild_emojis": RouteSpec("GET", "/guilds/{guild_id}/emojis"),
    "get_guild_emoji": RouteSpec("GET", "/guilds/{guild_id}/emojis/{emoji_id}"),
    "create_guild_emoji": RouteSpec("POST", "/guilds/{guild_id}/emojis"),
    "modify_guild_emoji": RouteSpec("PATCH", "/guilds/{guild_id}/emojis/{emoji_id}"),
    "delete_guild_emoji": RouteSpec("DELETE", "/guilds/{guild_id}/emojis/{emoji_id}"),
    "get_sticker": RouteSpec("GET", "/stickers/{sticker_id}"),
    "get_sticker_pack": RouteSpec("GET", "/sticker-packs/{sticker_pack_id}"),
    "list_sticker_packs": RouteSpec("GET", "/sticker-packs"),
    "list_guild_stickers": RouteSpec("GET", "/guilds/{guild_id}/stickers"),
    "get_guild_sticker": RouteSpec("GET", "/guilds/{guild_id}/stickers/{sticker_id}"),
    "create_guild_sticker": RouteSpec("POST", "/guilds/{guild_id}/stickers"),
    "modify_guild_sticker": RouteSpec("PATCH", "/guilds/{guild_id}/stickers/{sticker_id}"),
    "delete_guild_sticker": RouteSpec("DELETE", "/guilds/{guild_id}/stickers/{sticker_id}"),

    # Webhook management
    "create_webhook": RouteSpec("POST", "/channels/{channel_id}/webhooks"),
    "get_channel_webhooks": RouteSpec("GET", "/channels/{channel_id}/webhooks"),
    "get_guild_webhooks": RouteSpec("GET", "/guilds/{guild_id}/webhooks"),
    "get_webhook": RouteSpec("GET", "/webhooks/{webhook_id}"),
    "modify_webhook": RouteSpec("PATCH", "/webhooks/{webhook_id}"),
    "delete_webhook": RouteSpec("DELETE", "/webhooks/{webhook_id}"),
    "get_webhook_with_token": RouteSpec("GET", "/webhooks/{webhook_id}/{webhook_token}", auth=False),
    "modify_webhook_with_token": RouteSpec("PATCH", "/webhooks/{webhook_id}/{webhook_token}", auth=False),
    "delete_webhook_with_token": RouteSpec("DELETE", "/webhooks/{webhook_id}/{webhook_token}", auth=False),
    "execute_webhook": RouteSpec("POST", "/webhooks/{webhook_id}/{webhook_token}", auth=False),
    "get_webhook_message": RouteSpec("GET", "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", auth=False),
    "edit_webhook_message": RouteSpec("PATCH", "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", auth=False),
    "delete_webhook_message": RouteSpec("DELETE", "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", auth=False),

    # Interaction callback / followups
    "create_interaction_response": RouteSpec("POST", "/interactions/{interaction_id}/{interaction_token}/callback", auth=False),
    "get_original_interaction_response": RouteSpec("GET", "/webhooks/{application_id}/{interaction_token}/messages/@original", auth=False),
    "edit_original_interaction_response": RouteSpec("PATCH", "/webhooks/{application_id}/{interaction_token}/messages/@original", auth=False),
    "delete_original_interaction_response": RouteSpec("DELETE", "/webhooks/{application_id}/{interaction_token}/messages/@original", auth=False),

    # Application commands
    "list_global_commands": RouteSpec("GET", "/applications/{application_id}/commands"),
    "get_global_command": RouteSpec("GET", "/applications/{application_id}/commands/{command_id}"),
    "create_global_command": RouteSpec("POST", "/applications/{application_id}/commands"),
    "modify_global_command": RouteSpec("PATCH", "/applications/{application_id}/commands/{command_id}"),
    "delete_global_command": RouteSpec("DELETE", "/applications/{application_id}/commands/{command_id}"),
    "bulk_overwrite_global_commands": RouteSpec("PUT", "/applications/{application_id}/commands"),
    "list_guild_commands": RouteSpec("GET", "/applications/{application_id}/guilds/{guild_id}/commands"),
    "get_guild_command": RouteSpec("GET", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}"),
    "create_guild_command": RouteSpec("POST", "/applications/{application_id}/guilds/{guild_id}/commands"),
    "modify_guild_command": RouteSpec("PATCH", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}"),
    "delete_guild_command": RouteSpec("DELETE", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}"),
    "bulk_overwrite_guild_commands": RouteSpec("PUT", "/applications/{application_id}/guilds/{guild_id}/commands"),
    "get_guild_command_permissions": RouteSpec("GET", "/applications/{application_id}/guilds/{guild_id}/commands/permissions"),
    "get_command_permissions": RouteSpec("GET", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions"),
    "edit_command_permissions": RouteSpec("PUT", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions"),

    # Application emojis
    "list_application_emojis": RouteSpec("GET", "/applications/{application_id}/emojis"),
    "get_application_emoji": RouteSpec("GET", "/applications/{application_id}/emojis/{emoji_id}"),
    "create_application_emoji": RouteSpec("POST", "/applications/{application_id}/emojis"),
    "modify_application_emoji": RouteSpec("PATCH", "/applications/{application_id}/emojis/{emoji_id}"),
    "delete_application_emoji": RouteSpec("DELETE", "/applications/{application_id}/emojis/{emoji_id}"),

    # Auto moderation
    "list_automod_rules": RouteSpec("GET", "/guilds/{guild_id}/auto-moderation/rules"),
    "get_automod_rule": RouteSpec("GET", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}"),
    "create_automod_rule": RouteSpec("POST", "/guilds/{guild_id}/auto-moderation/rules"),
    "modify_automod_rule": RouteSpec("PATCH", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}"),
    "delete_automod_rule": RouteSpec("DELETE", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}"),

    # Stage
    "create_stage_instance": RouteSpec("POST", "/stage-instances"),
    "get_stage_instance": RouteSpec("GET", "/stage-instances/{channel_id}"),
    "modify_stage_instance": RouteSpec("PATCH", "/stage-instances/{channel_id}"),
    "delete_stage_instance": RouteSpec("DELETE", "/stage-instances/{channel_id}"),

    # Scheduled events
    "list_scheduled_events": RouteSpec("GET", "/guilds/{guild_id}/scheduled-events"),
    "create_scheduled_event": RouteSpec("POST", "/guilds/{guild_id}/scheduled-events"),
    "get_scheduled_event": RouteSpec("GET", "/guilds/{guild_id}/scheduled-events/{event_id}"),
    "modify_scheduled_event": RouteSpec("PATCH", "/guilds/{guild_id}/scheduled-events/{event_id}"),
    "delete_scheduled_event": RouteSpec("DELETE", "/guilds/{guild_id}/scheduled-events/{event_id}"),
    "list_scheduled_event_users": RouteSpec("GET", "/guilds/{guild_id}/scheduled-events/{event_id}/users"),

    # Soundboard
    "list_default_soundboard_sounds": RouteSpec("GET", "/soundboard-default-sounds"),
    "list_guild_soundboard_sounds": RouteSpec("GET", "/guilds/{guild_id}/soundboard-sounds"),
    "get_guild_soundboard_sound": RouteSpec("GET", "/guilds/{guild_id}/soundboard-sounds/{sound_id}"),
    "create_guild_soundboard_sound": RouteSpec("POST", "/guilds/{guild_id}/soundboard-sounds"),
    "modify_guild_soundboard_sound": RouteSpec("PATCH", "/guilds/{guild_id}/soundboard-sounds/{sound_id}"),
    "delete_guild_soundboard_sound": RouteSpec("DELETE", "/guilds/{guild_id}/soundboard-sounds/{sound_id}"),
    "send_soundboard_sound": RouteSpec("POST", "/channels/{channel_id}/send-soundboard-sound"),

    # Polls
    "get_poll_answer_voters": RouteSpec("GET", "/channels/{channel_id}/polls/{message_id}/answers/{answer_id}"),
    "end_poll": RouteSpec("POST", "/channels/{channel_id}/polls/{message_id}/expire"),

    # Monetization
    "list_skus": RouteSpec("GET", "/applications/{application_id}/skus"),
    "list_entitlements": RouteSpec("GET", "/applications/{application_id}/entitlements"),
    "get_entitlement": RouteSpec("GET", "/applications/{application_id}/entitlements/{entitlement_id}"),
    "consume_entitlement": RouteSpec("POST", "/applications/{application_id}/entitlements/{entitlement_id}/consume"),
    "create_test_entitlement": RouteSpec("POST", "/applications/{application_id}/entitlements"),
    "delete_test_entitlement": RouteSpec("DELETE", "/applications/{application_id}/entitlements/{entitlement_id}"),
    "list_sku_subscriptions": RouteSpec("GET", "/skus/{sku_id}/subscriptions"),
    "get_sku_subscription": RouteSpec("GET", "/skus/{sku_id}/subscriptions/{subscription_id}"),
    # Extra public endpoints commonly useful alongside discord.py's HTTP layer
    "search_members": RouteSpec("GET", "/guilds/{guild_id}/members/search"),
    "list_voice_regions": RouteSpec("GET", "/voice/regions"),
    "list_guild_voice_regions": RouteSpec("GET", "/guilds/{guild_id}/regions"),
    "get_current_authorization": RouteSpec("GET", "/oauth2/@me"),
    "get_current_user_connections": RouteSpec("GET", "/users/@me/connections"),
    "get_application_role_connection_metadata": RouteSpec("GET", "/applications/{application_id}/role-connections/metadata"),
    "update_application_role_connection_metadata": RouteSpec("PUT", "/applications/{application_id}/role-connections/metadata"),
    "get_user_application_role_connection": RouteSpec("GET", "/users/@me/applications/{application_id}/role-connection"),
    "update_user_application_role_connection": RouteSpec("PUT", "/users/@me/applications/{application_id}/role-connection"),
    "get_guild_widget_settings": RouteSpec("GET", "/guilds/{guild_id}/widget"),
    "get_guild_widget_json": RouteSpec("GET", "/guilds/{guild_id}/widget.json"),
    "get_guild_widget_image": RouteSpec("GET", "/guilds/{guild_id}/widget.png"),

}

def get_route(name: str) -> RouteSpec:
    try:
        return OFFICIAL_ROUTES[name]
    except KeyError:
        raise KeyError(
            f"{name!r} is not in the official route whitelist. "
            "Only routes mirrored from the public discord.py implementation are allowed."
        ) from None

def route_count() -> int:
    return len(OFFICIAL_ROUTES)
