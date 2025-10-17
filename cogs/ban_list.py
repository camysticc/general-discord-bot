# cogs/ban_list.py
# Implements a /ban-list command to display a list of banned users, restricted to a specific role.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

class BanListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable role ID that can use this command
        self.allowed_role_id = 1409970906981339317
        logger.info("BanListCog initialized successfully")

    @app_commands.command(name='ban-list', description='Displays a list of all banned users.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def ban_list_command(self, interaction: discord.Interaction):
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

            # Fetch the ban list
            bans = [entry async for entry in interaction.guild.bans()]
            
            if not bans:
                await interaction.response.send_message("There are no banned users on this server.", ephemeral=True)
                return
            
            ban_list = "\n".join([f"**{ban.user.name}** (`{ban.user.id}`)\nReason: {ban.reason or 'No reason provided'}" for ban in bans])
            
            embed = discord.Embed(
                title="Banned Users",
                description=ban_list,
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Total banned users: {len(bans)}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Ban list requested by {interaction.user.id}.")

        except Exception as e:
            logger.error(f"Error in ban-list command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while fetching the ban list. Check the bot's permissions.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(BanListCog(bot))
        logger.info("BanListCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add BanListCog to bot: {e}", exc_info=True)
        raise
