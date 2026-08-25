import unittest
from discord_omni.editor import (
    GuildSnapshot, SnapshotMutator, build_plan, EditorPolicy, PolicyError
)
from discord_omni.client import DiscordClient
from discord_omni.async_client import AsyncDiscordClient


class EditorTests(unittest.TestCase):
    def snapshot(self):
        return GuildSnapshot(
            guild_id="1",
            guild={"id": "1", "name": "Old"},
            channels=[
                {"id": "10", "name": "general", "type": 0, "position": 0},
                {"id": "11", "name": "old", "type": 0, "position": 1},
            ],
            roles=[
                {"id": "1", "name": "@everyone", "permissions": "0", "position": 0},
                {"id": "20", "name": "Member", "permissions": "0", "position": 1},
            ],
        )

    def test_mutate_and_plan(self):
        current = self.snapshot()
        desired = current.copy()
        edit = SnapshotMutator(desired)
        edit.set_guild(name="New")
        edit.edit_channel("10", topic="hello")
        edit.create_text_channel("news")
        edit.create_role("Moderator", permissions="8")
        plan = build_plan(current, desired)
        summaries = plan.summaries()
        self.assertTrue(any("UPDATE guild" in x for x in summaries))
        self.assertTrue(any("CREATE channel news" in x for x in summaries))
        self.assertTrue(any("CREATE role Moderator" in x for x in summaries))

    def test_delete_policy_blocks(self):
        current = self.snapshot()
        desired = current.copy()
        SnapshotMutator(desired).delete_channel("11")
        plan = build_plan(current, desired)
        with self.assertRaises(PolicyError):
            EditorPolicy().validate(plan)

    def test_delete_policy_allows_explicitly(self):
        current = self.snapshot()
        desired = current.copy()
        SnapshotMutator(desired).delete_channel("11")
        plan = build_plan(current, desired)
        policy = EditorPolicy(
            allow_delete_channels=True,
            max_destructive_operations=1,
        )
        self.assertTrue(policy.validate(plan))

    def test_clone(self):
        s = self.snapshot()
        clone = SnapshotMutator(s).clone_channel("10", name="copy")
        self.assertIsNone(clone["id"])
        self.assertEqual(clone["name"], "copy")

    def test_send_methods_are_class_members(self):
        self.assertTrue(hasattr(DiscordClient, "send"))
        self.assertTrue(hasattr(DiscordClient, "fetch"))
        self.assertTrue(hasattr(DiscordClient, "editor"))
        self.assertTrue(hasattr(AsyncDiscordClient, "send"))
        self.assertTrue(hasattr(AsyncDiscordClient, "fetch"))
        self.assertTrue(hasattr(AsyncDiscordClient, "editor"))


if __name__ == "__main__":
    unittest.main()
