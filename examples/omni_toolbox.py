from __future__ import annotations

import os
from datetime import datetime, timezone

from aiohttp import web

from discord_omni import AsyncDiscordClient, InteractionApp, snowflake_time
from discord_omni.power_tools import build_bot_invite_url, timestamp_long_datetime, timestamp_relative


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = require_env("DISCORD_BOT_TOKEN")
APPLICATION_ID = require_env("DISCORD_APPLICATION_ID")
PUBLIC_KEY = require_env("DISCORD_PUBLIC_KEY")
GUILD_ID = os.getenv("DISCORD_GUILD_ID", "").strip() or None
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
SYNC_COMMANDS = os.getenv("DISCORD_SYNC_COMMANDS", "1").lower() not in {"0", "false", "no", "off"}


COMMANDS = [
    {
        "type": 1,
        "name": "ping",
        "description": "BotとDiscord Interactionの応答状態を確認します",
        "dm_permission": True,
    },
    {
        "type": 1,
        "name": "about",
        "description": "Omni Toolboxの情報を表示します",
        "dm_permission": True,
    },
    {
        "type": 1,
        "name": "snowflake",
        "description": "Discord IDから作成日時を調べます",
        "dm_permission": True,
        "options": [
            {
                "type": 3,
                "name": "id",
                "description": "調べるDiscord Snowflake ID",
                "required": True,
                "min_length": 15,
                "max_length": 22,
            }
        ],
    },
    {
        "type": 1,
        "name": "user",
        "description": "Discordユーザーの基本情報を表示します",
        "dm_permission": True,
        "options": [
            {
                "type": 6,
                "name": "target",
                "description": "表示するユーザー（省略時は自分）",
                "required": False,
            }
        ],
    },
    {
        "type": 1,
        "name": "server",
        "description": "現在のDiscordサーバーの基本情報を表示します",
        "dm_permission": False,
    },
    {
        "type": 1,
        "name": "invite",
        "description": "このBotを追加するための公式OAuth2 URLを表示します",
        "dm_permission": True,
    },
]


interactions = InteractionApp(PUBLIC_KEY)
discord = AsyncDiscordClient(BOT_TOKEN)


def option_value(ctx, name: str, default=None):
    for option in ctx.data.get("options") or []:
        if option.get("name") == name:
            return option.get("value", default)
    return default


def resolved_user(ctx, user_id: str | None):
    if user_id is None:
        return ctx.user or {}

    resolved = ctx.data.get("resolved") or {}
    users = resolved.get("users") or {}
    return users.get(str(user_id)) or {}


def display_username(user: dict) -> str:
    global_name = user.get("global_name")
    username = user.get("username") or "unknown"
    return global_name or username


@interactions.slash_command("ping")
async def ping(ctx):
    interaction_id = ctx.payload.get("id")
    latency_ms = None
    if interaction_id:
        try:
            created = snowflake_time(interaction_id)
            now = datetime.now(timezone.utc)
            latency_ms = max(0, int((now - created).total_seconds() * 1000))
        except Exception:
            latency_ms = None

    if latency_ms is None:
        return ctx.reply("🏓 Pong! Omni Toolbox is online.")
    return ctx.reply(f"🏓 Pong! Interaction latency: **{latency_ms} ms**")


@interactions.slash_command("about")
async def about(ctx):
    return ctx.reply(
        "🧰 **Omni Toolbox**\n"
        "`discord-omni` の公式Discord API機能だけで動くサンプルBotです。\n\n"
        "Commands: `/ping` `/about` `/snowflake` `/user` `/server` `/invite`"
    )


@interactions.slash_command("snowflake")
async def snowflake(ctx):
    raw_id = str(option_value(ctx, "id", "")).strip()
    if not raw_id.isdigit():
        return ctx.reply("Discord IDは数字だけを入力してください。", ephemeral=True)

    try:
        created = snowflake_time(raw_id)
    except Exception:
        return ctx.reply("そのIDをDiscord Snowflakeとして解析できませんでした。", ephemeral=True)

    return ctx.reply(
        "🕒 **Snowflake information**\n"
        f"ID: `{raw_id}`\n"
        f"Created: {timestamp_long_datetime(created)}\n"
        f"Relative: {timestamp_relative(created)}"
    )


@interactions.slash_command("user")
async def user(ctx):
    target_id = option_value(ctx, "target")
    user_data = resolved_user(ctx, str(target_id) if target_id is not None else None)

    if not user_data:
        return ctx.reply("ユーザー情報を取得できませんでした。", ephemeral=True)

    user_id = str(user_data.get("id") or target_id or "unknown")
    username = display_username(user_data)
    raw_username = user_data.get("username") or "unknown"
    is_bot = "yes" if user_data.get("bot") else "no"

    created_line = "unknown"
    if user_id.isdigit():
        try:
            created = snowflake_time(user_id)
            created_line = f"{timestamp_long_datetime(created)} ({timestamp_relative(created)})"
        except Exception:
            pass

    return ctx.reply(
        "👤 **User information**\n"
        f"Display name: **{username}**\n"
        f"Username: `{raw_username}`\n"
        f"ID: `{user_id}`\n"
        f"Bot: `{is_bot}`\n"
        f"Created: {created_line}"
    )


@interactions.slash_command("server")
async def server(ctx):
    guild_id = ctx.guild_id
    if not guild_id:
        return ctx.reply("このコマンドはDiscordサーバー内で使ってください。", ephemeral=True)

    try:
        guild = await discord.official.get_guild(guild_id=str(guild_id))
    except Exception as exc:
        return ctx.reply(
            f"サーバー情報の取得に失敗しました: `{type(exc).__name__}`",
            ephemeral=True,
        )

    name = guild.get("name") or "unknown"
    owner_id = guild.get("owner_id") or "unknown"
    verification_level = guild.get("verification_level", "unknown")
    premium_tier = guild.get("premium_tier", "unknown")

    return ctx.reply(
        "🏠 **Server information**\n"
        f"Name: **{name}**\n"
        f"ID: `{guild_id}`\n"
        f"Owner ID: `{owner_id}`\n"
        f"Verification level: `{verification_level}`\n"
        f"Boost tier: `{premium_tier}`"
    )


@interactions.slash_command("invite")
async def invite(ctx):
    url = build_bot_invite_url(APPLICATION_ID, permissions=0)
    return ctx.reply(
        "🔗 **Bot install URL**\n"
        f"{url}\n\n"
        "必要な権限は、Botに実際に追加する機能に合わせてDeveloper Portal側で設定してください。",
        ephemeral=True,
    )


async def on_startup(app: web.Application):
    await discord.rest.open()

    if not SYNC_COMMANDS:
        print("[omni-toolbox] command sync disabled")
        return

    if GUILD_ID:
        await discord.official.bulk_overwrite_guild_commands(
            application_id=APPLICATION_ID,
            guild_id=GUILD_ID,
            json=COMMANDS,
        )
        print(f"[omni-toolbox] synced {len(COMMANDS)} guild commands to {GUILD_ID}")
    else:
        await discord.official.bulk_overwrite_global_commands(
            application_id=APPLICATION_ID,
            json=COMMANDS,
        )
        print(f"[omni-toolbox] synced {len(COMMANDS)} global commands")


async def on_cleanup(app: web.Application):
    await discord.rest.close()


async def health(request: web.Request):
    return web.json_response(
        {
            "ok": True,
            "service": "omni-toolbox",
            "commands": [command["name"] for command in COMMANDS],
            "scope": "guild" if GUILD_ID else "global",
        }
    )


async def home(request: web.Request):
    return web.Response(
        text="Omni Toolbox is running. POST Discord interactions to /interactions",
        content_type="text/plain",
    )


def build_web_app() -> web.Application:
    app = interactions.aiohttp_app(path="/interactions")
    app.router.add_get("/", home)
    app.router.add_get("/health", health)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


if __name__ == "__main__":
    web.run_app(build_web_app(), host=HOST, port=PORT)
