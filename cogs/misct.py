import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import random
import os

# Replace with your role ID for !ping+ command
PING_PLUS_ROLE_ID = 1349639595322773504

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Replies with Pong! and latency."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! 🏓 Latency: `{latency}ms`")

    @commands.command(name="ping+")
    @commands.has_role(PING_PLUS_ROLE_ID)
    async def pingplus(self, ctx):
        """High-precision latency test (locked to a specific role)."""
        wait_msg = await ctx.send("Running high-precision latency test, please wait 10 seconds...")
        latencies = []
        for _ in range(10):
            before = datetime.utcnow()
            await asyncio.sleep(1)
            after = datetime.utcnow()
            latency = (after - before).total_seconds() * 1000
            latencies.append(latency)
        avg_latency = sum(latencies) / len(latencies)
        await wait_msg.edit(content=f"High-precision Pong! 🏓 Average latency over 10 tests: `{avg_latency:.2f}ms`")

    @commands.command()
    async def pfp(self, ctx, user: discord.Member = None):
        """Displays the profile picture of the mentioned user or yourself."""
        user = user or ctx.author
        embed = discord.Embed(title=f"{user.display_name}'s Profile Picture")
        embed.set_image(url=user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        """Displays info about a user."""
        user = user or ctx.author
        roles = [role.mention for role in user.roles if role != ctx.guild.default_role]
        embed = discord.Embed(
            title=f"User Info - {user}",
            color=user.color if hasattr(user, "color") else discord.Color.default()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
        embed.add_field(name="Bot?", value="Yes" if user.bot else "No", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        """Provides server stats."""
        guild = ctx.guild
        embed = discord.Embed(
            title=f"Server Info - {guild.name}",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def hammer(self, ctx):
        """Sends a picture of a snail"""
        embed = discord.Embed(
            title="snail",
            description="snail",
            color=discord.Color.green()
        )
        embed.set_image(url="https://cdn.hswstatic.com/gif/gettyimages-568151731.jpg")
        await ctx.send(embed=embed)
        

    @commands.command()
    async def roleinfo(self, ctx, role: discord.Role):
        """Returns information about the specified role."""
        embed = discord.Embed(
            title=f"Role Info - {role.name}",
            color=role.color
        )
        embed.add_field(name="Role ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Created", value=role.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        perms = [name.replace('_', ' ').title() for name, value in role.permissions if value]
        embed.add_field(name="Permissions", value=", ".join(perms) if perms else "None", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx, *, args: str):
        """
        Start a timed giveaway.
        Usage: !giveaway [item] [duration]
        Example: !giveaway Nitro 1h30m
        """
        # Parse arguments
        try:
            *item_parts, duration_str = args.rsplit(" ", 1)
            item = " ".join(item_parts)
            duration = self.parse_duration(duration_str)
        except Exception:
            await ctx.send("❌ Usage: `!giveaway [item] [duration]` (e.g. `!giveaway Nitro 1h30m`)")
            return

        if duration.total_seconds() < 10:
            await ctx.send("❌ Duration must be at least 10 seconds.")
            return

        end_time = datetime.utcnow() + duration
        embed = discord.Embed(
            title="🎉 Giveaway! 🎉",
            description=f"**Prize:** {item}\nReact with 🎉 to enter!\n\nEnds <t:{int(end_time.timestamp())}:R>",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Started by {ctx.author.display_name}")

        giveaway_msg = await ctx.send(embed=embed)
        await giveaway_msg.add_reaction("🎉")

        await ctx.send(f"Giveaway started for **{item}**! Ends <t:{int(end_time.timestamp())}:R>.")

        await asyncio.sleep(duration.total_seconds())

        # Fetch message again to get all updated reactions
        giveaway_msg = await ctx.channel.fetch_message(giveaway_msg.id)

        # Find the 🎉 reaction specifically
        reaction = discord.utils.get(giveaway_msg.reactions, emoji="🎉")
        if reaction is None:
            await ctx.send("❌ No one reacted with 🎉.")
            return

        users = await reaction.users().flatten()
        users = [u for u in users if not u.bot]

        if not users:
            await ctx.send("❌ No valid entries, giveaway cancelled.")
            return

        winner = random.choice(users)
        await ctx.send(f"🎉 Congratulations {winner.mention}! You won **{item}**!")

    def parse_duration(self, time_str: str) -> timedelta:
        # Custom duration parser
        import re
        pattern = r"((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?"
        match = re.fullmatch(pattern, time_str.strip())
        if not match:
            raise ValueError("Invalid duration format.")

        time_data = {key: int(val) if val else 0 for key, val in match.groupdict().items()}
        return timedelta(**time_data)

    def parse_duration(self, duration_str):
        # Supports formats like 1h30m, 45m, 120s, 2h, etc.
        total_seconds = 0
        num = ''
        for char in duration_str:
            if char.isdigit():
                num += char
            elif char in 'hms' and num:
                if char == 'h':
                    total_seconds += int(num) * 3600
                elif char == 'm':
                    total_seconds += int(num) * 60
                elif char == 's':
                    total_seconds += int(num)
                num = ''
        if total_seconds == 0:
            raise ValueError("Invalid duration")
        return timedelta(seconds=total_seconds)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def streamstart(self, ctx, minutes: int):
        """
        Announces that the stream will start in X minutes.
        Usage: !streamstart [minutes]
        """
        if minutes < 1:
            await ctx.send("❌ Please specify a valid number of minutes.")
            return

        start_time = datetime.utcnow() + timedelta(minutes=minutes)
        unix_ts = int(start_time.timestamp())
        twitch_url = f"https://twitch.tv/{os.getenv('TWITCH_USERNAME1') or 'yourchannel'}"

        await ctx.send("@here")

        embed = discord.Embed(
            title="🔴 Stream Starting Soon!",
            description=(
                f"The stream will start in **{minutes} minutes**!\n"
                f"**Start Time:** <t:{unix_ts}:F>\n\n"
                f"[Watch here]({twitch_url})"
                f"\n![Bot Avatar]({self.bot.user.display_avatar.url})"
            ),
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Announced by {ctx.author.display_name}")

        await ctx.send(embed=embed)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass  # Bot can't delete the message

    @commands.command()
    async def unbump(self, ctx):
        """
        Does nothing except send an 'unbump' embed.
        """
        embed = discord.Embed(
            title="**UNBOARD: The Private Server Sinkhole**",
            description=(
                "Unbump complete. :thumbsdown:\n"
                "This server is now significantly harder to find.\n\n"
                "Proudly powered by outdated code, duct tape, and sheer stubbornness.\n"
                "No costs were covered. No help was received. No one asked for this. (actually fish did but whatever)"
            ),
            color=discord.Color.dark_gray()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1347242655515414590/1400150836574949376/invert.png?ex=688b9794&is=688a4614&hm=af2f1a12c97d2136c1dbeed9e5c6606ce45f1c56253835bf490d808bc44094a4&=&format=webp&quality=lossless&width=384&height=384")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Misc(bot))