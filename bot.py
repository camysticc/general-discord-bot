import discord
from discord import app_commands
from discord.ext import commands
import logging
import os
import asyncio
import sys

# Set up logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Enable all intents
intents = discord.Intents.all()

# Initialize bot with intents and application ID
class MyBot(commands.Bot):
    async def setup_hook(self):
        logger.info("Bot is starting up, loading cogs...")
        cogs_dir = './cogs'
        if not os.path.isdir(cogs_dir):
            logger.warning(f"Cog directory '{cogs_dir}' does not exist. No cogs loaded.")
        else:
            for filename in os.listdir(cogs_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    cog = f'cogs.{filename[:-3]}'
                    try:
                        await self.load_extension(cog)
                        logger.info(f"Loaded extension: {cog}")
                    except Exception as e:
                        logger.error(f"Failed to load extension {cog}: {e}", exc_info=True)

bot = MyBot(command_prefix='!', intents=intents, application_id=1409939541229436998)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}#{bot.user.discriminator} (ID: {bot.user.id})')
    logger.info("Bot is ready, starting command sync...")
    try:
        # Sync all commands specifically to the guild.
        # This will instantly update all commands (from all cogs)
        # without waiting for the global command cache to refresh.
        guild_id = 1144662039504109721
        synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
        logger.info(f"Successfully synced {len(synced)} slash commands to guild {guild_id}.")
        if len(synced) == 0:
            logger.warning("No slash commands were synced. Check if cogs are loaded and commands are registered correctly.")
        for command in bot.tree.get_commands(guild=discord.Object(id=guild_id)):
            logger.info(f"Registered command: {command.name}")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}", exc_info=True)
    logger.info('------')

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        # We handle cooldowns directly within the cog's error handler for a custom message.
        # If no cog-specific handler is found, this one would catch it.
        await interaction.response.send_message(f"This command is on cooldown! Try again in {int(error.retry_after)} seconds.", ephemeral=True)
        logger.warning(f"Command cooldown triggered by {interaction.user} for command /{interaction.command.name}")
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have the required permissions to use this command.", ephemeral=True)
        logger.warning(f"Missing permissions error for {interaction.user} on command /{interaction.command.name}")
    elif isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("You don't have the required role to use this command.", ephemeral=True)
        logger.warning(f"Missing role error for {interaction.user} on command /{interaction.command.name}")
    elif isinstance(error, app_commands.CommandNotFound):
        # This error is not handled by the global handler because Discord handles it before reaching here.
        pass
    else:
        await interaction.response.send_message(f"An unexpected error occurred: {error}", ephemeral=True)
        logger.error(f"Unhandled error in command /{interaction.command.name}: {error}", exc_info=True)

# Run the bot with the token from the environment variable
def run_bot():
    token = os.getenv('DISCORD_TOKEN')
    if token is None:
        error_message = """
        ========================================================================================
        ERROR: Discord bot token not found!

        The bot token is not set as an environment variable. Please set it before running the bot.
        
        To set the token, use one of the commands below in your terminal, replacing the placeholder with your actual token:

        On macOS/Linux:
        export DISCORD_TOKEN="YOUR_BOT_TOKEN_HERE"
        
        On Windows (Command Prompt):
        set DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE

        On Windows (PowerShell):
        $env:DISCORD_TOKEN="YOUR_BOT_TOKEN_HERE"

        After setting the environment variable, run the bot from the same terminal session.
        ========================================================================================
        """
        print(error_message, file=sys.stderr)
        sys.exit(1)
    else:
        bot.run(token)

if __name__ == "__main__":
    run_bot()
