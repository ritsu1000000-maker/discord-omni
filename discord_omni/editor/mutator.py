from __future__ import annotations
import uuid
from copy import deepcopy
from .models import GuildSnapshot
from .selectors import by_id, by_name


class SnapshotMutator:
    def __init__(self, snapshot: GuildSnapshot):
        self.snapshot = snapshot

    def set_guild(self, **changes):
        self.snapshot.guild.update({k: v for k, v in changes.items() if v is not None})
        return self

    def create_text_channel(self, name, **options):
        item = {"id": None, "_local_id": f"channel:{uuid.uuid4().hex}", "type": 0, "name": name, **options}
        self.snapshot.channels.append(item)
        return item

    def create_category(self, name, **options):
        item = {"id": None, "_local_id": f"channel:{uuid.uuid4().hex}", "type": 4, "name": name, **options}
        self.snapshot.channels.append(item)
        return item

    def edit_channel(self, channel_id, **changes):
        item = by_id(self.snapshot.channels, channel_id)
        if item is None:
            raise LookupError(f"channel not found: {channel_id}")
        item.update(changes)
        return item

    def edit_channel_named(self, name, **changes):
        matches = by_name(self.snapshot.channels, name)
        if len(matches) != 1:
            raise LookupError(f"channel name matched {len(matches)} items: {name}")
        matches[0].update(changes)
        return matches[0]

    def delete_channel(self, channel_id):
        item = by_id(self.snapshot.channels, channel_id)
        if item is None:
            raise LookupError(f"channel not found: {channel_id}")
        self.snapshot.channels.remove(item)
        return item

    def create_role(self, name, **options):
        item = {"id": None, "_local_id": f"role:{uuid.uuid4().hex}", "name": name, "permissions": "0", **options}
        self.snapshot.roles.append(item)
        return item

    def edit_role(self, role_id, **changes):
        item = by_id(self.snapshot.roles, role_id)
        if item is None:
            raise LookupError(f"role not found: {role_id}")
        item.update(changes)
        return item

    def edit_role_named(self, name, **changes):
        matches = by_name(self.snapshot.roles, name)
        if len(matches) != 1:
            raise LookupError(f"role name matched {len(matches)} items: {name}")
        matches[0].update(changes)
        return matches[0]

    def delete_role(self, role_id):
        if str(role_id) == str(self.snapshot.guild_id):
            raise ValueError("@everyone role cannot be removed")
        item = by_id(self.snapshot.roles, role_id)
        if item is None:
            raise LookupError(f"role not found: {role_id}")
        self.snapshot.roles.remove(item)
        return item

    def clone_channel(self, channel_id, *, name=None):
        source = by_id(self.snapshot.channels, channel_id)
        if source is None:
            raise LookupError(f"channel not found: {channel_id}")
        clone = deepcopy(source)
        clone["id"] = None
        clone["_local_id"] = f"channel:{uuid.uuid4().hex}"
        clone["name"] = name or f'{source.get("name", "channel")}-copy'
        self.snapshot.channels.append(clone)
        return clone

    def clone_role(self, role_id, *, name=None):
        source = by_id(self.snapshot.roles, role_id)
        if source is None:
            raise LookupError(f"role not found: {role_id}")
        clone = deepcopy(source)
        clone["id"] = None
        clone["_local_id"] = f"role:{uuid.uuid4().hex}"
        clone["name"] = name or f'{source.get("name", "role")}-copy'
        self.snapshot.roles.append(clone)
        return clone
