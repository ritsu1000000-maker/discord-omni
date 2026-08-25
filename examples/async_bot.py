import asyncio, os
from discord_omni import AsyncDiscordClient

async def main():
    async with AsyncDiscordClient(os.environ["DISCORD_BOT_TOKEN"]) as dc:
        me = await dc.get_current_user()
        print(me["username"])
        # await dc.send_message("CHANNEL_ID", "Hello from direct async API!")

asyncio.run(main())
