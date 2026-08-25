# Omni Toolbox

`examples/omni_toolbox.py` is a small Discord utility bot built only with the public Discord API features exposed by `discord-omni`.

## Commands

- `/ping` — interaction response check
- `/about` — bot information
- `/snowflake id:<ID>` — decode a Discord Snowflake creation time
- `/user [target]` — show basic user information
- `/server` — show basic guild information
- `/invite` — generate the official Discord OAuth2 bot install URL

## Requirements

- Python 3.10+
- A Discord Application with a Bot
- The application's Bot Token
- Application ID
- Application Public Key

Install the package from the repository root:

```bash
python -m pip install -e .
```

No `.env` file is required. The example reads configuration from process environment variables so secrets do not need to be committed to Git.

## Windows PowerShell

```powershell
$env:DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
$env:DISCORD_APPLICATION_ID="YOUR_APPLICATION_ID"
$env:DISCORD_PUBLIC_KEY="YOUR_PUBLIC_KEY"
$env:DISCORD_GUILD_ID="YOUR_TEST_GUILD_ID"   # optional but recommended while developing
$env:PORT="8080"
python examples/omni_toolbox.py
```

`DISCORD_GUILD_ID` is optional. If it is present, commands are synchronized to that single guild. If it is omitted, the example synchronizes global application commands.

Set `DISCORD_SYNC_COMMANDS=0` if you want to start the interaction server without overwriting the currently registered command set.

## Discord Developer Portal

The interaction endpoint is:

```text
https://YOUR_PUBLIC_HOST/interactions
```

The URL must be publicly reachable over HTTPS for Discord to validate it. The app verifies Discord's Ed25519 request signature before handling an interaction.

Health endpoints:

```text
GET /
GET /health
```

## Hosting

The example listens on `0.0.0.0` by default and uses the `PORT` environment variable, so it can be deployed to common Python web hosts. The start command is:

```text
python examples/omni_toolbox.py
```

Do not commit the Bot Token or other secrets into the repository.

## Security model

Omni Toolbox uses Bot/Application credentials and Discord's documented public API. It does not use user tokens, self-bot automation, private client endpoints, or authentication bypasses.
