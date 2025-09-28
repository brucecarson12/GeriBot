"""
GeriBot - A Discord chess bot for tournaments and chess analysis
Main entry point with modular structure
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import nest_asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Apply nest_asyncio for compatibility
nest_asyncio.apply()

# Bot configuration
TOKEN = os.getenv("DiscToken")
bot = commands.Bot('$', intents=discord.Intents.all())

# Global tournament variables (these should be moved to a proper state management system)
tnmtinfo = str()
people = []
players = []
rlist = []
complete_rounds = []
current_round = []
tournament = str()
tourney_status = 'None'


@bot.event
async def on_ready():
    """Event handler for when the bot is ready"""
    print('We have logged in as {0.user}'.format(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='$Geri'))


@bot.event
async def on_command_error(ctx, error):
    """Error handler for commands"""
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Oops! Looks like you didn't give me enough info.")
    elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Command not found. Use `/help` to see available commands.")
    else:
        await ctx.send(f"An error occurred: {error}")


async def load_cogs():
    """Load all command cogs"""
    try:
        await bot.load_extension('bot.commands.general_commands')
        await bot.load_extension('bot.commands.chess_commands')
        await bot.load_extension('bot.commands.lichess_commands')
        print("All cogs loaded successfully")
    except Exception as e:
        print(f"Failed to load cogs: {e}")


async def main():
    """Main function to start the bot"""
    await load_cogs()
    await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot crashed: {e}")
