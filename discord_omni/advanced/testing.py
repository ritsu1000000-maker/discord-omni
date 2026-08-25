from __future__ import annotations
from collections import deque


class FakeREST:
    def __init__(self):
        self.calls = []
        self.responses = deque()

    def queue(self, response):
        self.responses.append(response)
        return self

    def request(self, method, path, **kwargs):
        self.calls.append({"method": method, "path": path, **kwargs})
        return self.responses.popleft() if self.responses else None


class AsyncFakeREST:
    def __init__(self):
        self.calls = []
        self.responses = deque()

    def queue(self, response):
        self.responses.append(response)
        return self

    async def request(self, method, path, **kwargs):
        self.calls.append({"method": method, "path": path, **kwargs})
        return self.responses.popleft() if self.responses else None


def interaction_fixture(
    *,
    interaction_type=2,
    name="test",
    user_id="1",
    guild_id="2",
    channel_id="3",
    options=None,
    custom_id=None,
):
    data = {"name": name}
    if options is not None:
        data["options"] = options
    if custom_id is not None:
        data["custom_id"] = custom_id
    return {
        "id": "10",
        "application_id": "20",
        "type": interaction_type,
        "token": "test-token",
        "guild_id": guild_id,
        "channel_id": channel_id,
        "member": {"user": {"id": user_id, "username": "tester"}},
        "data": data,
    }
