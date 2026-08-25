import asyncio
import unittest

from discord_omni.advanced import (
    TTLCache, CooldownManager, CooldownError,
    SignedCustomID, CustomIDError, EventBus,
    PermissionResolver, ComponentRouter, Metrics,
)

class AdvancedTests(unittest.TestCase):
    def test_ttl_cache(self):
        c = TTLCache(ttl=60, max_size=2)
        c.set("a", 1)
        self.assertEqual(c.get("a"), 1)

    def test_cooldown(self):
        c = CooldownManager(rate=1, per=10)
        c.check("u")
        with self.assertRaises(CooldownError):
            c.check("u")

    def test_signed_custom_id(self):
        codec = SignedCustomID("secret", namespace="x")
        value = codec.encode("open", page=2)
        decoded = codec.decode(value)
        self.assertEqual(decoded["a"], "open")
        self.assertEqual(decoded["d"]["page"], 2)
        with self.assertRaises(CustomIDError):
            codec.decode(value[:-1] + ("A" if value[-1] != "A" else "B"))

    def test_permission_resolver(self):
        resolver = PermissionResolver()
        guild = {"id": "1", "owner_id": "999"}
        roles = [
            {"id": "1", "permissions": "1024"},
            {"id": "2", "permissions": "2048"},
        ]
        member = {"user": {"id": "5"}, "roles": ["2"]}
        self.assertEqual(resolver.guild_permissions(guild, member, roles), 3072)

    def test_metrics(self):
        m = Metrics()
        m.inc("x")
        m.set_gauge("g", 2)
        snap = m.snapshot()
        self.assertEqual(snap["counters"]["x"], 1)
        self.assertEqual(snap["gauges"]["g"], 2)

    def test_event_bus(self):
        async def run():
            bus = EventBus()
            out = []
            @bus.on("x", priority=10)
            async def a(v): out.append(("a", v))
            @bus.once("x")
            async def b(v): out.append(("b", v))
            await bus.emit("x", 1)
            await bus.emit("x", 2)
            return out
        out = asyncio.run(run())
        self.assertEqual(out, [("a", 1), ("b", 1), ("a", 2)])

    def test_component_router(self):
        async def run():
            router = ComponentRouter()
            class Ctx:
                user_id = "u"
            @router.route(r"item:(?P<id>\d+)")
            async def item(ctx, id):
                return int(id)
            return await router.dispatch("item:42", Ctx())
        self.assertEqual(asyncio.run(run()), 42)

if __name__ == "__main__":
    unittest.main()
