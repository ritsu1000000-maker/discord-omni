import { DiscordRest } from "./rest.js";

export class DiscordClient {
  constructor(token) {
    this.rest = new DiscordRest(token);
  }

  me() {
    return this.rest.request("GET", "/users/@me");
  }

  guild(id) {
    return this.rest.request("GET", `/guilds/${id}`);
  }

  send(channelId, content) {
    return this.rest.request("POST", `/channels/${channelId}/messages`, {
      body: { content }
    });
  }
}
