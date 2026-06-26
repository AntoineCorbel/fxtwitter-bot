import os
import re
from datetime import datetime
from pathlib import Path

import discord
from dotenv import load_dotenv

load_dotenv()

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


class FxtwitterBot(discord.Client):
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.content.lower() == "/fxtwitter stats":
            stats = self.get_guild_stats(str(message.guild.id))
            await message.channel.send(
                f"Stats for **{message.guild.name}**: Total {stats['conversions']}, Today {stats['today']}"
            )
            return

        rewritten = rewrite_message(message.content)
        if rewritten:
            await message.channel.send(f"{message.author.mention}:\n{rewritten}")
            self.record_conversion(str(message.guild.id), str(message.id), rewritten)
            try:
                await message.delete()
            except discord.HTTPException:
                pass

    def get_guild_stats(self, guild_id: str):
        data = {}
        f = Path(".fxtwitter_stats.json")
        if f.exists():
            data = eval(f.read_text())
        if guild_id not in data:
            data[guild_id] = {"conversions": 0, "today": 0, "day": None}
        g = data[guild_id]
        if g["day"] != datetime.now().date():
            g["today"] = 0
            g["day"] = datetime.now().date()
        f.write_text(str(data))
        return g

    def record_conversion(self, guild_id: str, message_id: str, rewritten: str):
        data = {}
        f = Path(".fxtwitter_stats.json")
        if f.exists():
            data = eval(f.read_text())
        if guild_id not in data:
            data[guild_id] = {"conversions": 0, "today": 0, "day": None}
        data[guild_id]["conversions"] += 1
        data[guild_id]["today"] += 1
        f.write_text(str(data))


def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("DISCORD_BOT_TOKEN not set")
        return
    FxtwitterBot().run(token)


if __name__ == "__main__":
    main()
