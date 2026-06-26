import json
import os
import re
from datetime import datetime
from pathlib import Path

import discord
from dotenv import load_dotenv

load_dotenv()

STATS_FILE = Path(".fxtwitter_stats.json")

X_URL_RE = re.compile(
    r"(?P<prefix>https?://(?:www\.)?)(?P<host>x|twitter)\.com(?P<suffix>/[^\s<>\"')\]]*)",
    re.IGNORECASE,
)


def rewrite_message(content: str) -> str | None:
    if not X_URL_RE.search(content):
        return None

    def _swap(m):
        return f"{m.group('prefix')}fxtwitter.com{m.group('suffix')}"

    return X_URL_RE.sub(_swap, content)


def _load_stats() -> dict:
    if STATS_FILE.exists():
        return json.loads(STATS_FILE.read_text())
    return {}


def _guild_entry(data: dict, guild_id: str) -> dict:
    if guild_id not in data:
        data[guild_id] = {"conversions": 0, "today": 0, "day": None}
    g = data[guild_id]
    today = datetime.now().date().isoformat()
    if g["day"] != today:
        g["today"] = 0
        g["day"] = today
    return g


class FxtwitterBot(discord.Client):
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.content.lower() == "/fxtwitter stats":
            data = _load_stats()
            g = _guild_entry(data, str(message.guild.id))
            STATS_FILE.write_text(json.dumps(data))
            await message.channel.send(
                f"Stats for **{message.guild.name}**: Total {g['conversions']}, Today {g['today']}"
            )
            return

        rewritten = rewrite_message(message.content)
        if rewritten:
            await message.channel.send(f"{message.author.mention}:\n{rewritten}")
            data = _load_stats()
            g = _guild_entry(data, str(message.guild.id))
            g["conversions"] += 1
            g["today"] += 1
            STATS_FILE.write_text(json.dumps(data))
            try:
                await message.delete()
            except discord.HTTPException:
                pass


def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("DISCORD_BOT_TOKEN not set")
        return
    FxtwitterBot().run(token)


if __name__ == "__main__":
    main()
