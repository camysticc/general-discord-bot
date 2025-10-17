# cogs/project_creator.py
# Implements the /set-project-id command for creating new projects.
# This cog handles the dropdown menu and saving new project data.

import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import os
import random
import string

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

def generate_unique_id():
    """Generates a unique 6-character alphanumeric ID."""
    characters = string.ascii_uppercase + string.digits
    while True:
        project_id = ''.join(random.choice(characters) for _ in range(6))
        projects = load_projects()
        # Check if the ID is already in use
        if project_id not in projects:
            return project_id

class ProjectSelectView(discord.ui.View):
    """
    A view with a dropdown menu to select a project department.
    """
    def __init__(self, cog, creator: discord.Member, recipient: discord.Member):
        super().__init__(timeout=180) # Timeout after 3 minutes
        self.cog = cog
        self.creator = creator
        self.recipient = recipient

    @discord.ui.select(
        placeholder="Select a project department...",
        options=[
            discord.SelectOption(label="Building", value="Building", description="Roblox building and design."),
            discord.SelectOption(label="Scripting", value="Scripting", description="Roblox Lua scripting."),
            discord.SelectOption(label="UI Design", value="UI Design", description="User interface design."),
            discord.SelectOption(label="Modelling", value="Modelling", description="3D modelling and asset creation."),
            discord.SelectOption(label="Animating", value="Animating", description="Character and asset animation."),
            discord.SelectOption(label="Terrain", value="Terrain", description="World and landscape creation."),
            discord.SelectOption(label="Graphics/Video Effects", value="Graphics/Video Effects", description="Visual effects and GFX."),
            discord.SelectOption(label="Sound VFX", value="Sound VFX", description="Sound effects and audio design.")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        """
        Callback for the dropdown menu.
        Generates a unique ID and saves the project.
        """
        department = select.values[0]
        project_id = generate_unique_id()
        
        projects = load_projects()
        # Save the new project to the dictionary and file
        projects[project_id] = {
            "department": department,
            "creator_id": str(self.creator.id),
            "recipient_id": str(self.recipient.id),
            "creator_name": self.creator.name,
            "recipient_name": self.recipient.name,
            "status": "Created"  # Initial status for a new project
        }
        save_projects(projects)
        
        # Create and send the DM embed to the recipient
        dm_embed = discord.Embed(
            title="Commission Started! 🥳",
            description=(
                f"Your commission has begun! {self.creator.mention} is your developer!\n\n"
                f"**Project ID:** `{project_id}`\n"
                f"**Department:** {department}\n"
                "You can check the status of this project anytime by using the `/project-status` command."
            ),
            color=7685565 # Hexadecimal value for the light blue color
        )
        dm_embed.set_footer(text="Powered by DevDen")
        
        try:
            await self.recipient.send(embed=dm_embed)
            logger.info(f"DM sent to recipient {self.recipient.id} for project {project_id}.")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {self.recipient.id}. They may have DMs disabled.")

        # Create and send the DM embed to the creator
        creator_dm_embed = discord.Embed(
            title="Project Created!",
            description=(
                f"Well done! Your project was created! \n\n"
                f"**Recipient:** {self.recipient.mention}\n"
                f"**ID:** `{project_id}`\n"
                f"**Department:** {department}\n\n"
                "Happy developing!"
            ),
            color=8542463 # Hexadecimal value for the blue color
        )
        try:
            await self.creator.send(embed=creator_dm_embed)
            logger.info(f"DM sent to creator {self.creator.id} for project {project_id}.")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {self.creator.id}. They may have DMs disabled.")


        embed = discord.Embed(
            title="Project Created! 🎉",
            description=(
                f"**Project ID:** `{project_id}`\n\n"
                f"**Department:** {department}\n"
                f"**Creator:** {self.creator.mention}\n"
                f"**Recipient:** {self.recipient.mention}\n"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Powered by DevDen")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
        self.stop() # Stop the view after a selection is made


class ProjectCreatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("ProjectCreatorCog initialized successfully")

    @app_commands.command(name='set-project-id', description='Creates a new project and gives it a unique ID.')
    @app_commands.describe(creator='The user who created the project.')
    @app_commands.describe(recipient='The user who is receiving the commission.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def set_project_id_command(self, interaction: discord.Interaction, creator: discord.Member, recipient: discord.Member):
        try:
            view = ProjectSelectView(self, creator, recipient)
            await interaction.response.send_message(
                "Please select the department for your new project:",
                view=view,
                ephemeral=True
            )
            logger.info(f"Project ID creation initiated by {interaction.user.id}.")

        except Exception as e:
            logger.error(f"Error in set-project-id command: {e}", exc_info=True)
            await interaction.response.send_message("An unexpected error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(ProjectCreatorCog(bot))
        logger.info("ProjectCreatorCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add ProjectCreatorCog to bot: {e}", exc_info=True)
        raise
