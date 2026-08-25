from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from urllib.parse import quote
import requests

from .errors import DiscordAPIError, DiscordAuthError, DiscordRateLimitError

API_BASE = "https://discord.com/api/v10"


@dataclass
class DiscordREST:
    token: Optional[str] = None
    auth_scheme: str = "Bot"
    api_base: str = API_BASE
    timeout: float = 25.0
    max_retries: int = 3
    max_rate_limit_sleep: float = 60.0
    user_agent: str = "discord-omni-api/0.5.0"

    def _headers(self, *, auth=True, reason=None, extra=None):
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"{self.auth_scheme} {self.token}"
        if reason:
            headers["X-Audit-Log-Reason"] = quote(reason, safe="")
        if extra:
            headers.update(dict(extra))
        return headers

    def request(self, method, path, *, json=None, params=None, data=None, files=None,
                headers=None, reason=None, auth=True):
        if not path.startswith("/"):
            path = "/" + path
        method = method.upper()
        url = self.api_base.rstrip("/") + path

        for attempt in range(self.max_retries + 1):
            r = requests.request(
                method, url,
                headers=self._headers(auth=auth, reason=reason, extra=headers),
                json=json, params=params, data=data, files=files,
                timeout=self.timeout,
            )
            if r.status_code == 429:
                try:
                    body = r.json()
                except Exception:
                    body = {}
                retry_after = float(body.get("retry_after", r.headers.get("Retry-After", 1)))
                if attempt < self.max_retries and retry_after <= self.max_rate_limit_sleep:
                    time.sleep(max(0.0, retry_after))
                    continue
                raise DiscordRateLimitError("Rate limited", status=429, body=body,
                                            retry_after=retry_after, route=f"{method} {path}")

            if 500 <= r.status_code < 600 and attempt < self.max_retries:
                time.sleep(min(4.0, 0.5 * (2 ** attempt)))
                continue

            if r.status_code == 204:
                return None

            try:
                body = r.json() if r.content else None
            except Exception:
                body = r.text

            if not r.ok:
                code = body.get("code") if isinstance(body, dict) else None
                cls = DiscordAuthError if r.status_code in (401, 403) else DiscordAPIError
                raise cls(f"Discord API HTTP {r.status_code}", status=r.status_code,
                          code=code, body=body, route=f"{method} {path}")
            return body

        raise DiscordAPIError("Request failed after retries", route=f"{method} {path}")

    def raw_request(self, method, path, **kwargs):
        return self.request(method, path, **kwargs)
