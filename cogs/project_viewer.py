# cogs/project_viewer.py
# Implements the /project-status command for viewing project details.

import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import os

# Set up logging
logger = logging.getLogger(__name__)

# File path for the project data
PROJECTS_FILE = 'projects.json'

def load_projects():
    """Loads projects from the JSON file."""
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("projects.json file is corrupted. Starting with an empty project dictionary.")
                return {}
    return {}

class ProjectViewerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("ProjectViewerCog initialized successfully")

    @app_commands.command(name='project-status', description='Shows the current status of a project.')
    @app_commands.describe(project_id='The unique ID of the project.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def project_status_command(self, interaction: discord.Interaction, project_id: str):
        try:
            projects = load_projects()
            project_id = project_id.upper()
            if project_id in projects:
                project = projects[project_id]
                
                embed = discord.Embed(
                    title=f"Project Status: `{project_id}`",
                    description=(
                        f"**Department:** {project['department']}\n"
                        f"**Creator:** <@{project['creator_id']}>\n"
                        f"**Current Status:** {project['status']}"
                    ),
                    color=discord.Color.gold()
                )
                embed.set_footer(text="Powered by DevDen")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                logger.info(f"Project status for {project_id} viewed by {interaction.user.id}.")
            else:
                await interaction.response.send_message("That project ID does not exist.", ephemeral=True)
                logger.warning(f"Attempted to view status for non-existent ID {project_id}.")
        except Exception as e:
            logger.error(f"Error in project-status command: {e}", exc_info=True)
            await interaction.response.send_message("An unexpected error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(ProjectViewerCog(bot))
        logger.info("ProjectViewerCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add ProjectViewerCog to bot: {e}", exc_info=True)
        raise
