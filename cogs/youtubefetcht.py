import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY1")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID1")

class YouTubeStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="youtubeinfo", aliases=["ytinfo", "hammeryt"])
    @commands.cooldown(1, 3600, commands.BucketType.user)  # 3600 seconds = 1 hour
    async def youtube_info(self, ctx):
        """Shows detailed information about the configured YouTube channel.
        This command can only be used once every 1 hour per user to comply with Google API quota limits.
        """
        base_url = "https://www.googleapis.com/youtube/v3"
        session = aiohttp.ClientSession()

        try:
            # 1. Get Channel Statistics and Snippet
            stats_url = f"{base_url}/channels?part=statistics,snippet&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
            async with session.get(stats_url) as resp:
                stats_data = await resp.json()
                if "items" not in stats_data or not stats_data["items"]:
                    await ctx.send("❌ Channel not found or misconfigured.")
                    return

                item = stats_data["items"][0]
                stats = item["statistics"]
                snippet = item["snippet"]
                channel_title = snippet["title"]
                channel_icon = snippet["thumbnails"]["default"]["url"]
                subs = int(stats["subscriberCount"])
                views = int(stats["viewCount"])

            # 2. Get Last Uploaded Video
            uploads_url = f"{base_url}/search?key={YOUTUBE_API_KEY}&channelId={CHANNEL_ID}&part=snippet&order=date&type=video&maxResults=10"
            async with session.get(uploads_url) as resp:
                uploads_data = await resp.json()
                last_video = None
                last_short = None
                for video in uploads_data.get("items", []):
                    vid_id = video["id"]["videoId"]
                    title = video["snippet"]["title"]
                    if not last_video:
                        last_video = (title, f"https://youtube.com/watch?v={vid_id}")
                    if not last_short and "/shorts/" in f"https://youtube.com/watch?v={vid_id}".replace("watch?v=", "shorts/"):
                        last_short = (title, f"https://youtube.com/shorts/{vid_id}")

            # 3. Get Last Livestream
            live_url = f"{base_url}/search?key={YOUTUBE_API_KEY}&channelId={CHANNEL_ID}&part=snippet&eventType=completed&type=video&maxResults=5"
            async with session.get(live_url) as resp:
                live_data = await resp.json()
                last_stream = None
                for video in live_data.get("items", []):
                    if "live" in video["snippet"].get("liveBroadcastContent", "").lower() or "live" in video["snippet"]["title"].lower():
                        vid_id = video["id"]["videoId"]
                        last_stream = (video["snippet"]["title"], f"https://youtube.com/watch?v={vid_id}")
                        break

            # 4. Construct Embed
            embed = discord.Embed(
                title=f"{channel_title} - Hammers YouTube Channel Info",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=channel_icon)
            embed.add_field(name="👥 Subscribers", value=f"{subs:,}", inline=True)
            embed.add_field(name="👁️ Total Views", value=f"{views:,}", inline=True)

            if last_video:
                embed.add_field(name="🎬 Last Video", value=f"[{last_video[0]}]({last_video[1]})", inline=False)
            if last_short:
                embed.add_field(name="📱 Last Short", value=f"[{last_short[0]}]({last_short[1]})", inline=False)
            if last_stream:
                embed.add_field(name="🔴 Last Livestream", value=f"[{last_stream[0]}]({last_stream[1]})", inline=False)

            await ctx.send(embed=embed)

        except commands.CommandOnCooldown as e:
            await ctx.send(f"❌ This command can only be used once every 1 hour per user to comply with Google API quota limits. Try again in {int(e.retry_after // 60)}m {int(e.retry_after) % 60}s.")
        except Exception as e:
            await ctx.send(f"❌ Something went wrong while fetching YouTube info. {e} ")
            print(f"[YouTubeInfoError] {e}")

        finally:
            await session.close()

    @youtube_info.error
    async def youtube_info_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"❌ This command can only be used once every 1 hour per user to comply with Google API monthly limits. Try again in {int(error.retry_after // 60)}m {int(error.retry_after) % 60}s.")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(YouTubeStats(bot))
