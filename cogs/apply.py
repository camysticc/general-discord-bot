# cogs/apply.py
# Updated to ensure setup function is synchronous to fix RuntimeWarning and TypeError.
# Supports different application fields for different roles.
# Configure the roles, channel, messages, and fields as before.
# To configure role-specific fields:
# 1. In the __init__ method, find the self.role_fields dictionary.
# 2. Add an entry for each role ID you want to customize.
# 3. The key is the integer role ID, and the value is a list of TextInput objects.
# Example: self.role_fields = {
#     123456789012345678: [
#         discord.ui.TextInput(label="What is your coding experience?", style=discord.TextStyle.paragraph, required=True, max_length=1000),
#         discord.ui.TextInput(label="Link to your portfolio/GitHub?", style=discord.TextStyle.short, required=False, placeholder="https://github.com/your-username")
#     ]
# }
# If a role ID is not in this dictionary, it will use the default self.default_fields list.
# You can add up to 5 TextInput items per role (Discord modal limit).
# Styles: discord.TextStyle.short for single-line, .paragraph for multi-line.

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ApplyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable role IDs: Add integers of role IDs here
        self.role_ids = [1409947732151505007, 1409946575853064445]
        
        # Configurable channel ID for sending applications
        self.application_channel_id = 1409946444751966259
        
        # Configurable acceptance message (use {role} placeholder for role name)
        self.accept_message = "Congratulations! Your application for {role} has been accepted."
        
        # Configurable decline message (use {role} and {reason} placeholders)
        self.decline_message = "Sorry, your application for {role} has been declined. Reason: {reason}"
        
        # Default fields to use if a specific role is not configured
        self.default_fields = [
            TextInput(
                label="Why are you a good fit for this role?",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=1000
            )
        ]
        
        # Dictionary to store role-specific fields
        self.role_fields = {
            1409947732151505007: [
                TextInput(label="Can you provide proof of Robux amounts? (y/n)", style=discord.TextStyle.short, required=True, placeholder="y/n"),
                TextInput(label="Attach video of funds open (30d)", style=discord.TextStyle.paragraph, required=True)
            ],
            1409946575853064445: [
                TextInput(label="Proof of sale for previous comms?", style=discord.TextStyle.paragraph, required=True),
                TextInput(label="Provide portfolio:", style=discord.TextStyle.paragraph, required=True),
                TextInput(label="Can someone vouch for you?", style=discord.TextStyle.short, required=False)
            ]
        }
        
        logger.info("ApplyCog initialized successfully")

    @app_commands.command(name='apply-dev', description='Apply for a developer role')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def apply_dev(self, interaction: discord.Interaction):
        try:
            if not self.role_ids:
                await interaction.response.send_message("No roles are configured for applications.", ephemeral=True)
                logger.warning("No roles configured for /apply-dev command")
                return

            guild = interaction.guild
            roles = [guild.get_role(role_id) for role_id in self.role_ids if guild.get_role(role_id)]
            if not roles:
                await interaction.response.send_message("No valid roles found.", ephemeral=True)
                logger.warning("No valid roles found in guild")
                return

            # Create select menu for roles
            select = Select(
                placeholder="Select a role to apply for",
                options=[discord.SelectOption(label=role.name, value=str(role.id)) for role in roles]
            )

            async def select_callback(inter: discord.Interaction):
                role_id = int(select.values[0])
                role = guild.get_role(role_id)
                modal = ApplicationModal(self, role)
                await inter.response.send_modal(modal)

            select.callback = select_callback

            view = View()
            view.add_item(select)

            await interaction.response.send_message("Select the role you want to apply for:", view=view, ephemeral=True)
            logger.info(f"Application process started for user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in apply_dev command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

class ApplicationModal(Modal):
    def __init__(self, cog, role):
        # Determine which fields to use based on the role ID
        fields = cog.role_fields.get(role.id, cog.default_fields)
        super().__init__(title=f"Application for {role.name}")
        self.cog = cog
        self.role = role
        # Add the configurable fields
        for field in fields:
            self.add_item(field)
        logger.info(f"ApplicationModal created for role {role.name} with custom fields")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Collect answers from fields
            answers = "\n".join(f"**{child.label}:** {child.value}" for child in self.children if isinstance(child, TextInput))
            
            # Create embed for application
            embed = discord.Embed(
                title=f"Application for {self.role.name}",
                description=f"Applicant: {interaction.user.mention}\n\n{answers or 'No additional fields provided.'}",
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"User ID: {interaction.user.id}")

            # Send to configured channel with approval view
            channel = self.cog.bot.get_channel(self.cog.application_channel_id)
            if not channel:
                await interaction.response.send_message("Error: Application channel not found.", ephemeral=True)
                logger.error(f"Application channel {self.cog.application_channel_id} not found")
                return

            view = ApprovalView(self.cog, interaction.user, self.role)
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message("Your application has been submitted!", ephemeral=True)
            logger.info(f"Application submitted by {interaction.user.id} for role {self.role.name}")
        except Exception as e:
            logger.error(f"Error in ApplicationModal on_submit: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while submitting your application.", ephemeral=True)

class ApprovalView(View):
    def __init__(self, cog, applicant, role):
        super().__init__(timeout=None)  # Non-persistent by default; restarts will clear active views
        self.cog = cog
        self.applicant = applicant
        self.role = role
        logger.info(f"ApprovalView created for applicant {applicant.id}, role {role.name}")

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, _button: discord.ui.Button):
        try:
            await self.applicant.add_roles(self.role)
            
            # Send the new custom embed to the applicant
            applicant_embed = discord.Embed(
                title="Application Accepted 🟢",
                description=f"Good news {self.applicant.mention}! Your application for **{self.role.name}** was processed and accepted!\n\nThe role has now been given to you and you can use it as proof to whatever commission you're doing. \n\nHappy developing!",
                color=0x1E8857 # A deep green color
            )
            applicant_embed.set_footer(text="Powered by DevDen.")
            await self.applicant.send(embed=applicant_embed)
            
            await interaction.response.send_message("Application accepted and role assigned.", ephemeral=True)
            
            # Send embed to the application channel
            channel = self.cog.bot.get_channel(self.cog.application_channel_id)
            if channel:
                channel_embed = discord.Embed(
                    title="Application Accepted",
                    description=f"**Accepted by:** {interaction.user.mention}\n**Applicant:** {self.applicant.mention}",
                    color=discord.Color.green()
                )
                await channel.send(embed=channel_embed)
                
            logger.info(f"Application accepted for {self.applicant.id}, role {self.role.name}")
        except Exception as e:
            logger.error(f"Error accepting application for {self.applicant.id}: {e}", exc_info=True)
            await interaction.response.send_message(f"Error accepting application: {e}", ephemeral=True)
        finally:
            self.stop()  # Disable buttons after use
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, _button: discord.ui.Button):
        try:
            modal = DeclineModal(self.cog, self.applicant, self.role)
            await interaction.response.send_modal(modal)
            logger.info(f"Decline modal opened for {self.applicant.id}, role {self.role.name}")
        except Exception as e:
            logger.error(f"Error opening decline modal for {self.applicant.id}: {e}", exc_info=True)
            await interaction.response.send_message(f"Error opening decline modal: {e}", ephemeral=True)

class DeclineModal(Modal):
    def __init__(self, cog, applicant, role):
        super().__init__(title="Decline Application")
        self.cog = cog
        self.applicant = applicant
        self.role = role
        self.add_item(TextInput(label="Reason for Decline", style=discord.TextStyle.paragraph, required=True))
        logger.info(f"DeclineModal created for {applicant.id}, role {role.name}")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            reason = self.children[0].value
            
            # Send embed to the applicant
            applicant_embed = discord.Embed(
                title="Application Declined 🔴",
                description=f"Unfortunately, your application for {self.role.name} has been declined.\n\nReason: {reason}\n\nWe thank you for taking the time to apply using our services, and you can submit another application anytime!",
                color=0xC32A1E
            )
            applicant_embed.set_footer(text="Powered by DevDen.")
            await self.applicant.send(embed=applicant_embed)
            
            await interaction.response.send_message("Application declined and reason sent.", ephemeral=True)
            
            # Send embed to the application channel
            channel = self.cog.bot.get_channel(self.cog.application_channel_id)
            if channel:
                channel_embed = discord.Embed(
                    title="Application Declined",
                    description=f"**Declined by:** {interaction.user.mention}\n**Reason:** {reason}",
                    color=discord.Color.red()
                )
                await channel.send(embed=channel_embed)
            
            logger.info(f"Application declined for {self.applicant.id}, role {self.role.name}, reason: {reason}")
        except Exception as e:
            logger.error(f"Error declining application for {self.applicant.id}: {e}", exc_info=True)
            await interaction.response.send_message(f"Error declining application: {e}", ephemeral=True)
        finally:
            # Disable buttons on the original view
            view = interaction.message.view
            if view:
                view.stop()
                for item in view.children:
                    item.disabled = True
                await interaction.message.edit(view=view)

async def setup(bot):
    try:
        await bot.add_cog(ApplyCog(bot))
        logger.info("ApplyCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add ApplyCog to bot: {e}", exc_info=True)
        raise
