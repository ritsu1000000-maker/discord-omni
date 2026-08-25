from __future__ import annotations


class AutoModEditor:
    def __init__(self, client, guild_id):
        self.client = client
        self.guild_id = str(guild_id)

    def list(self):
        return self.client.official.list_automod_rules(guild_id=self.guild_id)

    def create(self, payload, *, reason=None):
        return self.client.official.create_automod_rule(guild_id=self.guild_id, json=payload, reason=reason)

    def update(self, rule_id, payload, *, reason=None):
        return self.client.official.modify_automod_rule(guild_id=self.guild_id, rule_id=rule_id, json=payload, reason=reason)

    def delete(self, rule_id, *, reason=None):
        return self.client.official.delete_automod_rule(guild_id=self.guild_id, rule_id=rule_id, reason=reason)
