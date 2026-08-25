import unittest
from discord_omni.components import Container, TextDisplay, ActionRow, Button, Checkbox

class ComponentTests(unittest.TestCase):
    def test_v2_tree(self):
        c = Container([
            TextDisplay("hello"),
            ActionRow([Button(label="OK", custom_id="ok")]),
        ])
        d = c.to_dict()
        self.assertEqual(d["type"], 17)
        self.assertEqual(d["components"][0]["type"], 10)
        self.assertEqual(d["components"][1]["components"][0]["custom_id"], "ok")

    def test_checkbox(self):
        d = Checkbox(custom_id="agree", label="Agree").to_dict()
        self.assertEqual(d["type"], 23)
        self.assertTrue(d["required"])

if __name__ == "__main__":
    unittest.main()
