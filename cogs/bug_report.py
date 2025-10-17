# cogs/bug_report.py
# Implements a /bug-report slash command with a dropdown menu and modal for submitting bug reports.

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput
import logging

# Set up logging
logger = logging.getLogger(__name__)

class BugReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable channel ID where bug reports are sent
        self.bug_report_channel_id = 1409967773538455785
        # Configurable role ID to ping for new bug reports
        self.ping_role_id = 1409967856824750203
        logger.info("BugReportCog initialized successfully")

    @app_commands.command(name='bug-report', description='Submit a bug report')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def bug_report_command(self, interaction: discord.Interaction):
        try:
            # Create a dropdown menu for topic selection
            select = Select(
                placeholder="Select a topic for your bug report",
                options=[
                    discord.SelectOption(label="Channels", description="A bug related to server channels."),
                    discord.SelectOption(label="Bots", description="A bug related to the bot or other bots."),
                    discord.SelectOption(label="General", description="A general bug not related to channels or bots.")
                ]
            )
            
            async def select_callback(inter: discord.Interaction):
                topic = select.values[0]
                modal = BugReportModal(self, topic)
                await inter.response.send_modal(modal)

            select.callback = select_callback

            view = View()
            view.add_item(select)
            
            await interaction.response.send_message("Please select a topic for your bug report:", view=view, ephemeral=True)
            logger.info(f"Bug report initiated by user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in bug report command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

class BugReportModal(Modal):
    def __init__(self, cog, topic):
        super().__init__(title=f"Bug Report: {topic}")
        self.cog = cog
        self.topic = topic
        
        # Add a required text input for the bug description
        self.add_item(TextInput(
            label="Bug Description",
            style=discord.TextStyle.paragraph,
            placeholder="Describe the bug in detail...",
            required=True,
            max_length=1000
        ))
        
        # Add an optional text input for an image link
        self.add_item(TextInput(
            label="Image Link (Optional)",
            style=discord.TextStyle.short,
            placeholder="Paste a link to an image/video of the bug...",
            required=False
        ))
        logger.info(f"BugReportModal created for topic: {topic}")
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            description = self.children[0].value
            image_link = self.children[1].value
            
            # Create the embed for the bug report
            embed = discord.Embed(
                title=f"Bug Report: {self.topic}",
                description=description,
                color=discord.Color.red()
            )
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
            embed.set_footer(text=f"Reported by {interaction.user.name} | User ID: {interaction.user.id}")
            
            if image_link:
                embed.set_image(url=image_link)
            
            # Send to the configured channel
            channel = self.cog.bot.get_channel(self.cog.bug_report_channel_id)
            if not channel:
                await interaction.response.send_message("Error: Bug report channel not found.", ephemeral=True)
                logger.error(f"Bug report channel {self.cog.bug_report_channel_id} not found")
                return

            # Get the role to ping and send the message
            role = interaction.guild.get_role(self.cog.ping_role_id)
            if role:
                await channel.send(f"{role.mention}", embed=embed)
            else:
                await channel.send(embed=embed)
                logger.warning(f"Ping role {self.cog.ping_role_id} not found in guild {interaction.guild.id}")

            await interaction.response.send_message("Thank you! Your bug report has been submitted.", ephemeral=True)
            logger.info(f"Bug report submitted by {interaction.user.id} for topic {self.topic}")
        except Exception as e:
            logger.error(f"Error submitting bug report: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while submitting your bug report.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(BugReportCog(bot))
        logger.info("BugReportCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add BugReportCog to bot: {e}", exc_info=True)
        raise
