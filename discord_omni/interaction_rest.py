from __future__ import annotations
from .rest import DiscordREST

class InteractionREST:
    """Official interaction callback/followup routes used by discord.py webhooks."""

    def __init__(self):
        self.rest = DiscordREST()

    def create_response(self, interaction_id, interaction_token, payload, *, with_response=True):
        return self.rest.request(
            "POST",
            f"/interactions/{interaction_id}/{interaction_token}/callback",
            json=payload,
            params={"with_response": int(bool(with_response))},
            auth=False,
        )

    def get_original(self, application_id, interaction_token):
        return self.rest.request(
            "GET",
            f"/webhooks/{application_id}/{interaction_token}/messages/@original",
            auth=False,
        )

    def edit_original(self, application_id, interaction_token, **fields):
        return self.rest.request(
            "PATCH",
            f"/webhooks/{application_id}/{interaction_token}/messages/@original",
            json=fields,
            auth=False,
        )

    def delete_original(self, application_id, interaction_token):
        return self.rest.request(
            "DELETE",
            f"/webhooks/{application_id}/{interaction_token}/messages/@original",
            auth=False,
        )

    def followup(self, application_id, interaction_token, content=None, *, wait=True, **fields):
        payload = dict(fields)
        if content is not None:
            payload["content"] = content
        return self.rest.request(
            "POST",
            f"/webhooks/{application_id}/{interaction_token}",
            json=payload,
            params={"wait": int(bool(wait))},
            auth=False,
        )
