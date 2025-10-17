# cogs/flag.py
# Implements a /flag command to create a private investigation channel for a user.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

class FlagCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable role ID that can use this command
        self.allowed_role_id = 1409970906981339317
        # Configurable category ID where new channels will be created
        self.category_id = 1409971086392557618
        logger.info("FlagCog initialized successfully")

    @app_commands.command(name='flag', description='Create a private investigation channel for a user.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    @app_commands.describe(user='The user to create an investigation channel for.')
    async def flag_command(self, interaction: discord.Interaction, user: discord.Member):
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

            # Check if the category exists
            category = interaction.guild.get_channel(self.category_id)
            if not category:
                await interaction.response.send_message("Error: Investigation category not found.", ephemeral=True)
                logger.error(f"Investigation category {self.category_id} not found in guild {interaction.guild.id}")
                return

            # Sanitize username for channel name
            channel_name = f"{user.name.lower().replace(' ', '-')}-investigation"
            
            # Create the new channel
            new_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                topic=f"Investigation channel for {user.display_name} ({user.id})",
                overwrites={
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.guild.get_role(self.allowed_role_id): discord.PermissionOverwrite(read_messages=True),
                    user: discord.PermissionOverwrite(read_messages=False)
                }
            )

            await interaction.response.send_message(f"Investigation channel created for {user.mention} in {new_channel.mention}", ephemeral=True)
            logger.info(f"Investigation channel for {user.id} created by {interaction.user.id}.")

        except Exception as e:
            logger.error(f"Error in flag command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while creating the channel.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(FlagCog(bot))
        logger.info("FlagCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add FlagCog to bot: {e}", exc_info=True)
        raise
