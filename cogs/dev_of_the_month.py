# cogs/dev_of_the_month.py
# Implements the /dev-of-the-month command for recognizing an outstanding member.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Placeholder for announcements channel ID
# REPLACE WITH YOUR ACTUAL ANNOUNCEMENTS CHANNEL ID
ANNOUNCEMENTS_CHANNEL_ID = 123456789012345678  # Example ID

class DevOfTheMonthCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("DevOfTheMonthCog initialized successfully")

    @app_commands.command(name='dev-of-the-month', description='Recognizes an outstanding member (admin only).')
    @app_commands.describe(member='The member to recognize.')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def dev_of_the_month(self, interaction: discord.Interaction, member: discord.Member):
        """Recognizes an outstanding member of the month."""
        try:
            channel = self.bot.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
            if not channel:
                await interaction.response.send_message("Announcements channel not found. Please configure the channel ID.", ephemeral=True)
                return

            embed = discord.Embed(
                title="🌟 Developer of the Month! 🌟",
                description=f"A huge round of applause for our Developer of the Month, {member.mention}!",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name="Congratulations!", value="Thank you for your hard work and dedication to the community. Keep up the great work!", inline=False)
            embed.set_footer(text="Powered by DevDen")

            await channel.send(embed=embed)
            await interaction.response.send_message(f"Announcement sent for {member.mention}.", ephemeral=True)
            logger.info(f"Dev of the Month announcement made by {interaction.user.id} for {member.id}.")
        except Exception as e:
            logger.error(f"Error in dev-of-the-month command: {e}", exc_info=True)
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(DevOfTheMonthCog(bot))
        logger.info("DevOfTheMonthCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add DevOfTheMonthCog to bot: {e}", exc_info=True)
        raise
