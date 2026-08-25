export class DiscordRest {
  constructor(token, apiBase = "https://discord.com/api/v10") {
    this.token = token;
    this.apiBase = apiBase;
  }

  async request(method, path, { body, params, auth = true } = {}) {
    const url = new URL(this.apiBase + (path.startsWith("/") ? path : "/" + path));
    for (const [k, v] of Object.entries(params || {})) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }

    const headers = { "Accept": "application/json", "Content-Type": "application/json" };
    if (auth && this.token) headers.Authorization = `Bot ${this.token}`;

    const res = await fetch(url, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body)
    });

    if (res.status === 204) return null;
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;
    if (!res.ok) throw new Error(`Discord API ${res.status}: ${JSON.stringify(data)}`);
    return data;
  }
}
