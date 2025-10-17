# cogs/profile.py
# Implements a /profile command that allows a user to create and view a personal profile.
# The profile data is now stored in a JSON file for persistence across bot restarts.

import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import os

# Set up logging
logger = logging.getLogger(__name__)

# File path for the profile data
PROFILES_FILE = 'profiles.json'

def load_profiles():
    """Loads profiles from the JSON file."""
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("profiles.json file is corrupted. Starting with an empty profile dictionary.")
                return {}
    return {}

def save_profiles(profiles_data):
    """Saves profiles to the JSON file."""
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles_data, f, indent=4)

# Load profiles at the start
profiles = load_profiles()

class ProfileSetupModal(discord.ui.Modal, title='Create/Update Your Profile'):
    """
    A modal for users to input or update their profile information.
    """
    def __init__(self, cog, existing_data=None):
        super().__init__()
        self.cog = cog

        name_default = existing_data.get('name', '') if existing_data else ''
        pronouns_default = existing_data.get('pronouns', '') if existing_data else ''
        intro_default = existing_data.get('intro', '') if existing_data else ''
        links_default = existing_data.get('links', '') if existing_data else ''

        self.name_input = discord.ui.TextInput(
            label="What is your name?",
            style=discord.TextStyle.short,
            required=True,
            max_length=50,
            default=name_default
        )
        self.pronouns_input = discord.ui.TextInput(
            label="What are your pronouns?",
            style=discord.TextStyle.short,
            required=True,
            max_length=20,
            default=pronouns_default
        )
        self.intro_input = discord.ui.TextInput(
            label="Give a small and sweet introduction.",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
            default=intro_default
        )
        self.links_input = discord.ui.TextInput(
            label="Provide portfolio and other links:",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000,
            placeholder="e.g., https://github.com/your-username, https://devden.com/portfolio",
            default=links_default if links_default != "Not provided" else ''
        )
        
        self.add_item(self.name_input)
        self.add_item(self.pronouns_input)
        self.add_item(self.intro_input)
        self.add_item(self.links_input)

    async def on_submit(self, interaction: discord.Interaction):
        """
        Called when the user submits the modal.
        Saves the profile data and sends a confirmation message.
        """
        user_id = str(interaction.user.id) # Use string for dictionary key
        
        # Store the data and save to the file
        profiles[user_id] = {
            "name": self.name_input.value,
            "pronouns": self.pronouns_input.value,
            "intro": self.intro_input.value,
            "links": self.links_input.value or "Not provided" # Handle empty optional field
        }
        save_profiles(profiles)
        
        embed = discord.Embed(
            title="Profile Updated!",
            description="Your profile has been successfully updated. You can now view it with `/profile`.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"User {user_id} updated their profile.")


class ProfileOptionsView(discord.ui.View):
    """
    A view with a dropdown menu for profile options.
    """
    def __init__(self, cog, target_user):
        super().__init__(timeout=180) # Timeout after 3 minutes
        self.cog = cog
        self.target_user = target_user

    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder="Choose a profile action...",
        options=[
            discord.SelectOption(label="View Profile", value="view", description="View your existing profile."),
            discord.SelectOption(label="Update Profile", value="update", description="Update your profile information.")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        """
        Callback for the dropdown menu.
        """
        selected_option = select.values[0]
        user_id = str(interaction.user.id)

        if selected_option == "view":
            profile_data = profiles[user_id]
            embed = discord.Embed(
                title=f"{interaction.user.name}'s Profile!",
                description=(
                    f"**Name:**\n{profile_data['name']}\n\n"
                    f"**Pronouns:**\n{profile_data['pronouns']}\n\n"
                    f"**Here's a small introduction!**\n{profile_data['intro']}\n\n"
                    f"**Portfolio and other links:**\n{profile_data['links']}"
                ),
                color=0xFFFFFF # White color
            )
            embed.set_footer(text="Powered by DevDen")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Profile for {user_id} viewed via dropdown by {interaction.user.id}.")
        
        elif selected_option == "update":
            existing_data = profiles.get(user_id)
            modal = ProfileSetupModal(self.cog, existing_data)
            await interaction.response.send_modal(modal)
            logger.info(f"User {user_id} chose to update their profile via dropdown.")

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("ProfileCog initialized successfully")

    @app_commands.command(name='profile', description='View or create a user profile.')
    @app_commands.describe(user='The user whose profile you want to view. Leave empty for your own.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def profile_command(self, interaction: discord.Interaction, user: discord.Member = None):
        try:
            target_user = user or interaction.user
            user_id = str(target_user.id)
            
            # Scenario 1: User is viewing their own profile
            if target_user == interaction.user:
                if user_id in profiles:
                    # Profile exists, show the dropdown menu
                    view = ProfileOptionsView(self, target_user)
                    await interaction.response.send_message("What would you like to do?", view=view, ephemeral=True)
                else:
                    # Profile doesn't exist, prompt to create it
                    modal = ProfileSetupModal(self)
                    await interaction.response.send_modal(modal)
                return

            # Scenario 2: User is viewing someone else's profile
            if user_id in profiles:
                profile_data = profiles[user_id]
                
                # Create the formatted embed
                embed = discord.Embed(
                    title=f"{target_user.name}'s Profile!",
                    description=(
                        f"**Name:**\n{profile_data['name']}\n\n"
                        f"**Pronouns:**\n{profile_data['pronouns']}\n\n"
                        f"**Here's a small introduction!**\n{profile_data['intro']}\n\n"
                        f"**Portfolio and other links:**\n{profile_data['links']}"
                    ),
                    color=0xFFFFFF # White color
                )
                embed.set_footer(text="Powered by DevDen")
                embed.set_thumbnail(url=target_user.display_avatar.url)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                logger.info(f"Profile for {user_id} viewed by {interaction.user.id}.")
            else:
                # Profile does not exist
                await interaction.response.send_message(f"It looks like {target_user.name} hasn't created a profile yet.", ephemeral=True)
                logger.info(f"Attempt to view non-existent profile for {user_id} by {interaction.user.id}.")

        except Exception as e:
            logger.error(f"Error in profile command: {e}", exc_info=True)
            await interaction.response.send_message("An unexpected error occurred while processing the profile command.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(ProfileCog(bot))
        logger.info("ProfileCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add ProfileCog to bot: {e}", exc_info=True)
        raise
