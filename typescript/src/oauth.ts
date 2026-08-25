export function buildOAuthUrl(
  clientId: string,
  scopes: string[],
  options: {
    redirectUri?: string;
    state?: string;
    permissions?: string | number;
    guildId?: string;
  } = {}
): string {
  const url = new URL("https://discord.com/oauth2/authorize");
  url.searchParams.set("client_id", clientId);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("scope", scopes.join(" "));
  if (options.redirectUri) url.searchParams.set("redirect_uri", options.redirectUri);
  if (options.state) url.searchParams.set("state", options.state);
  if (options.permissions !== undefined) url.searchParams.set("permissions", String(options.permissions));
  if (options.guildId) url.searchParams.set("guild_id", options.guildId);
  return url.toString();
}
