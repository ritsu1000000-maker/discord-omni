import unittest
from datetime import datetime, timezone

from discord_omni.builders import Embed, Poll, PollAnswer, AllowedMentions, message_payload
from discord_omni.permissions import Permissions
from discord_omni.snowflake import snowflake_time, snowflake_from_datetime
from discord_omni.capabilities import capabilities
from discord_omni.official_routes import OFFICIAL_ROUTES

class MaxHelpersTests(unittest.TestCase):
    def test_embed(self):
        d = Embed(title="X").add_field("A", "B").to_dict()
        self.assertEqual(d["title"], "X")
        self.assertEqual(d["fields"][0]["name"], "A")

    def test_mentions_none(self):
        self.assertEqual(AllowedMentions.none().to_dict()["parse"], [])

    def test_poll(self):
        d = Poll("Q", [PollAnswer("A"), PollAnswer("B")]).to_dict()
        self.assertEqual(len(d["answers"]), 2)

    def test_permissions(self):
        p = Permissions.from_names("VIEW_CHANNEL", "SEND_MESSAGES")
        self.assertTrue(p.has("VIEW_CHANNEL"))
        self.assertTrue(p.has("SEND_MESSAGES"))

    def test_snowflake_roundtrip(self):
        dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        sf = snowflake_from_datetime(dt)
        recovered = snowflake_time(sf)
        self.assertEqual(recovered.year, 2024)

    def test_route_inventory_200_plus(self):
        self.assertGreaterEqual(len(OFFICIAL_ROUTES), 200)

    def test_capabilities(self):
        c = capabilities()
        self.assertEqual(c["official_route_count"], len(OFFICIAL_ROUTES))
        self.assertIn("Gateway v10", c["supports"])

if __name__ == "__main__":
    unittest.main()
