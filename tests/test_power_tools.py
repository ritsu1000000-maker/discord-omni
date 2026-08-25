import unittest
from datetime import datetime, timezone

from discord_omni import power_tools as p
from discord_omni.feature_registry import power_feature_count, power_feature_names

class PowerToolsTests(unittest.TestCase):
    def test_feature_count(self):
        self.assertGreaterEqual(power_feature_count(), 140)

    def test_mentions(self):
        self.assertEqual(p.mention_user(123), "<@123>")
        self.assertEqual(p.mention_channel(123), "<#123>")
        self.assertEqual(p.mention_role(123), "<@&123>")

    def test_oauth(self):
        url = p.build_bot_invite_url("123", permissions=8)
        self.assertIn("discord.com/oauth2/authorize", url)
        self.assertIn("permissions=8", url)

    def test_pkce(self):
        verifier = p.generate_pkce_verifier()
        challenge = p.pkce_challenge(verifier)
        self.assertTrue(verifier)
        self.assertTrue(challenge)

    def test_command_builder(self):
        cmd = p.slash_command("hello", "desc", options=[p.string_option("name", "Name")])
        self.assertEqual(cmd["type"], 1)
        self.assertEqual(cmd["options"][0]["type"], 3)

    def test_components(self):
        tree = p.container(
            p.text_display("hello"),
            p.action_row(p.button("OK", custom_id="ok")),
        )
        self.assertGreaterEqual(p.component_tree_count(tree), 4)
        self.assertEqual(p.component_custom_ids(tree), ["ok"])

    def test_route_tools(self):
        self.assertTrue(p.route_exists("get_guild"))
        self.assertIn("get_guild", p.find_routes("guild"))

    def test_poll(self):
        poll = p.poll_payload("Q", ["A", "B"])
        self.assertTrue(p.validate_poll_payload(poll))

    def test_permission_helpers(self):
        value = p.permission_value("VIEW_CHANNEL", "SEND_MESSAGES")
        self.assertTrue(p.permission_has(value, "VIEW_CHANNEL"))

    def test_snowflake(self):
        self.assertTrue(p.is_snowflake("123456789012345678"))
        self.assertEqual(p.normalize_snowflake("00123"), "123")

if __name__ == "__main__":
    unittest.main()
