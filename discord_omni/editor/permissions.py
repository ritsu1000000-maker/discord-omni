from __future__ import annotations


def overwrite_payload(*, allow=0, deny=0, target_type=0):
    return {"allow": str(int(allow)), "deny": str(int(deny)), "type": int(target_type)}


def set_channel_overwrite(client, channel_id, target_id, *, allow=0, deny=0, target_type=0, reason=None):
    return client.official.edit_channel_permissions(channel_id=channel_id, target_id=target_id, json=overwrite_payload(allow=allow, deny=deny, target_type=target_type), reason=reason)


def delete_channel_overwrite(client, channel_id, target_id, *, reason=None):
    return client.official.delete_channel_permissions(channel_id=channel_id, target_id=target_id, reason=reason)
