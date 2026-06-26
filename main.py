import os
import re
import sys

import discord
from dotenv import load_dotenv

load_dotenv()

# Match http(s)://(www.)?(x|twitter).com/<path> URLs.
# Capture the host so we can replace it case-insensitively while keeping
# scheme, optional www, path and query intact. Stop the path at
# whitespace or delimiters that shouldn't be part of a URL.
X_URL_RE = re.compile(
    r"(?P<prefix>https?://(?:www\.)?)(?P<host>x|twitter)\.com(?P<suffix>/[^\s<>\"')\]]*)",
    re.IGNORECASE,
)


def rewrite_message(content: str) -> str | None:
    """Replace x.com/twitter.com hosts with fxtwitter.com.

    Returns the rewritten text, or None if no x/twitter URL was present.
    """
    if not X_URL_RE.search(content):
        return None

    def _swap(match: re.Match[str]) -> str:
        return f"{match.group('prefix')}fxtwitter.com{match.group('suffix')}"

    return X_URL_RE.sub(_swap, content)


class FxtwitterBot(discord.Client):
    def __init__(self) -> None:
        # We only need to read messages; content intent is required to see
        # the body of messages from other users.
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_message(self, message: discord.Message) -> None:
        # Ignore our own messages and messages from other bots.
        if message.author.bot:
            return

        rewritten = rewrite_message(message.content)
        if rewritten is None:
            return

        # Re-upload any attachments the original message carried so nothing
        # is lost besides the x.com link being swapped out.
        files: list[discord.File] = []
        for attachment in message.attachments:
            try:
                files.append(await attachment.to_file())
            except (discord.HTTPException, discord.DiscordException):
                # Skip attachments we fail to fetch; better to send the
                # rewritten text than nothing.
                pass

        # Mention the original author without actually pinging them:
        # allowed_mentions suppresses the notification while keeping the
        # mention visually clickable.
        mention = message.author.mention
        new_content = f"{mention}:\n{rewritten}"

        send_kwargs: dict = {
            "content": new_content,
            "allowed_mentions": discord.AllowedMentions.none(),
        }
        if files:
            send_kwargs["files"] = files
        # Carry over stickers by id where possible.
        if message.stickers:
            sticker_ids = [s.id for s in message.stickers if s.id is not None]
            if sticker_ids:
                send_kwargs["stickers"] = sticker_ids

        try:
            await message.channel.send(**send_kwargs)
        except discord.DiscordException:
            # If we can't send, leave the original message intact.
            return

        try:
            await message.delete()
        except discord.DiscordException:
            # Best effort: the replacement was already sent.
            pass


def main() -> None:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        sys.exit("DISCORD_BOT_TOKEN is not set. Put it in a .env file or export it in your shell.")

    client = FxtwitterBot()
    client.run(token)


if __name__ == "__main__":
    main()
