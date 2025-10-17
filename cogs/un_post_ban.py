# cogs/un_post_ban.py
# Implements a /un-post-ban command to allow a user to post again in specific channels and sends them a DM.

import discord
from discord import app_commands
from discord.ext import commands
import logging

# Set up logging
logger = logging.getLogger(__name__)

class UnPostBanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configurable role ID that can use this command
        self.allowed_role_id = 1409970906981339317
        # Channels to remove the post ban from
        self.banned_channels = [
            1408415131590852761,
            1408415152646389771,
            1408415175975112877
        ]
        logger.info("UnPostBanCog initialized successfully")

    @app_commands.command(name='un-post-ban', description='Allows a user to post in specific channels again.')
    @app_commands.describe(user='The user to un-post-ban.')
    @app_commands.describe(reason='The reason for the un-post-ban.')
    @app_commands.guilds(discord.Object(id=1144662039504109721))
    async def un_post_ban_command(self, interaction: discord.Interaction, user: discord.Member, reason: str):
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

            # Prepare the DM embed
            dm_embed = discord.Embed(
                title="You have been un-post banned! 🟢",
                description=f"Dear {user.name},\n\nYou have been unbanned from posting in DevDen by {interaction.user.name} in these channels:\n\n"
                            + "\n".join([f"<#{channel_id}>" for channel_id in self.banned_channels])
                            + f"\n\nReason: {reason}\n\nWe are excited to see you recruit, sell and complete further tasks with us! Have a great day!",
                color=5832565
            )
            dm_embed.set_footer(text="Powered by DevDen")

            # DM the user
            try:
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                await interaction.response.send_message("Could not DM the user. They may have DMs disabled.", ephemeral=True)
                logger.warning(f"Failed to DM user {user.id} for un-post-ban.")

            # Apply channel-specific permission overwrites to allow posting again
            for channel_id in self.banned_channels:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    # Reset permissions, which effectively allows them to send messages again
                    await channel.set_permissions(user, send_messages=True)
                    logger.info(f"Un-post-ban applied to user {user.id} in channel {channel.id}.")

            await interaction.response.send_message(f"User {user.mention} has been un-post-banned from the specified channels.", ephemeral=True)
            logger.info(f"Un-post-ban command used by {interaction.user.id} on {user.id} for reason: {reason}.")

        except Exception as e:
            logger.error(f"Error in un-post-ban command: {e}", exc_info=True)
            await interaction.response.send_message("An error occurred while un-post-banning the user.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(UnPostBanCog(bot))
        logger.info("UnPostBanCog added to bot successfully")
    except Exception as e:
        logger.error(f"Failed to add UnPostBanCog to bot: {e}", exc_info=True)
        raise
