import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Constants
MOD_CHANNEL_ID = 1375784527581937684  # Replace with your moderator channel ID
startup_logs = []

def log(message: str):
    """Log a message with timestamp to both console and startup_logs."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    startup_logs.append(formatted_message)

print("Starting the bot...")
print("-------------------------------")

# Load environment variables
log("Loading environment variables...")
load_dotenv()
log("✅ Environment variables loaded")

# Get tokens
log("Checking for required environment variables...")
TOKEN = os.getenv("DISCORD_TOKEN1")

if not TOKEN:
    log("❌ No Discord token found in .env file")
    raise ValueError("No Discord token found in .env file")
log("✅ Discord token found")

# Initialize intents
log("Initializing Discord intents...")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
log("✅ Intents initialized")

# Create bot instance
log("Creating bot instance...")
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Send startup logs to moderator channel when bot is ready."""
    try:
        mod_channel = bot.get_channel(MOD_CHANNEL_ID)
        if mod_channel:
            log_message = "**Bot Startup Logs:**\n```\n"
            log_message += "\n".join(startup_logs)
            log_message += "\n```"
            
            # Split messages if too long
            while len(log_message) > 1900:
                split_point = log_message[:1900].rfind('\n')
                await mod_channel.send(log_message[:split_point] + "```")
                log_message = "```\n" + log_message[split_point:]
            
            await mod_channel.send(log_message)
            log("✅ Startup logs sent to moderator channel")
    except Exception as e:
        log(f"❌ Failed to send startup logs to moderator channel: {e}")

async def load_extensions():
    """Load all cog extensions."""
    extensions = [
        "cogs.moderationt"
    ]
    
    for extension in extensions:
        try:
            log(f"Loading extension: {extension}")
            await bot.load_extension(extension)
            log(f"✅ Loaded {extension}")
        except Exception as e:
            log(f"❌ Failed to load extension {extension}: {e}")

async def main():
    try:
        # Load extensions
        log("Beginning extension loading process...")
        await load_extensions()
        log("✅ All extensions loaded")

        # Start the bot
        log("Starting bot...")
        await bot.start(TOKEN)

    except Exception as e:
        log(f"❌ Error during startup: {e}")
        raise

if __name__ == "__main__":
    try:
        log("Initializing main process...")
        asyncio.run(main())
    except KeyboardInterrupt:
        log("⚠️ Bot shutdown initiated by user")
    except Exception as e:
        log(f"❌ Fatal error: {e}")