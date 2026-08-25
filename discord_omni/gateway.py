from __future__ import annotations
import asyncio
import inspect
import json
import random
import time
import zlib
from collections import defaultdict, deque
import websockets

DEFAULT_GATEWAY = "wss://gateway.discord.gg/?v=10&encoding=json"
ZLIB_SUFFIX = b"\x00\x00\xff\xff"

class GatewaySendLimiter:
    """Conservative per-connection limiter. Discord's payload-size rule is also enforced."""
    def __init__(self, count=110, per=60.0):
        self.count = count
        self.per = per
        self.sent = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            while self.sent and now - self.sent[0] >= self.per:
                self.sent.popleft()
            if len(self.sent) >= self.count:
                wait = self.per - (now - self.sent[0])
                await asyncio.sleep(max(0.0, wait))
            self.sent.append(time.monotonic())

class DiscordGateway:
    def __init__(self, token, *, intents=0, shard=None, presence=None, compress=True):
        self.token = token
        self.intents = int(intents)
        self.shard = shard
        self.presence = presence
        self.compress = compress
        self.sequence = None
        self.session_id = None
        self.resume_gateway_url = None
        self.user = None
        self.guilds = {}
        self.channels = {}
        self._handlers = defaultdict(list)
        self._closed = False
        self._last_ack = True
        self._limiter = GatewaySendLimiter()
        self._ws = None
        self._zlib = zlib.decompressobj()
        self._buffer = bytearray()

    def event(self, name=None):
        def deco(fn):
            key = (name or fn.__name__).upper()
            if key.startswith("ON_"): key = key[3:]
            self._handlers[key].append(fn)
            return fn
        return deco

    async def dispatch(self, name, data):
        self._update_cache(name, data)
        for fn in list(self._handlers.get(name, [])) + list(self._handlers.get("*", [])):
            result = fn(data)
            if inspect.isawaitable(result):
                await result

    def _update_cache(self, name, data):
        if name == "READY":
            self.user = data.get("user")
            for g in data.get("guilds", []):
                if g.get("id"): self.guilds[str(g["id"])] = g
        elif name in ("GUILD_CREATE", "GUILD_UPDATE"):
            if data.get("id"): self.guilds[str(data["id"])] = data
        elif name == "GUILD_DELETE":
            self.guilds.pop(str(data.get("id")), None)
        elif name in ("CHANNEL_CREATE", "CHANNEL_UPDATE"):
            if data.get("id"): self.channels[str(data["id"])] = data
        elif name == "CHANNEL_DELETE":
            self.channels.pop(str(data.get("id")), None)

    async def send(self, op, data):
        if self._ws is None:
            raise RuntimeError("Gateway is not connected")
        payload = json.dumps({"op": int(op), "d": data}, separators=(",", ":"))
        if len(payload.encode("utf-8")) > 4096:
            raise ValueError("Gateway payload exceeds Discord's 4096-byte limit")
        await self._limiter.acquire()
        await self._ws.send(payload)

    async def update_presence(self, *, since=None, activities=None, status="online", afk=False):
        await self.send(3, {"since": since, "activities": activities or [], "status": status, "afk": bool(afk)})

    async def update_voice_state(self, guild_id, *, channel_id=None, self_mute=False, self_deaf=False):
        await self.send(4, {
            "guild_id": str(guild_id),
            "channel_id": None if channel_id is None else str(channel_id),
            "self_mute": bool(self_mute), "self_deaf": bool(self_deaf),
        })

    async def request_members(self, guild_id, *, query="", limit=0, presences=False, user_ids=None, nonce=None):
        data = {"guild_id": str(guild_id), "query": query, "limit": int(limit), "presences": bool(presences)}
        if user_ids is not None: data["user_ids"] = [str(x) for x in user_ids]
        if nonce is not None: data["nonce"] = str(nonce)
        await self.send(8, data)

    def _gateway_url(self, resume=False):
        base = self.resume_gateway_url if resume and self.resume_gateway_url else "wss://gateway.discord.gg/"
        query = "?v=10&encoding=json"
        if self.compress:
            query += "&compress=zlib-stream"
        return base.rstrip("/") + "/" + query

    def _decode(self, raw):
        if isinstance(raw, str):
            return json.loads(raw)
        if not self.compress:
            return json.loads(raw.decode("utf-8"))
        self._buffer.extend(raw)
        if len(raw) < 4 or raw[-4:] != ZLIB_SUFFIX:
            return None
        text = self._zlib.decompress(bytes(self._buffer)).decode("utf-8")
        self._buffer.clear()
        return json.loads(text)

    async def _heartbeat(self, interval):
        await asyncio.sleep(random.random() * interval)
        while not self._closed and self._ws is not None:
            if not self._last_ack:
                await self._ws.close(code=4000)
                return
            self._last_ack = False
            await self.send(1, self.sequence)
            await asyncio.sleep(interval)

    async def _identify(self):
        d = {
            "token": self.token,
            "intents": self.intents,
            "properties": {"os": "python", "browser": "discord-omni-api", "device": "discord-omni-api"},
        }
        if self.shard is not None: d["shard"] = list(self.shard)
        if self.presence is not None: d["presence"] = self.presence
        await self.send(2, d)

    async def _resume(self):
        await self.send(6, {"token": self.token, "session_id": self.session_id, "seq": self.sequence})

    async def connect(self, *, reconnect=True):
        self._closed = False
        resume = bool(self.session_id and self.sequence is not None)
        backoff = 1.0

        while not self._closed:
            try:
                async with websockets.connect(self._gateway_url(resume), max_size=None, compression=None) as ws:
                    self._ws = ws
                    raw = await ws.recv()
                    hello = self._decode(raw)
                    if not hello or hello.get("op") != 10:
                        raise RuntimeError("Expected Gateway HELLO")
                    interval = hello["d"]["heartbeat_interval"] / 1000.0
                    self._last_ack = True
                    hb = asyncio.create_task(self._heartbeat(interval))
                    await (self._resume() if resume else self._identify())
                    backoff = 1.0

                    try:
                        async for raw in ws:
                            p = self._decode(raw)
                            if p is None:
                                continue
                            if p.get("s") is not None:
                                self.sequence = p["s"]
                            op = p.get("op")
                            if op == 0:
                                name = p.get("t")
                                data = p.get("d") or {}
                                if name == "READY":
                                    self.session_id = data.get("session_id")
                                    self.resume_gateway_url = data.get("resume_gateway_url")
                                    resume = True
                                elif name == "RESUMED":
                                    resume = True
                                await self.dispatch(name, data)
                            elif op == 1:
                                await self.send(1, self.sequence)
                            elif op == 7:
                                resume = True
                                break
                            elif op == 9:
                                resume = bool(p.get("d"))
                                if not resume:
                                    self.session_id = None
                                    self.sequence = None
                                    self.resume_gateway_url = None
                                await asyncio.sleep(random.uniform(1, 5))
                                break
                            elif op == 11:
                                self._last_ack = True
                    finally:
                        hb.cancel()
                        self._ws = None

            except asyncio.CancelledError:
                raise
            except Exception:
                self._ws = None
                if not reconnect or self._closed:
                    raise
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

            if not reconnect:
                break

    async def close(self):
        self._closed = True
        if self._ws is not None:
            await self._ws.close(code=1000)
            self._ws = None


class ShardManager:
    """Starts multiple shards while respecting max_concurrency buckets."""

    def __init__(self, token, shard_count, *, intents=0, max_concurrency=1, compress=True):
        self.token = token
        self.shard_count = int(shard_count)
        self.intents = int(intents)
        self.max_concurrency = max(1, int(max_concurrency))
        self.compress = compress
        self.shards = [
            DiscordGateway(token, intents=intents, shard=(i, self.shard_count), compress=compress)
            for i in range(self.shard_count)
        ]

    def event(self, name=None):
        def deco(fn):
            for shard in self.shards:
                shard.event(name)(fn)
            return fn
        return deco

    async def start(self):
        tasks = []
        # Identify buckets are shard_id % max_concurrency. Start a wave, then wait 5s.
        for wave_start in range(0, self.shard_count, self.max_concurrency):
            for shard in self.shards[wave_start:wave_start + self.max_concurrency]:
                tasks.append(asyncio.create_task(shard.connect()))
            if wave_start + self.max_concurrency < self.shard_count:
                await asyncio.sleep(5.1)
        await asyncio.gather(*tasks)
