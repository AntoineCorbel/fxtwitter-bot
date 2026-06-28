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
        data[guild_id] = {"conversions": 0, "today": 0, "day": None, "mode": "delete"}
    data[guild_id].setdefault("mode", "delete")
    g = data[guild_id]
    today = datetime.now().date().isoformat()
    if g["day"] != today:
        g["today"] = 0
        g["day"] = today
    return g


class FxtwitterBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

        @self.tree.command(
            name="fxtwitter", description="Show link conversion stats for this server"
        )
        async def stats(interaction: discord.Interaction):
            data = _load_stats()
            g = _guild_entry(data, str(interaction.guild_id))
            STATS_FILE.write_text(json.dumps(data))
            await interaction.response.send_message(
                f"Stats for **{interaction.guild.name}**: Total {g['conversions']}, Today {g['today']}"
            )

        @self.tree.command(
            name="fxtwitterbot",
            description="Choose what happens to the original message",
        )
        @discord.app_commands.describe(mode="How to handle the original message")
        @discord.app_commands.choices(
            mode=[
                discord.app_commands.Choice(name="Delete original message", value="delete"),
                discord.app_commands.Choice(
                    name="Keep message, remove its embed", value="suppress"
                ),
            ]
        )
        async def settings(
            interaction: discord.Interaction,
            mode: discord.app_commands.Choice[str],
        ):
            data = _load_stats()
            g = _guild_entry(data, str(interaction.guild_id))
            g["mode"] = mode.value
            STATS_FILE.write_text(json.dumps(data))
            await interaction.response.send_message(f"Mode set to **{mode.name}**.")

    async def on_ready(self):
        cmds = self.tree.get_commands()
        print(f"[on_ready] tree has {len(cmds)} commands: {[c.name for c in cmds]}", flush=True)
        try:
            synced = await self.tree.sync()
            print(
                f"[on_ready] synced {len(synced)} commands: {[c.name for c in synced]}", flush=True
            )
            Path("/app/debug.txt").write_text(
                f"tree_cmds={[c.name for c in cmds]}\nsynced={[c.name for c in synced]}\n"
            )
        except Exception as e:
            print(f"[on_ready] sync FAILED: {type(e).__name__}: {e}", flush=True)
            Path("/app/debug.txt").write_text(
                f"tree_cmds={[c.name for c in cmds]}\nsync_error={type(e).__name__}: {e}\n"
            )

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
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
                if g["mode"] == "suppress":
                    await message.edit(suppress=True)
                else:
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
