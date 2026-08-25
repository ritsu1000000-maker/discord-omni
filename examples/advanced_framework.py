from discord_omni.advanced import (
    AdvancedDiscordApp,
    CooldownManager,
    SignedCustomID,
)

app = AdvancedDiscordApp(
    "BOT_TOKEN",
    application_id="APPLICATION_ID",
    intents=1,
)

ids = SignedCustomID("CHANGE_ME_TO_A_RANDOM_SECRET", namespace="panel")

@app.component(r"panel\.(?P<action>[a-z]+)\..+")
async def panel(ctx, action):
    return {"content": f"action={action}, user={ctx.user_id}"}

cooldown = CooldownManager(rate=1, per=3)

@app.routed_command("ping", cooldown=cooldown)
async def ping(ctx):
    return {"content": "pong"}

# app.run()
