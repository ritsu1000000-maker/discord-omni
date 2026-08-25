from __future__ import annotations
import inspect
import json
from dataclasses import dataclass
from typing import Any, Callable, Optional

def verify_interaction_signature(public_key_hex, signature_hex, timestamp, raw_body):
    try:
        from nacl.exceptions import BadSignatureError
        from nacl.signing import VerifyKey
    except ImportError as exc:
        raise RuntimeError(
            "Interaction signature verification requires PyNaCl. "
            "Install package dependencies with: pip install discord-omni-api"
        ) from exc

    try:
        VerifyKey(bytes.fromhex(public_key_hex)).verify(
            timestamp.encode("utf-8") + raw_body,
            bytes.fromhex(signature_hex),
        )
        return True
    except (BadSignatureError, ValueError):
        return False

def message_response(content="", *, ephemeral=False, **fields):
    d = {"content": content, **fields}
    if ephemeral: d["flags"] = int(d.get("flags", 0)) | 64
    return {"type": 4, "data": d}

def components_v2_response(*components, ephemeral=False, flags=0, **fields):
    d = dict(fields)
    d["flags"] = int(flags) | (1 << 15) | (64 if ephemeral else 0)
    d["components"] = [x.to_dict() if hasattr(x, "to_dict") else x for x in components]
    return {"type": 4, "data": d}

def deferred_response(*, ephemeral=False):
    return {"type": 5, "data": {"flags": 64} if ephemeral else {}}

def autocomplete_response(choices):
    return {"type": 8, "data": {"choices": list(choices)}}

def modal_response(custom_id, title, *components):
    return {"type": 9, "data": {
        "custom_id": custom_id,
        "title": title,
        "components": [x.to_dict() if hasattr(x, "to_dict") else x for x in components],
    }}

@dataclass
class InteractionContext:
    payload: dict[str, Any]

    @property
    def data(self): return self.payload.get("data") or {}
    @property
    def user(self):
        member = self.payload.get("member") or {}
        return member.get("user") or self.payload.get("user")
    @property
    def guild_id(self): return self.payload.get("guild_id")
    @property
    def channel_id(self): return self.payload.get("channel_id")
    @property
    def custom_id(self): return self.data.get("custom_id")
    @property
    def command_name(self): return self.data.get("name")

    def reply(self, content="", **kwargs): return message_response(content, **kwargs)
    def reply_components(self, *components, **kwargs): return components_v2_response(*components, **kwargs)
    def defer(self, **kwargs): return deferred_response(**kwargs)
    def modal(self, custom_id, title, *components): return modal_response(custom_id, title, *components)

class InteractionApp:
    def __init__(self, public_key: str):
        self.public_key = public_key
        self.commands = {}
        self.components = {}
        self.modals = {}
        self.autocomplete_handlers = {}

    def slash_command(self, name):
        def deco(fn):
            self.commands[name] = fn
            return fn
        return deco

    def component(self, custom_id):
        def deco(fn):
            self.components[custom_id] = fn
            return fn
        return deco

    def modal(self, custom_id):
        def deco(fn):
            self.modals[custom_id] = fn
            return fn
        return deco

    def autocomplete(self, command_name):
        def deco(fn):
            self.autocomplete_handlers[command_name] = fn
            return fn
        return deco

    async def _invoke(self, fn, ctx):
        result = fn(ctx)
        if inspect.isawaitable(result):
            result = await result
        return result

    async def handle_payload(self, payload):
        t = payload.get("type")
        if t == 1:
            return {"type": 1}
        ctx = InteractionContext(payload)
        if t == 2:
            fn = self.commands.get(ctx.command_name)
        elif t == 3:
            fn = self.components.get(ctx.custom_id)
        elif t == 4:
            fn = self.autocomplete_handlers.get(ctx.command_name)
        elif t == 5:
            fn = self.modals.get(ctx.custom_id)
        else:
            fn = None
        if fn is None:
            return message_response("No handler registered.", ephemeral=True)
        result = await self._invoke(fn, ctx)
        return result if result is not None else deferred_response()

    async def _http_handler(self, request):
        raw = await request.read()
        sig = request.headers.get("X-Signature-Ed25519", "")
        ts = request.headers.get("X-Signature-Timestamp", "")
        if not verify_interaction_signature(self.public_key, sig, ts, raw):
            from aiohttp import web
            return web.Response(status=401, text="invalid request signature")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            from aiohttp import web
            return web.Response(status=400, text="invalid json")
        result = await self.handle_payload(payload)
        from aiohttp import web
        return web.json_response(result)

    def aiohttp_app(self, path="/interactions"):
        try:
            from aiohttp import web
        except ImportError as exc:
            raise RuntimeError(
                "InteractionApp HTTP server requires aiohttp. "
                "Install package dependencies with: pip install discord-omni-api"
            ) from exc
        app = web.Application()
        app.router.add_post(path, self._http_handler)
        return app

    def run(self, *, host="127.0.0.1", port=8080, path="/interactions"):
        try:
            from aiohttp import web
        except ImportError as exc:
            raise RuntimeError(
                "InteractionApp HTTP server requires aiohttp. "
                "Install package dependencies with: pip install discord-omni-api"
            ) from exc
        web.run_app(self.aiohttp_app(path), host=host, port=port)
