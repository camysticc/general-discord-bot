# cogs/feedback.py
# Implements a /feedback slash command with a modal for submitting feedback with a star rating.

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
import logging

# Set up logging
logger = logging.getLogger(__name__)

class FeedbackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable channel ID where feedback is sent
        self.feedback_channel_id = 1409969635725410415
        # Configurable role ID to ping for new feedback
        self.ping_role_id = 1409967856824750203
        logger.info("FeedbackCog initialized successfully")

    @app_commands.command(name='feedback', description='Submit feedback for a developer')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def feedback_command(self, interaction: discord.Interaction):
        try:
            modal = FeedbackModal(self)
            await interaction.response.send_modal(modal)
            logger.info(f"Feedback command initiated by user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in feedback command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

class FeedbackModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Developer Feedback")
        self.cog = cog
        
        # Input for developer's name
        self.add_item(TextInput(
            label="Name of dev?",
            style=discord.TextStyle.short,
            placeholder="e.g., JohnDoe#1234",
            required=True
        ))

        # Input for the star rating
        self.rating_input = TextInput(
            label="Star Rating (1-5)",
            style=discord.TextStyle.short,
            placeholder="e.g., 5",
            required=True
        )
        self.add_item(self.rating_input)
        
        # Input for the feedback message
        self.add_item(TextInput(
            label="Why did you give this rating?",
            style=discord.TextStyle.paragraph,
            placeholder="Tell us about your experience...",
            required=True,
            max_length=1000
        ))
        logger.info("FeedbackModal created")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            dev_name = self.children[0].value
            rating_str = self.children[1].value
            feedback_message = self.children[2].value

            # Validate the rating
            try:
                rating = int(rating_str)
                if not 1 <= rating <= 5:
                    await interaction.response.send_message("Please enter a star rating between 1 and 5.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("Please enter a valid number for the star rating.", ephemeral=True)
                return

            # Generate the star string
            star_rating = "⭐" * rating

            # Create the embed for the feedback report
            embed = discord.Embed(
                title=f"Feedback for {dev_name}",
                description=f"**Rating:** {star_rating}\n\n**Feedback:**\n{feedback_message}",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            embed.set_footer(text=f"Submitted by {interaction.user.name} | User ID: {interaction.user.id}")
            
            # Send to the configured channel
            channel = self.cog.bot.get_channel(self.cog.feedback_channel_id)
            if not channel:
                await interaction.response.send_message("Error: Feedback channel not found.", ephemeral=True)
                logger.error(f"Feedback channel {self.cog.feedback_channel_id} not found")
                return

            await channel.send(embed=embed)
            logger.info(f"Feedback submitted by {interaction.user.id} for {dev_name} with a {rating}-star rating.")

            await interaction.response.send_message("Thank you for your feedback! It has been submitted.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while submitting your feedback.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(FeedbackCog(bot))
        logger.info("FeedbackCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add FeedbackCog to bot: {e}", exc_info=True)
        raise
