from __future__ import annotations


class MemberEditor:
    def __init__(self, client, guild_id, user_id):
        self.client = client
        self.guild_id = str(guild_id)
        self.user_id = str(user_id)

    def set_nickname(self, nickname, *, reason=None):
        return self.client.official.modify_member(guild_id=self.guild_id, user_id=self.user_id, json={"nick": nickname}, reason=reason)

    def add_role(self, role_id, *, reason=None):
        return self.client.official.add_member_role(guild_id=self.guild_id, user_id=self.user_id, role_id=role_id, reason=reason)

    def remove_role(self, role_id, *, reason=None):
        return self.client.official.remove_member_role(guild_id=self.guild_id, user_id=self.user_id, role_id=role_id, reason=reason)

    def move_voice(self, channel_id, *, reason=None):
        return self.client.official.modify_member(guild_id=self.guild_id, user_id=self.user_id, json={"channel_id": channel_id}, reason=reason)
