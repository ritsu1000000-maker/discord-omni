# discord-omni 1.0.1 PyPI SDK

Discord公式APIを `discord.py` なしで直接扱うためのPythonパッケージです。

## 0.6.0: official-only

この版では「非公式APIを使わない」ことを明確にするため、
`Rapptz/discord.py` の公開GitHub実装で確認した公式Discord APIルートを
`OFFICIAL_ROUTES` にまとめています。

基準:
- `discord/http.py`
- `discord/webhook/async_.py`
- `discord/gateway.py`
- REST: `https://discord.com/api/v10`
- Gateway: `wss://gateway.discord.gg/`

private client API / self-bot / user token 自動化用エンドポイントは追加していません。

## 公式ルートだけを呼ぶ

```python
from discord_omni import DiscordClient

dc = DiscordClient("BOT_TOKEN")

print(len(dc.official.names()))

guild = dc.official.get_guild(
    guild_id="GUILD_ID"
)

dc.official.create_message(
    channel_id="CHANNEL_ID",
    json={"content": "hello"}
)
```

存在しないルート名:

```python
dc.official.some_private_api(...)
```

は `AttributeError` になります。

また:

```python
dc.official_request("unknown_route")
```

も拒否されます。

## Async

```python
import asyncio
from discord_omni import AsyncDiscordClient

async def main():
    async with AsyncDiscordClient("BOT_TOKEN") as dc:
        me = await dc.official.get_current_user()
        print(me)

asyncio.run(main())
```

## 追加した公式カテゴリ

- Gateway / Bot Gateway
- Current User / User / DM
- Messages / modern Pins / Reactions
- Channels / Permission Overwrites / Voice Channel Status
- Threads / archived threads
- Guilds / Guild MFA / Vanity URL / Widget / Incident Actions
- Members / Bans / Bulk Ban / Prune / Voice States
- Roles / Role Member Counts
- Invites
- Guild Templates
- Welcome Screen
- Guild Onboarding
- Integrations
- Guild Emojis / Application Emojis
- Stickers / Sticker Packs
- Webhooks
- Interaction Callback / Original Interaction Response / Followups
- Application Commands
- Command Permissions
- Auto Moderation
- Stage Instances
- Scheduled Events + Event Users
- Soundboard
- Poll voters / Poll end
- SKUs / Entitlements / Subscriptions
- Components V2
- OAuth2
- Gateway events / zlib-stream / resume / reconnect / sharding

## Components V2

```python
from discord_omni import Container, TextDisplay, ActionRow, Button

ui = Container([
    TextDisplay("# Panel"),
    ActionRow([
        Button(label="OK", custom_id="ok", style=1)
    ])
])
```

## Interaction server

```python
from discord_omni import InteractionApp

app = InteractionApp("APPLICATION_PUBLIC_KEY")

@app.slash_command("hello")
async def hello(ctx):
    return ctx.reply("こんにちは")

app.run(host="0.0.0.0", port=8080)
```

## 注意

「何でも」はDiscordが公開しているAPIと、そのBot/Application/OAuth2認可に
与えられた権限の範囲です。Discord APIに存在しない操作、認証回避、self-botは含みません。

discord.pyそのものを同梱・コピーしているわけではありません。
GitHub実装の公開ルート構成を参照し、独立したAPIラッパーとして実装しています。


## 0.6.1: community extension

公式Discord API本体は引き続き `official-only` のままです。

追加した非公式連携は `discord_omni.community` に隔離しています。
現在は **Top.gg v1** のみです。

```python
from discord_omni.community import TopGGClient

topgg = TopGGClient("TOPGG_TOKEN")

project = topgg.get_project()
print(project["name"])

topgg.post_metrics(
    server_count=123,
    shard_count=2,
)
```

Top.gg上のコマンド表示も更新できます。

```python
topgg.push_commands([
    {
        "name": "ping",
        "description": "Replies with Pong!"
    }
])
```

これはDiscordへSlash Commandを登録する処理ではありません。
Discordへの登録は `DiscordClient` の公式Application Commands APIを使います。

### Top.gg Webhook

```python
from discord_omni.community import TopGGClient

event = TopGGClient.parse_webhook(payload)

if event.is_vote:
    print(event.discord_user_id)
    print(event.vote_weight)
```

### 分離ポリシー

- `discord_omni.official` / `OFFICIAL_ROUTES` → Discord公式APIのみ
- `discord_omni.community` → 外部コミュニティサービス
- Discordのprivate client API → 非対応
- self-bot / user-token自動操作 → 非対応


## 0.7.0 MAX

「Discordで普通に作れるものを、このパッケージだけで組みやすくする」ための層を追加しました。

### 1つのAppでBotを動かす

```python
from discord_omni import DiscordApp
from discord_omni.intents import GUILDS, GUILD_MESSAGES

app = DiscordApp(
    "BOT_TOKEN",
    application_id="APPLICATION_ID",
    intents=GUILDS | GUILD_MESSAGES,
)

@app.event("READY")
async def ready(data):
    print("READY:", data["user"]["username"])

app.run()
```

### Embed

```python
from discord_omni import Embed

embed = (
    Embed(title="Status", description="Online", color=0x57F287)
    .add_field("Servers", "123", inline=True)
    .set_footer("discord-omni-api")
)

await client.send("CHANNEL_ID", embeds=[embed])
```

### Poll

```python
from discord_omni import Poll, PollAnswer

poll = Poll(
    "どっち？",
    [
        PollAnswer("A"),
        PollAnswer("B"),
    ],
    duration=24,
)

await client.send("CHANNEL_ID", poll=poll)
```

### Mentions制御

```python
from discord_omni import AllowedMentions

await client.send(
    "CHANNEL_ID",
    "通知しないメッセージ",
    allowed_mentions=AllowedMentions.none(),
)
```

### Permission

```python
from discord_omni import Permissions

perms = Permissions.from_names(
    "VIEW_CHANNEL",
    "SEND_MESSAGES",
    "EMBED_LINKS",
)

print(perms.to_int())
```

### Snowflake

```python
from discord_omni import snowflake_time

print(snowflake_time("123456789012345678"))
```

### 公式ルートの一覧

```python
from discord_omni import capabilities

print(capabilities())
```

`OFFICIAL_ROUTE_SNAPSHOT.json` には、この版に登録した公式RESTルートのスナップショットも入っています。

### discord.pyとの差分確認

`Rapptz/discord.py` をローカルにclone済みなら:

```powershell
python tools\sync_discordpy_routes.py C:\path\to\discord.py
```

で `discord/http.py` とWebhook HTTP実装から `Route(...)` を抽出し、
`discordpy-route-snapshot.json` を生成できます。

これでDiscord側やdiscord.py側に新しい公式ルートが増えたときも、
手作業だけに頼らず差分を確認できます。

## 対象外

- Discordのprivate/internal client API
- user tokenを使うself-bot
- 認証回避
- CAPTCHA回避
- spam / mass-DM用の最適化

Discord公式APIに存在する操作でも、実行にはBot/Applicationの権限が必要です。


## 0.8.0 ULTRA

新たに **217個のPower Helper** を追加しました。

```python
from discord_omni import power_tools as p

print(p.mention_user("123456789012345678"))
print(p.timestamp_relative(1735689600))

permissions = p.permission_value(
    "VIEW_CHANNEL",
    "SEND_MESSAGES",
)

invite = p.build_bot_invite_url(
    "APPLICATION_ID",
    permissions=permissions,
)

command = p.slash_command(
    "hello",
    "挨拶します",
    options=[
        p.string_option("name", "名前")
    ],
)
```

`POWER_FEATURES.md` に追加機能を全件掲載しています。

主な追加分野:
- Discordメンション / Timestamp / Markdown
- Snowflake操作
- Permissions / Permission Overwrite
- OAuth2 / PKCE / Install URL
- Application Command Builder
- Message / Poll / Flags / Allowed Mentions
- Components V2 Builder
- Webhook Utility
- Discord CDN URL Builder
- 公式Route検索 / 統計
- Interaction Payload Parser
- Validators
- Channel / Forum / Thread / Invite Builder
- Scheduled Event Builder
- AutoMod Builder
- Guild / User / Channel object helpers

公式API本体とTop.ggの分離方針はそのままです。


## 0.9.0 ADVANCED

0.8.0までは「APIと便利関数をたくさん持つSDK」でした。
0.9.0では、それらを組み合わせるための高度なフレームワーク層を追加しています。

### Signed custom_id

Buttonの`custom_id`に状態を埋め込みつつ、HMAC署名で改ざんを検出できます。

```python
from discord_omni.advanced import SignedCustomID

codec = SignedCustomID("SECRET", namespace="shop")

custom_id = codec.encode(
    "buy",
    product="abc",
    page=2,
)

data = codec.decode(custom_id)
```

### Component Router

```python
@app.component(r"shop\.(?P<action>[a-z]+)\..+")
async def shop_button(ctx, action):
    return {"content": f"action={action}"}
```

### Cooldown

```python
from discord_omni.advanced import CooldownManager

cooldown = CooldownManager(rate=1, per=5)

@app.routed_command("ping", cooldown=cooldown)
async def ping(ctx):
    return {"content": "pong"}
```

### Event Bus

```python
from discord_omni.advanced import EventBus

bus = EventBus()

@bus.on("ready", priority=100)
async def first(data):
    print("first")

@bus.once("ready")
async def only_once(data):
    print("once")
```

### State

```python
await app.state.set(
    ("wizard", user_id),
    {"step": 2},
    ttl=600,
)

state = await app.state.get(("wizard", user_id))
```

### Permission Resolver

Guild rolesとChannel permission overwritesを合成して、
そのメンバーの実効権限を計算できます。

### Plugin System

機能を別Pythonモジュールに分離して、ロード/アンロードできます。

### Testing

実Discordへ接続せずにAPI呼び出しやInteractionをテストするための
`FakeREST` / `AsyncFakeREST` / `interaction_fixture()` を追加しています。

つまり0.9.0は、

```text
Discord API
   ↓
REST / Gateway / Webhook / Interaction
   ↓
Router / Middleware / Permission Resolver
   ↓
Cooldown / State / Cache / Metrics
   ↓
Plugin / Application Logic
```

という多層構造で組めるようになっています。


## 1.0.0 MEGA SDK

Pythonだけの構成から、複数言語・複数レイヤーのDiscord開発キットへ拡張しました。

```text
python SDK
typescript SDK
javascript SDK
CLI
OpenAPI
JSON Schema
protocol registry
Docker
PowerShell/Bash scripts
GitHub Actions
generated registries
documentation
```

`discord_omni/` の既存Python機能はそのまま残しています。
### CLI

```powershell
python -m cli.main info
python -m cli.main routes --search webhook
```

### TypeScript

```powershell
cd typescript
npm install
npm run check
```

### JavaScript

```javascript
import { DiscordClient } from "./javascript/src/index.js";
```

秘密情報をフロントエンドへ埋め込む設計にはしていません。
Discord private/internal APIやself-botも追加していません。


## 1.0.1 PyPI SDK

PyPIパッケージ用途に合わせて、HTML/CSS/ブラウザ管理画面を削除しました。

残しているもの:
- Python SDK本体
- Advanced framework
- Community integrations
- CLI
- TypeScript / JavaScript参考SDK
- JSON Schema
- OpenAPI
- Protocol定義
- Config
- Docker(Python)
- PowerShell / Bash scripts
- Docs
- Tests
- Generated route/feature registries

ブラウザUIやHTMLファイルは含みません。
