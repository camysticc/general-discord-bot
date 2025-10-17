# cogs/color.py
# Implements a /color command to display a color from a hex code.

import discord
from discord import app_commands
from discord.ext import commands
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

class ColorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("ColorCog initialized successfully")

    @app_commands.command(name='color', description='Displays a color from a hex code.')
    @app_commands.describe(hex_code='The hex code for the color (e.g., #FF5733 or FF5733).')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def color_command(self, interaction: discord.Interaction, hex_code: str):
        try:
            # Sanitize and validate the hex code
            hex_code = hex_code.strip('#')
            if not re.match(r'^[0-9a-fA-F]{6}$', hex_code):
                await interaction.response.send_message("Invalid hex code. Please provide a 6-digit hex code.", ephemeral=True)
                return
            
            # Convert hex to integer for the embed color
            color_int = int(hex_code, 16)
            
            # Create the embed
            embed = discord.Embed(
                title=f"Color Preview: #{hex_code.upper()}",
                color=color_int
            )
            
            # Create a URL for a preview image
            color_preview_url = f"https://placehold.co/200x200/{hex_code.lower()}/FFFFFF.png?text=%23{hex_code.upper()}"
            embed.set_thumbnail(url=color_preview_url)
            embed.set_footer(text="Powered by DevDen")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Color command used by {interaction.user.id} for hex code {hex_code}.")

        except Exception as e:
            logger.error(f"Error in color command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while displaying the color.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(ColorCog(bot))
        logger.info("ColorCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add ColorCog to bot: {e}", exc_info=True)
        raise
