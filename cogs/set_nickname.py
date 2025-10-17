# cogs/set_nickname.py
# Implements a /set-nickname command to change a user's nickname, restricted to a specific role.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

class SetNicknameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable role ID that can use this command
        self.allowed_role_id = 1409970906981339317
        logger.info("SetNicknameCog initialized successfully")

    @app_commands.command(name='set-nickname', description='Changes a users nickname.')
    @app_commands.describe(user='The user whose nickname you want to change.')
    @app_commands.describe(nickname='The new nickname for the user.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def set_nickname_command(self, interaction: discord.Interaction, user: discord.Member, nickname: str):
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
            
            # Change the nickname
            await user.edit(nick=nickname)
            
            await interaction.response.send_message(f"Changed {user.mention}'s nickname to `{nickname}`.", ephemeral=True)
            logger.info(f"Nickname for {user.id} changed by {interaction.user.id}.")

        except Exception as e:
            logger.error(f"Error in set-nickname command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while changing the nickname. Check the bot's permissions.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(SetNicknameCog(bot))
        logger.info("SetNicknameCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add SetNicknameCog to bot: {e}", exc_info=True)
        raise
