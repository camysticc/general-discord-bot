# cogs/lock.py
# Implements a /lock command to lock a channel.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

class LockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable role ID that can use this command
        self.allowed_role_id = 1409970906981339317
        logger.info("LockCog initialized successfully")

    @app_commands.command(name='lock', description='Locks a channel, preventing non-moderators from sending messages.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    @app_commands.describe(channel='The channel to lock.')
    async def lock_command(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            # Check if the user has the allowed role
            allowed_role = interaction.guild.get_role(self.allowed_role_id)
            if not allowed_role:
                await interaction.response.send_message("Error: Allowed role not found.", ephemeral=True)
                logger.error(f"Allowed role {self.allowed_role_id} not found in guild {interaction.guild.id}")
                return

            if allowed_role not in interaction.user.roles:
                await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
                return
            
            # Get the @everyone role
            everyone_role = interaction.guild.default_role
            
            # Set permissions to deny sending messages for everyone
            await channel.set_permissions(everyone_role, send_messages=False)
            
            await interaction.response.send_message(f"{channel.mention} has been locked. Only users with the specified role can send messages.", ephemeral=True)
            logger.info(f"Channel {channel.id} locked by {interaction.user.id}.")

        except Exception as e:
            logger.error(f"Error in lock command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while locking the channel.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(LockCog(bot))
        logger.info("LockCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add LockCog to bot: {e}", exc_info=True)
        raise
