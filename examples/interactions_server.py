import os
from discord_omni import InteractionApp, Container, TextDisplay, ActionRow, Button

app = InteractionApp(os.environ["DISCORD_PUBLIC_KEY"])

@app.slash_command("hello")
async def hello(ctx):
    return ctx.reply("こんにちは！")

@app.slash_command("panel")
async def panel(ctx):
    return ctx.reply_components(
        Container([
            TextDisplay("# Control panel"),
            ActionRow([Button(label="実行", custom_id="run", style=1)]),
        ])
    )

@app.component("run")
async def run_button(ctx):
    return ctx.reply("実行しました", ephemeral=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
