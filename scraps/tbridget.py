"""
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

try:
    from twitchio.ext import commands as twitch_commands
except ImportError:
    twitch_commands = None  # TwitchIO not installed

load_dotenv()
TWITCH_CHANNEL = os.getenv("TWITCH_USERNAME1")  # Twitch channel name (lowercase)
DISCORD_CHANNEL_ID = 1375784527581937684  # Replace with your Discord channel ID

class TwitchBridge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_bot = None

    async def cog_load(self):
        if twitch_commands:
            asyncio.create_task(self.start_twitch_bot())

    async def start_twitch_bot(self):
        if not twitch_commands:
            print("TwitchIO is not installed. Twitch bridge will not run.")
            return

        class TwitchBot(twitch_commands.Bot):
            def __init__(self, discord_bot):
                super().__init__(
                    irc_token=os.getenv("TWITCH_IRC_TOKEN"),
                    client_id=os.getenv("TWITCH_CLIENT_ID1"),
                    nick=os.getenv("TWITCH_USERNAME1"),
                    prefix="!",
                    initial_channels=[TWITCH_CHANNEL.lower()]
                )
                self.discord_bot = discord_bot

            async def event_message(self, message):
                if message.echo:
                    return
                discord_channel = self.discord_bot.get_channel(DISCORD_CHANNEL_ID)
                if discord_channel:
                    await discord_channel.send(f"[Twitch] {message.author.name}: {message.content}")

        self.twitch_bot = TwitchBot(self.bot)
        await self.twitch_bot.start()

async def setup(bot):
    await bot.add_cog(TwitchBridge(bot))
"""