from __future__ import annotations
from datetime import datetime, timezone

DISCORD_EPOCH_MS = 1420070400000

def snowflake_time(snowflake: int | str) -> datetime:
    sid = int(snowflake)
    ms = (sid >> 22) + DISCORD_EPOCH_MS
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)

def snowflake_from_datetime(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ms = int(dt.timestamp() * 1000)
    return (ms - DISCORD_EPOCH_MS) << 22

def worker_id(snowflake: int | str) -> int:
    return (int(snowflake) & 0x3E0000) >> 17

def process_id(snowflake: int | str) -> int:
    return (int(snowflake) & 0x1F000) >> 12

def increment(snowflake: int | str) -> int:
    return int(snowflake) & 0xFFF
