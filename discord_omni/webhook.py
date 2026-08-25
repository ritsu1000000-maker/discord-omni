import re
from dataclasses import dataclass
from .rest import DiscordREST

_RE = re.compile(r"/webhooks/(\d+)/([^/?]+)")

@dataclass
class DiscordWebhook:
    webhook_id: str
    token: str
    rest: DiscordREST

    @classmethod
    def from_url(cls, url):
        m = _RE.search(url)
        if not m:
            raise ValueError("Invalid Discord webhook URL")
        return cls(m.group(1), m.group(2), DiscordREST())

    @property
    def base_path(self): return f"/webhooks/{self.webhook_id}/{self.token}"

    def get(self): return self.rest.request("GET", self.base_path, auth=False)
    def modify(self, **fields): return self.rest.request("PATCH", self.base_path, json=fields, auth=False)
    def delete(self): return self.rest.request("DELETE", self.base_path, auth=False)

    def send(self, content=None, *, wait=True, thread_id=None, with_components=False, **fields):
        payload = dict(fields)
        if content is not None: payload["content"] = str(content)
        params = {"wait": int(bool(wait)), "with_components": int(bool(with_components))}
        if thread_id is not None: params["thread_id"] = str(thread_id)
        return self.rest.request("POST", self.base_path, json=payload, params=params, auth=False)

    def send_components_v2(self, *components, wait=True, thread_id=None, flags=0, **fields):
        payload = dict(fields)
        payload["flags"] = int(flags) | (1 << 15)
        payload["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in components]
        params = {"wait": int(bool(wait)), "with_components": 1}
        if thread_id is not None: params["thread_id"] = str(thread_id)
        return self.rest.request("POST", self.base_path, json=payload, params=params, auth=False)

    def get_message(self, message_id, *, thread_id=None):
        p = {"thread_id": str(thread_id)} if thread_id is not None else None
        return self.rest.request("GET", f"{self.base_path}/messages/{message_id}", params=p, auth=False)
    def edit_message(self, message_id, *, thread_id=None, **fields):
        p = {"thread_id": str(thread_id)} if thread_id is not None else None
        return self.rest.request("PATCH", f"{self.base_path}/messages/{message_id}", json=fields, params=p, auth=False)
    def delete_message(self, message_id, *, thread_id=None):
        p = {"thread_id": str(thread_id)} if thread_id is not None else None
        return self.rest.request("DELETE", f"{self.base_path}/messages/{message_id}", params=p, auth=False)
