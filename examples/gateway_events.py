import asyncio, os
from discord_omni import DiscordGateway
from discord_omni.intents import GUILDS, GUILD_MESSAGES

gw = DiscordGateway(os.environ["DISCORD_BOT_TOKEN"], intents=GUILDS | GUILD_MESSAGES)

@gw.event("READY")
async def ready(data):
    print("READY:", data["user"]["username"])

@gw.event("MESSAGE_CREATE")
async def message(data):
    print(data.get("content"))

asyncio.run(gw.connect())
