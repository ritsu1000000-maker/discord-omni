import { DiscordClient } from "../../javascript/src/index.js";

const client = new DiscordClient(process.env.DISCORD_BOT_TOKEN);
console.log(await client.me());
