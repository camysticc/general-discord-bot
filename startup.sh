#!/bin/bash

# This script sets the Discord bot token as an environment variable
# and then runs the bot.
#
# IMPORTANT: Replace YOUR_BOT_TOKEN_HERE with your actual bot token.
# You can get this from the Discord Developer Portal.

export DISCORD_TOKEN="123456789assfghjklqwertyuiopzcvbnm"

# Check if the token was set
if [ -z "$DISCORD_TOKEN" ]; then
    echo "Error: DISCORD_TOKEN is not set."
    exit 1
fi

# Run the bot.py script using python3
echo "Starting the bot..."
python3 bot.py

