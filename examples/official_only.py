import os
from discord_omni import DiscordClient, route_count

dc = DiscordClient(os.environ["DISCORD_BOT_TOKEN"])

print("Official route count:", route_count())
print(dc.official.names()[:20])

# Official route:
# me = dc.official.get_current_user()
# print(me)

# Unknown/private names are rejected:
# dc.official_request("some_private_api")
