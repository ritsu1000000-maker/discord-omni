# Discord Omni State Editor

`discord_omni.editor` はDiscordサーバーを宣言的に編集するための層です。

流れ:

```text
Discord Guild
  ↓ snapshot
GuildSnapshot
  ↓ edit
Desired Snapshot
  ↓ diff
EditPlan
  ↓ policy
Validated Plan
  ↓ apply
Discord official Bot API
```

## 例

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

result = editor.apply(dry_run=True)
result = editor.apply(
    policy=EditorPolicy(
        allow_delete_channels=False,
        allow_delete_roles=False,
        max_destructive_operations=0,
    ),
    reason="discord-omni state editor",
)
```

Bot自身が持たない権限、ロール階層より上の対象、Discord側で禁止される変更は適用できません。
