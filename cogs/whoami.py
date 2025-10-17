# cogs/whoami.py
# Implements a /whoami command to display user information.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

class WhoamiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("WhoamiCog initialized successfully")

    @app_commands.command(name='whoami', description='Tells you your Discord ID, account creation date, and join date.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def whoami_command(self, interaction: discord.Interaction):
        try:
            user = interaction.user
            
            embed = discord.Embed(
                title="User Information",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="User", value=user.mention, inline=False)
            embed.add_field(name="User ID", value=user.id, inline=False)
            embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Whoami command used by {user.id}")
        except Exception as e:
            logger.error(f"Error in whoami command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while fetching your information.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(WhoamiCog(bot))
        logger.info("WhoamiCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add WhoamiCog to bot: {e}", exc_info=True)
        raise
