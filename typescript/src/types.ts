export type Snowflake = string;

export interface DiscordUser {
  id: Snowflake;
  username: string;
  global_name?: string | null;
  avatar?: string | null;
  bot?: boolean;
}

export interface DiscordGuild {
  id: Snowflake;
  name: string;
  owner_id?: Snowflake;
  icon?: string | null;
}

export interface DiscordMessage {
  id: Snowflake;
  channel_id: Snowflake;
  content: string;
  author: DiscordUser;
}

export interface RequestOptions {
  params?: Record<string, string | number | boolean | undefined>;
  body?: unknown;
  reason?: string;
  auth?: boolean;
}
