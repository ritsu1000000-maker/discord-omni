import unittest
from discord_omni.community import TopGGClient, TopGGWebhookEvent

class TopGGTests(unittest.TestCase):
    def test_vote_payload(self):
        event = TopGGClient.parse_webhook({
            "type": "vote.create",
            "data": {
                "weight": 2,
                "user": {"platform_id": "123"},
                "project": {"platform_id": "456"},
            },
        })
        self.assertTrue(event.is_vote)
        self.assertEqual(event.discord_user_id, "123")
        self.assertEqual(event.discord_project_id, "456")
        self.assertEqual(event.vote_weight, 2)

    def test_metrics_validation(self):
        client = TopGGClient("dummy")
        with self.assertRaises(ValueError):
            client.post_metrics()

    def test_batch_validation(self):
        client = TopGGClient("dummy")
        with self.assertRaises(ValueError):
            client.post_metrics_batch([])

if __name__ == "__main__":
    unittest.main()
