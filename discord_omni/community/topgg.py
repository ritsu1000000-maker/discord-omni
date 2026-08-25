from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import requests


TOPGG_V1_BASE = "https://top.gg/api/v1"


class TopGGError(RuntimeError):
    def __init__(self, message: str, *, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


@dataclass(slots=True)
class TopGGWebhookEvent:
    type: str
    data: dict[str, Any]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "TopGGWebhookEvent":
        return cls(
            type=str(payload.get("type", "")),
            data=dict(payload.get("data") or {}),
        )

    @property
    def is_vote(self) -> bool:
        return self.type == "vote.create"

    @property
    def is_test(self) -> bool:
        return self.type == "webhook.test"

    @property
    def discord_user_id(self) -> Optional[str]:
        user = self.data.get("user") or {}
        value = user.get("platform_id")
        return str(value) if value is not None else None

    @property
    def discord_project_id(self) -> Optional[str]:
        project = self.data.get("project") or {}
        value = project.get("platform_id")
        return str(value) if value is not None else None

    @property
    def vote_weight(self) -> int:
        try:
            return int(self.data.get("weight", 1))
        except (TypeError, ValueError):
            return 1


class TopGGClient:
    """
    Small Top.gg v1 client.

    This module is deliberately isolated from the Discord official API client:
    `discord_omni.community.TopGGClient`.

    Authentication uses the Top.gg project token as a Bearer token.
    """

    def __init__(self, token: str, *, timeout: float = 20.0):
        if not token:
            raise ValueError("Top.gg token is required")
        self.token = token
        self.timeout = float(timeout)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "discord-omni-api/0.6.1 community-topgg",
        }

    def _request(self, method: str, path: str, *, json: Any = None) -> Any:
        if not path.startswith("/"):
            path = "/" + path

        response = requests.request(
            method.upper(),
            TOPGG_V1_BASE + path,
            headers=self._headers(),
            json=json,
            timeout=self.timeout,
        )

        if response.status_code == 204:
            return None

        try:
            body = response.json() if response.content else None
        except Exception:
            body = response.text

        if not response.ok:
            detail = body.get("detail") if isinstance(body, dict) else body
            raise TopGGError(
                f"Top.gg API HTTP {response.status_code}: {detail}",
                status=response.status_code,
                body=body,
            )

        return body

    def get_project(self) -> dict[str, Any]:
        """GET /projects/@me"""
        return self._request("GET", "/projects/@me")

    def update_project(
        self,
        *,
        headline: Optional[dict[str, str]] = None,
        page_content: Optional[dict[str, str]] = None,
    ) -> None:
        """PATCH /projects/@me"""
        payload: dict[str, Any] = {}
        if headline is not None:
            payload["headline"] = headline
        if page_content is not None:
            payload["page_content"] = page_content
        if not payload:
            raise ValueError("headline or page_content is required")
        self._request("PATCH", "/projects/@me", json=payload)

    def create_announcement(self, title: str, content: str) -> dict[str, Any]:
        """POST /projects/@me/announcements"""
        return self._request(
            "POST",
            "/projects/@me/announcements",
            json={"title": title, "content": content},
        )

    def post_metrics(
        self,
        *,
        server_count: Optional[int] = None,
        shard_count: Optional[int] = None,
        member_count: Optional[int] = None,
        online_count: Optional[int] = None,
    ) -> None:
        """PATCH /projects/@me/metrics"""
        payload: dict[str, int] = {}
        for key, value in {
            "server_count": server_count,
            "shard_count": shard_count,
            "member_count": member_count,
            "online_count": online_count,
        }.items():
            if value is not None:
                if int(value) < 0:
                    raise ValueError(f"{key} must be >= 0")
                payload[key] = int(value)

        if not payload:
            raise ValueError("At least one metric is required")

        self._request("PATCH", "/projects/@me/metrics", json=payload)

    def post_metrics_batch(self, entries: list[dict[str, Any]]) -> None:
        """POST /projects/@me/metrics/batch"""
        if not 1 <= len(entries) <= 100:
            raise ValueError("entries must contain 1 to 100 items")
        self._request("POST", "/projects/@me/metrics/batch", json={"data": entries})

    def push_commands(self, commands: list[dict[str, Any]]) -> None:
        """
        PUT /projects/@me/commands

        Pushes Discord application-command definitions to the bot's Top.gg page.
        This does not register the commands with Discord itself.
        """
        self._request("PUT", "/projects/@me/commands", json=list(commands))

    @staticmethod
    def parse_webhook(payload: dict[str, Any]) -> TopGGWebhookEvent:
        return TopGGWebhookEvent.from_payload(payload)
