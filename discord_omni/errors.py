class DiscordError(RuntimeError):
    """Base package exception."""


class DiscordAPIError(DiscordError):
    def __init__(self, message, *, status=None, code=None, body=None, route=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.body = body
        self.route = route


class DiscordRateLimitError(DiscordAPIError):
    def __init__(self, message, *, retry_after=None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class DiscordAuthError(DiscordAPIError):
    pass


class GatewayError(DiscordError):
    pass
