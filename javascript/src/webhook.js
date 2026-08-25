export class DiscordWebhook {
  constructor(url) {
    this.url = url;
  }

  async send(content, extra = {}) {
    const res = await fetch(`${this.url}?wait=true`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, ...extra })
    });
    if (!res.ok) throw new Error(`Webhook HTTP ${res.status}`);
    return res.json();
  }
}
