import asyncio
import os

from discord_omni import (
    AsyncDiscordClient,
    Embed,
    Poll,
    PollAnswer,
    AllowedMentions,
    capabilities,
)

async def main():
    print(capabilities())

    async with AsyncDiscordClient(os.environ["DISCORD_BOT_TOKEN"]) as dc:
        me = await dc.official.get_current_user()
        print("Connected as:", me["username"])

        # await dc.send(
        #     "CHANNEL_ID",
        #     "Hello!",
        #     embeds=[Embed(title="Hello", description="Direct Discord API")],
        #     allowed_mentions=AllowedMentions.none(),
        # )

asyncio.run(main())
