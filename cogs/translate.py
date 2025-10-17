# cogs/translate.py
# Implements a /translate command to translate a block of text to a different language.

import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
import logging

# Set up logging
logger = logging.getLogger(__name__)

class TranslateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("TranslateCog initialized successfully")

    @app_commands.command(name='translate', description='Translate a block of text to a different language.')
    @app_commands.describe(language='The language to translate to (e.g., en, es, fr).')
    @app_commands.describe(text='The text to translate.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def translate_command(self, interaction: discord.Interaction, language: str, text: str):
        try:
            # Use deep-translator with Google Translate backend
            translator = GoogleTranslator(source='auto', target=language)
            translation = translator.translate(text)
            
            embed = discord.Embed(
                title="Translation",
                description=f"**Original Text:**\n{text}\n\n**Translated Text ({language}):**\n{translation}",
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Translation requested by {interaction.user.id} for language {language}")
        except Exception as e:
            logger.error(f"Error in translate command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred during translation. Please check the language code.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(TranslateCog(bot))
        logger.info("TranslateCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add TranslateCog to bot: {e}", exc_info=True)
        raise
