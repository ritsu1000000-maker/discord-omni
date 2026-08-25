import os
from discord_omni import DiscordClient
from discord_omni.editor import EditorPolicy

client = DiscordClient(os.environ["DISCORD_BOT_TOKEN"])

editor = client.editor(os.environ["DISCORD_GUILD_ID"]).load()

editor.edit.set_guild(name="Omni Test")
editor.edit.create_text_channel("omni-news", topic="Created by discord-omni")

plan = editor.plan()
print("\n".join(plan.summaries()))

preview = editor.apply(dry_run=True)
print(preview.skipped)

# Uncomment only after checking the plan:
# result = editor.apply(
#     policy=EditorPolicy(max_destructive_operations=0),
#     reason="discord-omni editor test",
# )
