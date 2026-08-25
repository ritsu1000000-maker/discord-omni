import { DiscordClient } from "../../typescript/src/index.js";

const client = new DiscordClient(process.env.DISCORD_BOT_TOKEN);
const me = await client.getCurrentUser();
console.log(me.username);
