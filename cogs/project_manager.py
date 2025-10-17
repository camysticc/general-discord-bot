# cogs/project_manager.py
# Implements the /manage-status command for updating project status.
# This cog restricts access to only the project's creator.

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

def save_projects(projects_data):
    """Saves projects to the JSON file."""
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(projects_data, f, indent=4)

class ProjectManageStatusView(discord.ui.View):
    """
    A view with a dropdown menu to update the project status.
    """
    def __init__(self, cog, project_id):
        super().__init__(timeout=180) # Timeout after 3 minutes
        self.cog = cog
        self.project_id = project_id

    @discord.ui.select(
        placeholder="Select a new project status...",
        options=[
            discord.SelectOption(label="In Progress", value="In Progress", description="Project is being worked on."),
            discord.SelectOption(label="Awaiting Feedback", value="Awaiting Feedback", description="Project is awaiting client feedback."),
            discord.SelectOption(label="Completed", value="Completed", description="Project is finished and delivered."),
            discord.SelectOption(label="Canceled", value="Canceled", description="Project has been canceled.")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        """
        Callback for the dropdown menu to update the status.
        """
        new_status = select.values[0]
        
        projects = load_projects()
        # Check if the project ID still exists
        if self.project_id in projects:
            project_data = projects[self.project_id]
            project_data["status"] = new_status
            save_projects(projects)
            
            embed = discord.Embed(
                title="Status Updated!",
                description=f"Project `{self.project_id}` status has been updated to **{new_status}**.",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Powered by DevDen")
            
            # Send DM to recipient if the status is "Completed"
            if new_status == "Completed":
                recipient_id = int(project_data.get("recipient_id"))
                creator_id = int(project_data.get("creator_id"))
                
                recipient = self.cog.bot.get_user(recipient_id)
                creator = self.cog.bot.get_user(creator_id)
                
                if recipient and creator:
                    dm_embed = discord.Embed(
                        title="Commission Finished! 🥳",
                        description=(
                            f"Your commission has been completed! {creator.mention} was your developer!\n\n"
                            f"**Project ID:** `{self.project_id}`\n"
                            f"**Department:** {project_data['department']}\n\n"
                            "Contact your developer for more information!"
                        ),
                        color=7685565 # Hexadecimal value for the light blue color
                    )
                    dm_embed.set_footer(text="Powered by DevDen")
                    
                    try:
                        await recipient.send(embed=dm_embed)
                        logger.info(f"Completed DM sent to recipient {recipient.id} for project {self.project_id}.")
                    except discord.Forbidden:
                        logger.warning(f"Could not send 'Completed' DM to {recipient.id}. They may have DMs disabled.")
                else:
                    logger.error(f"Could not find recipient or creator user object for project {self.project_id}.")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Project {self.project_id} status updated to {new_status} by {interaction.user.id}.")
        else:
            await interaction.response.send_message("This project no longer exists.", ephemeral=True)
            logger.warning(f"Attempt to update non-existent project {self.project_id} by {interaction.user.id}.")
        
        self.stop() # Stop the view after a selection is made

class ProjectManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("ProjectManagerCog initialized successfully")
        
    @app_commands.command(name='manage-status', description='Manages the status of a project (creator only).')
    @app_commands.describe(project_id='The unique ID of the project to manage.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def manage_status_command(self, interaction: discord.Interaction, project_id: str):
        try:
            projects = load_projects()
            project_id = project_id.upper()
            if project_id not in projects:
                await interaction.response.send_message("That project ID does not exist.", ephemeral=True)
                return

            project = projects[project_id]
            
            # Check if the user is the project creator
            if str(interaction.user.id) == project["creator_id"]:
                view = ProjectManageStatusView(self, project_id)
                await interaction.response.send_message("What would you like to update the status to?", view=view, ephemeral=True)
                logger.info(f"Manage status initiated for project {project_id} by creator {interaction.user.id}.")
            else:
                await interaction.response.send_message("You do not have permission to manage this project's status.", ephemeral=True)
                logger.warning(f"Unauthorized attempt to manage project {project_id} by {interaction.user.id}.")
        except Exception as e:
            logger.error(f"Error in manage-status command: {e}", exc_info=True)
            await interaction.response.send_message("An unexpected error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(ProjectManagerCog(bot))
        logger.info("ProjectManagerCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add ProjectManagerCog to bot: {e}", exc_info=True)
        raise
