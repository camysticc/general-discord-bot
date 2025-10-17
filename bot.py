import discord
from discord.ext import commands, tasks
import os
import json
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import time
import datetime

class TicketBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)
        self.config = self.load_config()
        self.auto_close_tasks = {}  # Store running auto-close tasks

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            'staff_roles': [],
            'admin_roles': [],
            'blacklist': [],
            'transcript_channel': None,
            'ticket_categories': {},
            'support_category': None,
            'billing_category': None,
            'feedback_category': None,
            'scheduled_closes': {}
        }

        if not os.path.exists(config_path):
            print("Config file not found. Creating default config.")
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            self.config = default_config
            return default_config

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            # Ensure all required keys exist
            for key in default_config:
                if key not in config:
                    print(f"{key} missing in config. Adding default value.")
                    config[key] = default_config[key]
            # Convert role IDs and blacklist to integers, handle invalid entries
            try:
                config['admin_roles'] = [int(id) for id in config['admin_roles'] if str(id).isdigit()]
                config['staff_roles'] = [int(id) for id in config['staff_roles'] if str(id).isdigit()]
                config['blacklist'] = [int(id) for id in config['blacklist'] if str(id).isdigit()]
                # Convert category IDs to integers or None
                for cat in ['support_category', 'billing_category', 'feedback_category']:
                    if config[cat] is not None and str(config[cat]).isdigit():
                        config[cat] = int(config[cat])
                    else:
                        config[cat] = None
                # Ensure scheduled_closes is a dict
                if not isinstance(config['scheduled_closes'], dict):
                    config['scheduled_closes'] = {}
            except (ValueError, TypeError) as e:
                print(f"Error converting IDs to integers: {e}. Using cleaned config.")
            self.config = config
            self.save_config()
            return config
        except json.JSONDecodeError as e:
            print(f"Error decoding config.json: {e}. Using default config.")
            self.config = default_config
            self.save_config()
            return default_config

    def save_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if hasattr(self, 'config'):
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        else:
            print("Warning: save_config called but self.config is not set.")

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        self.check_auto_closes.start()

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        print(f"Loaded config: {self.config}")

    async def on_message(self, message: discord.Message):
        # Ignore bot messages
        if message.author.bot:
            return
        # Check if message is in a ticket channel with scheduled auto-close
        if str(message.channel.id) in self.config['scheduled_closes']:
            print(f"Debug: Message detected in ticket {message.channel.id}. Cancelling auto-close.")
            del self.config['scheduled_closes'][str(message.channel.id)]
            self.save_config()
            if message.channel.id in self.auto_close_tasks:
                self.auto_close_tasks[message.channel.id].cancel()
                del self.auto_close_tasks[message.channel.id]
        await self.process_commands(message)

    @tasks.loop(seconds=60)
    async def check_auto_closes(self):
        current_time = time.time()
        for channel_id, close_time in list(self.config['scheduled_closes'].items()):
            if current_time >= close_time:
                channel = self.get_channel(int(channel_id))
                if channel:
                    try:
                        # Send closure message
                        embed = discord.Embed(
                            title="Ticket Auto-Closed",
                            description="This ticket was closed due to inactivity.\nThis channel will be deleted in 60 seconds.",
                            color=discord.Color.red(),
                            timestamp=datetime.datetime.now(datetime.timezone.utc)
                        )
                        await channel.send(embed=embed)
                        await asyncio.sleep(60)  # Delay deletion by 60 seconds
                        # Generate transcript after deletion
                        transcript_channel = self.get_channel(self.config['transcript_channel'])
                        if transcript_channel:
                            messages = []
                            async for msg in channel.history(limit=None):
                                messages.append(f"[{msg.created_at}] {msg.author.name}: {msg.content}")
                            transcript = "\n".join(reversed(messages))
                            with open(f"transcript_{channel.name}.txt", "w", encoding="utf-8") as f:
                                f.write(transcript)
                            await channel.delete()  # Delete channel
                            await transcript_channel.send(
                                content="Transcript for auto-closed ticket",
                                file=discord.File(f"transcript_{channel.name}.txt")
                            )
                        else:
                            await channel.delete()  # Delete channel if no transcript channel
                    except discord.errors.HTTPException as e:
                        print(f"Debug: Error auto-closing channel {channel_id}: {e}")
                        if transcript_channel:
                            await transcript_channel.send(f"Failed to auto-close channel {channel_id}: {e}")
                # Remove from scheduled_closes
                del self.config['scheduled_closes'][channel_id]
                self.save_config()
                if int(channel_id) in self.auto_close_tasks:
                    del self.auto_close_tasks[int(channel_id)]

load_dotenv()
print(f"Loaded DISCORD_TOKEN: {os.getenv('DISCORD_TOKEN')[:10]}...")  # Debug token (partial)
bot = TicketBot()
token = os.getenv('DISCORD_TOKEN')
if not token:
    print("Error: DISCORD_TOKEN not found in .env file.")
    exit(1)
bot.run(token)