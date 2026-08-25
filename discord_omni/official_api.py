from __future__ import annotations
import inspect
import string
from urllib.parse import quote

from .official_routes import OFFICIAL_ROUTES, get_route

_FMT = string.Formatter()

def _format_path(template: str, values: dict) -> tuple[str, dict]:
    field_names = [name for _, name, _, _ in _FMT.parse(template) if name]
    path_values = {}
    remaining = dict(values)
    for name in field_names:
        if name not in remaining:
            raise TypeError(f"Missing route parameter: {name}")
        path_values[name] = remaining.pop(name)
    encoded = {k: quote(str(v), safe="") for k, v in path_values.items()}
    return template.format(**encoded), remaining

class OfficialAPI:
    """Sync facade restricted to known public routes mirrored from discord.py."""

    def __init__(self, rest):
        self._rest = rest

    def names(self):
        return tuple(sorted(OFFICIAL_ROUTES))

    def spec(self, name):
        return get_route(name)

    def call(self, name, *, params=None, json=None, data=None, files=None,
             headers=None, reason=None, **route_params):
        spec = get_route(name)
        path, extras = _format_path(spec.path, route_params)
        if extras:
            raise TypeError(f"Unexpected route parameters for {name}: {', '.join(extras)}")
        return self._rest.request(
            spec.method, path, params=params, json=json, data=data, files=files,
            headers=headers, reason=reason, auth=spec.auth,
        )

    def __getattr__(self, name):
        if name not in OFFICIAL_ROUTES:
            raise AttributeError(name)
        def invoke(*, params=None, json=None, data=None, files=None,
                   headers=None, reason=None, **route_params):
            return self.call(
                name, params=params, json=json, data=data, files=files,
                headers=headers, reason=reason, **route_params
            )
        invoke.__name__ = name
        invoke.__doc__ = f"Official Discord API route: {OFFICIAL_ROUTES[name].method} {OFFICIAL_ROUTES[name].path}"
        return invoke

class AsyncOfficialAPI:
    """Async facade restricted to known public routes mirrored from discord.py."""

    def __init__(self, rest):
        self._rest = rest

    def names(self):
        return tuple(sorted(OFFICIAL_ROUTES))

    def spec(self, name):
        return get_route(name)

    async def call(self, name, *, params=None, json=None, data=None, files=None,
                   headers=None, reason=None, **route_params):
        spec = get_route(name)
        path, extras = _format_path(spec.path, route_params)
        if extras:
            raise TypeError(f"Unexpected route parameters for {name}: {', '.join(extras)}")
        return await self._rest.request(
            spec.method, path, params=params, json=json, data=data, files=files,
            headers=headers, reason=reason, auth=spec.auth,
        )

    def __getattr__(self, name):
        if name not in OFFICIAL_ROUTES:
            raise AttributeError(name)
        async def invoke(*, params=None, json=None, data=None, files=None,
                         headers=None, reason=None, **route_params):
            return await self.call(
                name, params=params, json=json, data=data, files=files,
                headers=headers, reason=reason, **route_params
            )
        invoke.__name__ = name
        invoke.__doc__ = f"Official Discord API route: {OFFICIAL_ROUTES[name].method} {OFFICIAL_ROUTES[name].path}"
        return invoke
