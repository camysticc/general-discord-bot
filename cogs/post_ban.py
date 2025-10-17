# cogs/post_ban.py
# Implements a /post-ban command to prevent a user from posting in specific channels and sends them a DM.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

class PostBanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable role ID that can use this command
        self.allowed_role_id = 1409970906981339317
        # Channels to apply the post ban to
        self.banned_channels = [
            1408415131590852761,
            1408415152646389771,
            1408415175975112877
        ]
        logger.info("PostBanCog initialized successfully")

    @app_commands.command(name='post-ban', description='Bans a user from posting in specific channels.')
    @app_commands.describe(user='The user to post-ban.')
    @app_commands.describe(reason='The reason for the post-ban.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def post_ban_command(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        try:
            # Check if the command runner has the allowed role
            allowed_role = interaction.guild.get_role(self.allowed_role_id)
            if not allowed_role:
                await interaction.response.send_message("Error: Allowed role not found.", ephemeral=True)
                logger.error(f"Allowed role {self.allowed_role_id} not found in guild {interaction.guild.id}")
                return

            if allowed_role not in interaction.user.roles:
                await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
                return

            # Check if the user is a bot
            if user.bot:
                await interaction.response.send_message("You cannot post-ban a bot.", ephemeral=True)
                return
            
            # Prepare the DM embed
            dm_embed = discord.Embed(
                title="Post Banned! 🔴",
                description=f"Dear {user.name},\n\nYou have been banned from posting in DevDen by {interaction.user.name} in these channels:\n\n"
                            + "\n".join([f"<#{channel_id}>" for channel_id in self.banned_channels])
                            + f"\n\nReason: {reason}\n\nWe are very sorry for this ban, you have the right to appeal. You have the right to open a modmail ticket to appeal.",
                color=5814783
            )
            dm_embed.set_footer(text="Powered by DevDen")

            # DM the user
            try:
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                await interaction.response.send_message("Could not DM the user. They may have DMs disabled.", ephemeral=True)
                logger.warning(f"Failed to DM user {user.id} for post-ban.")

            # Apply channel-specific permission overwrites to prevent posting
            for channel_id in self.banned_channels:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.set_permissions(user, send_messages=False)
                    logger.info(f"Post-ban applied to user {user.id} in channel {channel.id}.")
            
            await interaction.response.send_message(f"User {user.mention} has been post-banned from the specified channels.", ephemeral=True)
            logger.info(f"Post-ban command used by {interaction.user.id} on {user.id} for reason: {reason}.")

        except Exception as e:
            logger.error(f"Error in post-ban command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while post-banning the user.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(PostBanCog(bot))
        logger.info("PostBanCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add PostBanCog to bot: {e}", exc_info=True)
        raise
