import type { RequestOptions } from "./types.js";

export class DiscordRest {
  constructor(
    public token?: string,
    public apiBase = "https://discord.com/api/v10"
  ) {}

  async request<T = unknown>(
    method: string,
    path: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = new URL(this.apiBase + (path.startsWith("/") ? path : "/" + path));

    for (const [key, value] of Object.entries(options.params ?? {})) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }

    const headers: Record<string, string> = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "User-Agent": "discord-omni-sdk/1.0.0"
    };

    if (options.auth !== false && this.token) {
      headers["Authorization"] = `Bot ${this.token}`;
    }

    if (options.reason) {
      headers["X-Audit-Log-Reason"] = encodeURIComponent(options.reason);
    }

    const response = await fetch(url, {
      method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body)
    });

    if (response.status === 204) return undefined as T;

    const text = await response.text();
    const body = text ? JSON.parse(text) : undefined;

    if (!response.ok) {
      throw new Error(`Discord API ${response.status}: ${JSON.stringify(body)}`);
    }

    return body as T;
  }
}
