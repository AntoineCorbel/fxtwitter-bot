# fxtwitter-bot

A Discord bot that rewrites `x.com` / `twitter.com` links to `fxtwitter.com` so they embed correctly in Discord.

## What it does

- Detects messages containing `x.com` or `twitter.com` URLs.
- Reposts the message with only the host swapped to `fxtwitter.com` — all other text, attachments, and stickers are preserved.
- Attributes the original author via a non-pinging mention (`@user:`).
- Deletes the original message.

## Setup

1. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Enable the **Message Content Intent** under Bot → Privileged Gateway Intents.
3. Copy `.env.example` to `.env` and set `DISCORD_BOT_TOKEN`.
4. Invite the bot to your server with the **Send Messages**, **Manage Messages**, **Embed Links**, and **Attach Files** permissions.
5. Run:

```sh
uv run python main.py
```

## Configuration

| Env var | Description |
| --- | --- |
| `DISCORD_BOT_TOKEN` | The bot token from the Developer Portal. |
