# cogs/help.py
# Implements a /help slash command that displays an embed with buttons for "Rules" and "Freelancing Roles."
# Clicking a button sends a new embed with relevant information.
# The command is restricted to the guild with ID 1144662039504109721.
# The setup function is now asynchronous to properly await bot.add_cog().

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import logging

# Set up logging
logger = logging.getLogger(__name__)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("HelpCog initialized successfully")

    @app_commands.command(name='help', description='Get help with server rules or freelancing roles')
    @app_commands.guilds(discord.Object(id=1144662039504109721))  # Restrict to specific guild
    async def help_command(self, interaction: discord.Interaction):
        try:
            # Initial embed asking what the user needs help with
            embed = discord.Embed(
                title="Help Menu",
                description="Please select an option to get more information:",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Powered by DevDen")

            # Create buttons
            view = HelpView()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            logger.info(f"Help command initiated by user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in help command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Non-persistent by default; restarts will clear active views

    @discord.ui.button(label="Rules", style=discord.ButtonStyle.primary)
    async def rules_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        try:
            # Embed for Rules
            embed = discord.Embed(
                title="Server Rules",
                description=(
                    "Here are the server rules:\n"
                    "1. Be respectful to all members.\n"
                    "2. No spamming or advertising without permission.\n"
                    "3. Follow Discord's Community Guidelines.\n"
                    "4. Keep discussions relevant to the channel.\n"
                    "5. Contact moderators for any issues.\n"
                    "For more details, check the #rules channel."
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="Powered by DevDen")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Rules help requested by user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in rules button callback: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while displaying rules.", ephemeral=True)

    @discord.ui.button(label="Freelancing Roles", style=discord.ButtonStyle.primary)
    async def roles_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        try:
            # Embed for Freelancing Roles
            embed = discord.Embed(
                title="Freelancing Roles",
                description=(
                    "Our server offers various freelancing roles:\n"
                    "- **Verified Freelancer**: To verify you have completed commissions successfully! Use `/apply-dev` to apply!\n"
                    "- **Funds Verified**: Just to confirm you have funds to pay for the commission in robux only! We only ever verify robux, if anyone asks for your bank details for this verification please report them to us. Use `/apply-dev` to apply!\n"
                    "To apply, use the `/apply-dev` command and follow the instructions.\n"
                    "For more details, check the #roles channel."
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="Powered by DevDen")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Freelancing Roles help requested by user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in roles button callback: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while displaying freelancing roles.", ephemeral=True)

async def setup(bot):
    try:
        cog_instance = HelpCog(bot)
        await bot.add_cog(cog_instance)
        logger.info("HelpCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add HelpCog to bot: {e}", exc_info=True)
        raise
