# fxtwitter-bot

A Discord bot that rewrites `x.com` / `twitter.com` links to `fxtwitter.com` so they embed correctly in Discord.

## What it does

- Detects messages containing `x.com` or `twitter.com` URLs.
- Reposts the message with only the host swapped to `fxtwitter.com` (all other text, attachments, and stickers are preserved).
- Attributes the original author via a non-pinging mention (`@user:`).
- **Deletes** the original message by default (or **suppresses its embed** if configured via `/fxtwitterbot mode:suppress`).

## Commands

- `/fxtwitter` — Show link conversion stats for this server.
- `/fxtwitterbot mode:<Delete|Suppress>` — Configure how to handle the original message (per-guild setting).

## Setup

1. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Enable the **Message Content Intent** under Bot → Privileged Gateway Intents.
3. Copy `.env.example` to `.env` and set `DISCORD_BOT_TOKEN`.
4. Invite the bot to your server with both OAuth scopes:
   - `bot`
   - `applications.commands`
5. Give it the **View Channels**, **Send Messages**, **Manage Messages**, and **Embed Links** permissions.
6. Run locally:

```sh
uv run python main.py
```

Or with Docker:

```sh
docker compose up -d
```

## Configuration

| Env var | Description |
| --- | --- |
| `DISCORD_BOT_TOKEN` | The bot token from the Developer Portal. |
