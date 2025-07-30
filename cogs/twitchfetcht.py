import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import re

# Load .env
load_dotenv()
TWITCH_CLIENT_ID1 = os.getenv("TWITCH_CLIENT_ID1")
TWITCH_CLIENT_SECRET1 = os.getenv("TWITCH_CLIENT_SECRET1")
TWITCH_USERNAME1 = os.getenv("TWITCH_USERNAME1")
if TWITCH_USERNAME1:
    TWITCH_USERNAME1 = TWITCH_USERNAME1.lower()
else:
    raise ValueError("TWITCH_USERNAME1 is not set in the .env file")

class TwitchStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = None
        self.token_expiry = None

    async def get_token(self):
        if self.token and self.token_expiry and datetime.now(timezone.utc) < self.token_expiry:
            return self.token

        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": TWITCH_CLIENT_ID1,
            "client_secret": TWITCH_CLIENT_SECRET1,
            "grant_type": "client_credentials"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as resp:
                data = await resp.json()
                self.token = data["access_token"]
                self.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])
                return self.token

    async def get_user(self, session, token):
        headers = {
            "Client-ID": TWITCH_CLIENT_ID1,
            "Authorization": f"Bearer {token}"
        }
        async with session.get(f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME1}", headers=headers) as resp:
            data = await resp.json()
            if not data.get("data"):
                print("Twitch API user response:", data)
            return data["data"][0] if data.get("data") else None

    async def get_followers(self, session, token, user_id):
        headers = {
            "Client-ID": TWITCH_CLIENT_ID1,
            "Authorization": f"Bearer {token}"
        }
        url = f"https://api.twitch.tv/helix/users/follows?to_id={user_id}"
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            if data.get("total", 0) == 0:
                print("Twitch API followers response:", data)
            return int(data.get("total", 0))

    async def get_channel_views(self, session, token, user_id):
        headers = {
            "Client-ID": TWITCH_CLIENT_ID1,
            "Authorization": f"Bearer {token}"
        }
        async with session.get(f"https://api.twitch.tv/helix/users?id={user_id}", headers=headers) as resp:
            data = await resp.json()
            if not data.get("data"):
                print("Twitch API views response:", data)
            if data.get("data"):
                return int(data["data"][0].get("view_count", 0))
            return 0

    async def get_videos(self, session, token, user_id):
        headers = {
            "Client-ID": TWITCH_CLIENT_ID1,
            "Authorization": f"Bearer {token}"
        }
        url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive&first=100"
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            if not data.get("data"):
                print("Twitch API videos response:", data)
            return data.get("data", [])

    def parse_twitch_duration(self, duration_str):
        # Twitch duration: e.g. "2h13m5s", "45m", "1h", "30s"
        h = m = s = 0
        for value, unit in re.findall(r'(\d+)([hms])', duration_str):
            if unit == 'h':
                h = int(value)
            elif unit == 'm':
                m = int(value)
            elif unit == 's':
                s = int(value)
        return h + m / 60 + s / 3600

    @commands.command(name="twitchstats", aliases=["twinfo", "hammerlive"])
    @commands.cooldown(rate=1, per=3600, type=commands.BucketType.user)
    async def twitchstats(self, ctx):
        """Shows Twitch stats for the configured streamer."""
        await ctx.typing()
        token = await self.get_token()

        async with aiohttp.ClientSession() as session:
            user = await self.get_user(session, token)
            if not user:
                await ctx.send("❌ Could not find Twitch user.")
                return

            user_id = user["id"]
            display_name = user["display_name"]
            profile_image = user["profile_image_url"]

            followers_count = await self.get_followers(session, token, user_id)
            channel_views = await self.get_channel_views(session, token, user_id)
            videos = await self.get_videos(session, token, user_id)

            # Calculate hours streamed this year and last stream date
            current_year = datetime.utcnow().year
            hours_streamed = 0
            last_stream_date = None

            for v in videos:
                created_at = v.get("created_at")
                duration_str = v.get("duration")  # e.g. "2h13m5s"
                if created_at:
                    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                    if not last_stream_date or dt > last_stream_date:
                        last_stream_date = dt
                    if dt.year == current_year and duration_str:
                        hours_streamed += self.parse_twitch_duration(duration_str)

            # Format last stream date
            last_stream_str = (
                f"<t:{int(last_stream_date.replace(tzinfo=timezone.utc).timestamp())}:R>"
                if last_stream_date else "N/A"
            )

        embed = discord.Embed(
            title=f"{display_name} Twitch Stats",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=profile_image)
        embed.add_field(name="Followers", value=f"{followers_count:,}", inline=True)
        embed.add_field(name="Total Channel Views", value=f"{channel_views:,}", inline=True)
        embed.add_field(name="Hours Streamed (This Year)", value=f"{hours_streamed:.2f}", inline=True)
        embed.add_field(name="Last Stream", value=last_stream_str, inline=True)
        stream_link = f"https://twitch.tv/{display_name}" if display_name else None
        embed.add_field(
            name="🔗 Channel link here:",
            value=stream_link or "link error",
            inline=False
        )

        await ctx.send(embed=embed)

    @twitchstats.error
    async def cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ You can use this command again in {int(error.retry_after // 60)} minutes.")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(TwitchStats(bot))
