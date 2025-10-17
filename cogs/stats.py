# cogs/stats.py
# Implements a /stats command to display bot statistics.

import discord
from discord import app_commands
from discord.ext import commands
import logging
import os
import psutil

# Set up logging
logger = logging.getLogger(__name__)

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("StatsCog initialized successfully")

    @app_commands.command(name='stats', description='Displays bot statistics.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def stats_command(self, interaction: discord.Interaction):
        try:
            # Get bot statistics
            guilds = len(self.bot.guilds)
            users = len(self.bot.users)
            
            # Get memory usage
            process = psutil.Process(os.getpid())
            memory_usage_mb = process.memory_info().rss / 1024**2  # in MB

            embed = discord.Embed(
                title="Bot Statistics",
                color=discord.Color.gold()
            )
            embed.add_field(name="Servers", value=guilds, inline=True)
            embed.add_field(name="Users", value=users, inline=True)
            embed.add_field(name="Memory Usage", value=f"{memory_usage_mb:.2f} MB", inline=True)
            embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Stats command used by {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in stats command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while fetching bot statistics.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(StatsCog(bot))
        logger.info("StatsCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add StatsCog to bot: {e}", exc_info=True)
        raise
