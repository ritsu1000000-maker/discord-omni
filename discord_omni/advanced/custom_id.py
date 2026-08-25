from __future__ import annotations
import base64
import hashlib
import hmac
import json
from typing import Any


class CustomIDError(ValueError):
    pass


class SignedCustomID:
    """
    Encodes compact component state into a custom_id and signs it with HMAC.
    Useful for preventing users from manually altering button/modal state.
    """
    def __init__(self, secret: str | bytes, *, namespace="x", max_length=100):
        self.secret = secret.encode() if isinstance(secret, str) else bytes(secret)
        self.namespace = namespace
        self.max_length = int(max_length)

    def _sign(self, raw: bytes) -> str:
        sig = hmac.new(self.secret, raw, hashlib.sha256).digest()[:10]
        return base64.urlsafe_b64encode(sig).decode().rstrip("=")

    def encode(self, action: str, **data: Any) -> str:
        payload = {"a": action, "d": data}
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
        body = base64.urlsafe_b64encode(raw).decode().rstrip("=")
        signed = f"{self.namespace}.{body}.{self._sign(raw)}"
        if len(signed) > self.max_length:
            raise CustomIDError("encoded custom_id exceeds Discord's 100-character limit")
        return signed

    def decode(self, custom_id: str) -> dict[str, Any]:
        try:
            ns, body, signature = custom_id.split(".", 2)
            if ns != self.namespace:
                raise CustomIDError("namespace mismatch")
            pad = "=" * (-len(body) % 4)
            raw = base64.urlsafe_b64decode(body + pad)
            expected = self._sign(raw)
            if not hmac.compare_digest(signature, expected):
                raise CustomIDError("invalid signature")
            return json.loads(raw.decode())
        except CustomIDError:
            raise
        except Exception as exc:
            raise CustomIDError("invalid custom_id") from exc
