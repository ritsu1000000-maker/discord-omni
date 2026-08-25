import { DiscordRest } from "./rest.js";
import type { DiscordGuild, DiscordMessage, DiscordUser, Snowflake } from "./types.js";

export class DiscordClient {
  rest: DiscordRest;

  constructor(token?: string) {
    this.rest = new DiscordRest(token);
  }

  getCurrentUser() {
    return this.rest.request<DiscordUser>("GET", "/users/@me");
  }

  getGuild(guildId: Snowflake) {
    return this.rest.request<DiscordGuild>("GET", `/guilds/${guildId}`);
  }

  getMessage(channelId: Snowflake, messageId: Snowflake) {
    return this.rest.request<DiscordMessage>("GET", `/channels/${channelId}/messages/${messageId}`);
  }

  sendMessage(channelId: Snowflake, content: string) {
    return this.rest.request<DiscordMessage>("POST", `/channels/${channelId}/messages`, {
      body: { content }
    });
  }

  createRole(guildId: Snowflake, body: Record<string, unknown>) {
    return this.rest.request("POST", `/guilds/${guildId}/roles`, { body });
  }

  createChannel(guildId: Snowflake, body: Record<string, unknown>) {
    return this.rest.request("POST", `/guilds/${guildId}/channels`, { body });
  }
}
