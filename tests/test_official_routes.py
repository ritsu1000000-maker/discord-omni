import unittest
from discord_omni.official_routes import OFFICIAL_ROUTES, get_route
from discord_omni.official_api import _format_path

class OfficialRouteTests(unittest.TestCase):
    def test_route_inventory_large(self):
        self.assertGreaterEqual(len(OFFICIAL_ROUTES), 150)

    def test_base_paths_are_relative(self):
        for name, spec in OFFICIAL_ROUTES.items():
            self.assertTrue(spec.path.startswith("/"), name)
            self.assertNotIn("canary.discord.com", spec.path)
            self.assertNotIn("ptb.discord.com", spec.path)

    def test_unknown_route_is_rejected(self):
        with self.assertRaises(KeyError):
            get_route("private_magic_endpoint")

    def test_format_path(self):
        path, remaining = _format_path(
            "/guilds/{guild_id}/members/{user_id}",
            {"guild_id": 1, "user_id": 2},
        )
        self.assertEqual(path, "/guilds/1/members/2")
        self.assertEqual(remaining, {})

    def test_modern_pin_route(self):
        self.assertEqual(
            OFFICIAL_ROUTES["pin_message"].path,
            "/channels/{channel_id}/messages/pins/{message_id}",
        )

if __name__ == "__main__":
    unittest.main()
