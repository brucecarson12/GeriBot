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
    
    # Load cogs after bot is ready
    try:
        # Load test commands first
        await bot.load_extension('bot.commands.test_commands')
        print("✅ Test commands loaded")
        
        # Try to load main command modules
        try:
            await bot.load_extension('bot.commands.general_commands')
            print("✅ General commands loaded")
        except Exception as e:
            print(f"❌ Failed to load general commands: {e}")
        
        try:
            await bot.load_extension('bot.commands.chess_commands')
            print("✅ Chess commands loaded")
        except Exception as e:
            print(f"❌ Failed to load chess commands: {e}")
        
        try:
            await bot.load_extension('bot.commands.lichess_commands')
            print("✅ Lichess commands loaded")
        except Exception as e:
            print(f"❌ Failed to load lichess commands: {e}")
        
        print("Cog loading completed")
    except Exception as e:
        print(f"❌ Failed to load cogs: {e}")
        import traceback
        traceback.print_exc()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        import traceback
        traceback.print_exc()
    
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


# Test command to verify bot is working
@bot.hybrid_command(name="test", description="Test command to verify bot is working")
async def test(ctx):
    """Test command to verify the bot is working"""
    await ctx.send("✅ Bot is working! Commands are functional.")


async def main():
    """Main function to start the bot"""
    await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot crashed: {e}")
