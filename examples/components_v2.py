import os
from discord_omni import DiscordClient, Container, TextDisplay, ActionRow, Button

dc = DiscordClient(os.environ["DISCORD_BOT_TOKEN"])

ui = Container([
    TextDisplay("# Discord Omni"),
    TextDisplay("Components V2 test"),
    ActionRow([
        Button(label="OK", custom_id="ok", style=3),
        Button(label="Cancel", custom_id="cancel", style=4),
    ]),
])

# dc.send_components_v2("CHANNEL_ID", ui)
print(ui.to_dict())
