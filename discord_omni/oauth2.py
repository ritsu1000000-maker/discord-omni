from dataclasses import dataclass
from typing import Iterable, Optional
from urllib.parse import urlencode
import requests
from .errors import DiscordAPIError

API_BASE = "https://discord.com/api/v10"
AUTHORIZE_URL = "https://discord.com/oauth2/authorize"

@dataclass
class DiscordOAuth2:
    client_id: str
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    timeout: float = 25.0

    def authorization_url(self, scopes: Iterable[str], *, state=None, permissions=None,
                          guild_id=None, disable_guild_select=False, prompt=None,
                          integration_type=None):
        p = {"client_id": self.client_id, "response_type": "code", "scope": " ".join(scopes)}
        if self.redirect_uri: p["redirect_uri"] = self.redirect_uri
        if state: p["state"] = state
        if permissions is not None: p["permissions"] = str(permissions)
        if guild_id is not None: p["guild_id"] = str(guild_id)
        if disable_guild_select: p["disable_guild_select"] = "true"
        if prompt is not None: p["prompt"] = prompt
        if integration_type is not None: p["integration_type"] = str(integration_type)
        return AUTHORIZE_URL + "?" + urlencode(p)

    def _token(self, data):
        auth = (self.client_id, self.client_secret) if self.client_secret else None
        r = requests.post(f"{API_BASE}/oauth2/token", data=data, auth=auth,
                          headers={"Content-Type": "application/x-www-form-urlencoded"},
                          timeout=self.timeout)
        if not r.ok:
            raise DiscordAPIError("OAuth2 token request failed", status=r.status_code, body=r.text)
        return r.json()

    def exchange_code(self, code, *, code_verifier=None):
        if not self.redirect_uri: raise ValueError("redirect_uri is required")
        p = {"grant_type": "authorization_code", "code": code, "redirect_uri": self.redirect_uri}
        if code_verifier: p["code_verifier"] = code_verifier
        return self._token(p)

    def refresh(self, refresh_token):
        return self._token({"grant_type": "refresh_token", "refresh_token": refresh_token})

    def client_credentials(self, scopes):
        return self._token({"grant_type": "client_credentials", "scope": " ".join(scopes)})
