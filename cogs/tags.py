# cogs/tags.py
# This cog implements a versatile slash command group for managing and sending tags.
# It uses a JSON file for persistent storage and restricts administrative
# subcommands to a specific role.

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import logging

# Set up logging for this cog
logger = logging.getLogger(__name__)

# File path for tag data
TAGS_FILE = 'tags.json'

def load_tags():
    """
    Loads tags from the JSON file.
    Returns an empty dictionary if the file doesn't exist or is corrupted.
    """
    if os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("tags.json file is corrupted. Starting with an empty dictionary.")
                return {}
    return {}

def save_tags(tags_data):
    """Saves the current tag data to the JSON file."""
    with open(TAGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tags_data, f, indent=4)
    logger.info("Tags data saved to tags.json.")


class TagsCog(commands.Cog):
    """
    A cog for managing and displaying custom tags.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tags = load_tags()
        self.TAG_ADMIN_ROLE_ID = 1409970906981339317  # Your specified role ID

    # This is the main command group for `/tag`
    # All subcommands will be part of this group.
    tag_group = app_commands.Group(
        name="tag",
        description="Manage and send custom tags."
    )

    # Autocomplete function for the tag names
    # This provides suggestions as the user types, making it easier to use.
    async def tag_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocompletes tag names for the user."""
        choices = []
        for tag_name in self.tags.keys():
            if current.lower() in tag_name.lower():
                choices.append(app_commands.Choice(name=tag_name, value=tag_name))
        return choices[:25] # Limit to 25 choices for Discord's API limits

    @tag_group.command(name="send", description="Sends a pre-defined tag.")
    @app_commands.describe(name="The name of the tag you want to send.")
    @app_commands.autocomplete(name=tag_autocomplete)
    async def send_tag(self, interaction: discord.Interaction, name: str):
        """
        Handles the /tag send command.
        Sends the content of a tag if it exists.
        """
        if name in self.tags:
            content = self.tags[name]
            await interaction.response.send_message(content)
            logger.info(f"Tag '{name}' sent by {interaction.user.name} ({interaction.user.id}).")
        else:
            await interaction.response.send_message(
                f"Sorry, a tag named `{name}` does not exist.",
                ephemeral=True
            )
            logger.warning(f"Attempted to send non-existent tag '{name}' by {interaction.user.id}.")

    @tag_group.command(name="create", description="Creates a new tag.")
    @app_commands.describe(
        name="The name for the new tag.",
        content="The content for the new tag."
    )
    # Restrict this command to the specified role ID
    @app_commands.has_any_role(1409970906981339317)
    async def create_tag(self, interaction: discord.Interaction, name: str, content: str):
        """
        Handles the /tag create command.
        Creates a new tag with the given name and content.
        """
        await interaction.response.defer(ephemeral=True, thinking=True) # Defer the response for a better user experience
        name = name.lower() # Normalize tag name to lowercase

        if name in self.tags:
            await interaction.followup.send(
                f"A tag named `{name}` already exists. Please choose a different name.",
                ephemeral=True
            )
            logger.warning(f"Failed to create tag '{name}'. It already exists.")
            return

        self.tags[name] = content
        save_tags(self.tags)
        
        await interaction.followup.send(
            f"Tag `{name}` has been successfully created!",
            ephemeral=True
        )
        logger.info(f"Tag '{name}' created by {interaction.user.name} ({interaction.user.id}).")

    @tag_group.command(name="delete", description="Deletes an existing tag.")
    @app_commands.describe(name="The name of the tag to delete.")
    # Restrict this command to the specified role ID
    @app_commands.has_any_role(1409970906981339317)
    async def delete_tag(self, interaction: discord.Interaction, name: str):
        """
        Handles the /tag delete command.
        Deletes a tag with the given name.
        """
        await interaction.response.defer(ephemeral=True, thinking=True) # Defer the response
        name = name.lower() # Normalize tag name to lowercase

        if name not in self.tags:
            await interaction.followup.send(
                f"Sorry, a tag named `{name}` does not exist.",
                ephemeral=True
            )
            logger.warning(f"Failed to delete tag '{name}'. It does not exist.")
            return

        del self.tags[name]
        save_tags(self.tags)
        
        await interaction.followup.send(
            f"Tag `{name}` has been successfully deleted!",
            ephemeral=True
        )
        logger.info(f"Tag '{name}' deleted by {interaction.user.name} ({interaction.user.id}).")
        
    # Handles a generic error for the command group
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handles errors for this cog's commands."""
        if isinstance(error, app_commands.MissingAnyRole):
            await interaction.response.send_message(
                "You do not have the required permissions to use this command.",
                ephemeral=True
            )
        else:
            logger.error(f"An error occurred in a tag command: {error}", exc_info=True)
            await interaction.response.send_message(
                "An unexpected error occurred while processing your command.",
                ephemeral=True
            )

async def setup(bot):
    """Adds the TagsCog to the bot."""
    await bot.add_cog(TagsCog(bot))
    logger.info("TagsCog loaded successfully.")
