# discord-omni 1.1.0 STATE EDITOR

`discord-omni-api` は、Discordの公開Bot/Application APIをPythonから扱うためのSDKです。

単なるAPIラッパーではなく、v1.1.0からは **State Editor** を追加しています。

```text
Discord Guild
  ↓ load()
Snapshot
  ↓ edit
Desired State
  ↓ plan()
Diff / EditPlan
  ↓ dry-run / policy
Validation
  ↓ apply()
Discord Official Bot API
```

## Install

```bash
pip install discord-omni-api
```

ローカルwheelから入れる場合:

```bash
pip install discord_omni_api-1.1.0-py3-none-any.whl
```

## Basic

```python
from discord_omni import DiscordClient

client = DiscordClient("BOT_TOKEN")
me = client.official.get_current_user()
print(me)
```

## State Editor

```python
from discord_omni import DiscordClient
from discord_omni.editor import EditorPolicy

client = DiscordClient("BOT_TOKEN")
editor = client.editor("GUILD_ID").load()

editor.edit.set_guild(name="My Server")
editor.edit.create_text_channel("news", topic="お知らせ")
editor.edit.create_role("Moderator", permissions="0")

plan = editor.plan()
for line in plan.summaries():
    print(line)

# まず変更せず確認
preview = editor.apply(dry_run=True)

# 削除を許可しない状態で反映
result = editor.apply(
    policy=EditorPolicy(
        allow_delete_channels=False,
        allow_delete_roles=False,
        max_destructive_operations=0,
    ),
    reason="discord-omni state editor",
)
```

## Editor features

- Guild snapshot
- Guild settings editing
- Channel create / edit / delete / clone
- Role create / edit / delete / clone / move
- Declarative diff engine
- EditPlan
- Dry-run
- Destructive-operation policy
- JSON snapshot export / import
- Sync / Async editor
- Channel permission overwrite helpers
- Member nickname / role / voice helpers
- AutoMod editor
- CLI snapshot diff

## CLI

```bash
discord-omni info
discord-omni routes --search webhook
discord-omni features --search oauth
discord-omni snapshot-diff current.json desired.json
```

## Existing SDK layers

- Sync / Async REST
- Gateway v10
- Sharding
- Webhooks
- OAuth2 / PKCE
- Interactions
- Slash / User / Message Commands
- Components V2
- Embed / Poll builders
- Permissions
- Snowflakes
- AutoMod
- Scheduled Events
- Soundboard
- Emoji / Sticker
- SKUs / Entitlements / Subscriptions
- Top.gg community integration
- Advanced Router / Middleware / State / Cache / Metrics / Plugins
- 217 Power Helpers
- 201 registered public REST route definitions

## Scope

このライブラリはDiscordの公開Bot/Application APIと、Botに付与された権限の範囲で動作します。

含まないもの:

- self-bot
- user token automation
- Discord private/internal client API
- CAPTCHA/認証回避
- 権限回避

## Package

- PyPI name: `discord-omni-api`
- Import: `discord_omni`
- Python: `>=3.10`
- License: MIT
