from __future__ import annotations
from typing import AsyncIterator, Callable, Any

async def snowflake_after_pages(
    fetch_page: Callable[..., Any],
    *,
    page_size=100,
    cursor_key="after",
    item_id=lambda item: item["id"],
    **kwargs,
) -> AsyncIterator[dict]:
    cursor = kwargs.pop(cursor_key, None)
    while True:
        params = dict(kwargs)
        params["limit"] = page_size
        if cursor is not None:
            params[cursor_key] = cursor
        page = await fetch_page(**params)
        if not page:
            return
        for item in page:
            yield item
        if len(page) < page_size:
            return
        cursor = item_id(page[-1])

async def snowflake_before_pages(
    fetch_page: Callable[..., Any],
    *,
    page_size=100,
    cursor_key="before",
    item_id=lambda item: item["id"],
    **kwargs,
) -> AsyncIterator[dict]:
    cursor = kwargs.pop(cursor_key, None)
    while True:
        params = dict(kwargs)
        params["limit"] = page_size
        if cursor is not None:
            params[cursor_key] = cursor
        page = await fetch_page(**params)
        if not page:
            return
        for item in page:
            yield item
        if len(page) < page_size:
            return
        cursor = item_id(page[-1])
