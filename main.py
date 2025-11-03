import discord
import discord.ext.commands as commands
from discord import app_commands
from dotenv import load_dotenv
import os
from functions import *
import requests
import asyncio
import nest_asyncio

nest_asyncio.apply()

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DiscToken")

# Ensure all necessary intents are enabled
intents = discord.Intents.all()
intents.message_content = True  # Required for message-based commands

bot = commands.Bot('$', intents=intents)

# Optional: Set a test guild ID for faster command syncing during development
# Remove this or set to None for global command syncing (takes up to 1 hour)
TEST_GUILD_ID = None  # Set to a guild ID (int) for instant syncing during testing
# Example: TEST_GUILD_ID = 123456789012345678  # Replace with your guild ID

tnmtinfo = str()
people = []
players=[]
rlist=[]
complete_rounds =[]
current_round = []
tournament = str()
tourney_status = 'None'


# Setup hook to ensure commands are registered
@bot.event
async def setup_hook():
    """This is called when the bot is setting up, before it connects to Discord."""
    print("Setting up bot and registering commands...")
    
    # Commands are automatically registered when decorated with @bot.hybrid_command
    # This hook ensures everything is ready before connecting

#------Generic Commands-----
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(f'Bot ID: {bot.user.id}')
    print(f'Discord.py version: {discord.__version__}')
    
    # Ensure we wait for the bot to be fully ready
    await bot.wait_until_ready()
    
    channel = bot.get_channel(763912928247414794) if bot.get_channel(763912928247414794) else None
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='$Geri'))
    
    # Give a small delay to ensure all commands are registered
    await asyncio.sleep(1)
    
    # List all registered commands BEFORE sync
    print(f"\n📋 Checking registered hybrid commands (before sync):")
    # Get commands from the tree
    tree_commands = bot.tree.get_commands()
    print(f"   Found {len(tree_commands)} command(s) in command tree")
    
    if len(tree_commands) == 0:
        print("   ⚠️  WARNING: No commands found in tree! Commands may not be registering properly.")
        print("   Checking if commands are defined as hybrid commands...")
        # Check all bot commands
        all_commands = list(bot.commands)
        print(f"   Found {len(all_commands)} regular command(s): {[cmd.name for cmd in all_commands]}")
        print("   This suggests commands might be registered as regular commands, not hybrid commands.")
    else:
        for command in tree_commands[:10]:  # Show first 10
            desc = command.description[:50] if command.description else "No description"
            print(f"   - /{command.name}: {desc}...")
        if len(tree_commands) > 10:
            print(f"   ... and {len(tree_commands) - 10} more commands")
    
    # Sync commands with Discord
    print(f"\n🔄 Syncing commands with Discord...")
    
    # Try to validate commands before syncing
    print("   Validating command structure...")
    invalid_commands = []
    for cmd in tree_commands:
        # Check description length
        if cmd.description and len(cmd.description) > 100:
            invalid_commands.append(f"{cmd.name}: description too long ({len(cmd.description)} chars)")
            print(f"   ⚠️  {cmd.name}: description is {len(cmd.description)} characters (max 100)")
        
        # Check parameter descriptions
        if hasattr(cmd, 'parameters'):
            for param in cmd.parameters.values():
                if hasattr(param, 'description') and param.description and len(param.description) > 100:
                    invalid_commands.append(f"{cmd.name}.{param.name}: parameter description too long")
                    print(f"   ⚠️  {cmd.name}.{param.name}: description is {len(param.description)} characters (max 100)")
    
    if invalid_commands:
        print(f"\n❌ Found {len(invalid_commands)} validation issue(s)!")
    
    try:
        if TEST_GUILD_ID:
            # Sync to specific guild for instant updates (good for testing)
            print(f"   Syncing to guild {TEST_GUILD_ID} (instant update)...")
            guild = discord.Object(id=TEST_GUILD_ID)
            synced = await bot.tree.sync(guild=guild)
            print(f"\n✅ Successfully synced {len(synced)} command(s) to guild {TEST_GUILD_ID}")
        else:
            # Sync globally (takes up to 1 hour to propagate)
            print("   Syncing globally (may take up to 1 hour to appear)...")
            synced = await bot.tree.sync()
            print(f"\n✅ Successfully synced {len(synced)} command(s) globally")
            print("   ⚠️  Note: Global commands can take up to 1 hour to appear in Discord")
            print("   💡 Tip: Set TEST_GUILD_ID in main.py for instant command updates during testing")
        
        if len(synced) > 0:
            print("\n📝 Synced commands:")
            for cmd in synced[:20]:  # Show first 20
                print(f"   - /{cmd.name}")
            if len(synced) > 20:
                print(f"   ... and {len(synced) - 20} more commands")
        else:
            print("   ⚠️  WARNING: No commands were synced! Check command definitions.")
            
    except discord.HTTPException as e:
        print(f"\n❌ HTTP Error syncing commands: {e}")
        print(f"   Status: {e.status}")
        print(f"   Code: {e.code if hasattr(e, 'code') else 'N/A'}")
        if hasattr(e, 'text'):
            print(f"   Response text: {e.text}")
        try:
            if hasattr(e, 'response') and e.response:
                import json
                response_data = await e.response.json() if hasattr(e.response, 'json') else str(e.response)
                print(f"   Full response: {json.dumps(response_data, indent=2)}")
        except:
            pass
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Failed to sync commands: {e}")
        import traceback
        traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Oops! Looks like you didn't give me enough info.")
    elif isinstance(error, discord.app_commands.CommandInvokeError):
        await ctx.send(f"An error occurred while executing the command: {error.original}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handle errors for slash commands"""
    # Log the error for debugging
    print(f"❌ Slash command error in {interaction.command.name if interaction.command else 'unknown'}: {error}")
    import traceback
    traceback.print_exc()
    
    # Check if interaction was already responded to
    if interaction.response.is_done():
        # Try to follow up
        try:
            await interaction.followup.send(
                f"❌ An error occurred: {str(error.original) if isinstance(error, discord.app_commands.CommandInvokeError) else str(error)}",
                ephemeral=True
            )
        except:
            pass
    else:
        # Respond to the interaction
        try:
            error_msg = str(error.original) if isinstance(error, discord.app_commands.CommandInvokeError) else str(error)
            # Limit error message length
            if len(error_msg) > 1000:
                error_msg = error_msg[:997] + "..."
            await interaction.response.send_message(
                f"❌ An error occurred: {error_msg}",
                ephemeral=True
            )
        except Exception as e:
            print(f"Failed to send error message: {e}")

@bot.hybrid_command(name="test")
async def test(ctx):
    """Test command to verify hybrid commands are working"""
    await ctx.send("✅ Hybrid commands are working! Both slash and prefix commands should function.")

@bot.hybrid_command(name="sync")
async def sync(ctx):
    """Manually sync slash commands (Admin only)"""
    # Check if user is admin
    if hasattr(ctx, 'author'):
        # Prefix command
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return
    elif hasattr(ctx, 'user'):
        # Slash command
        if not ctx.user.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.", ephemeral=True)
            return
    
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        await ctx.send(f"❌ Failed to sync: {e}")

@bot.hybrid_command(name="hello")
async def hello(ctx):
    """Say hello to Geri!"""
    await ctx.send('Hey! Type $Geri to learn more about me!')

@bot.hybrid_command(name="geri")
async def Geri(ctx):
    """An alternate help command"""
    with open(file="data/Geri-intro.txt",mode="r") as introtext:
            txtinfo = introtext.read()
            embed = discord.Embed(description = '[My namesake.](https://www.youtube.com/watch?v=uMVtpCPx8ow)')
            await ctx.send(content=txtinfo, embed=embed)

@bot.hybrid_command(name="resources")
async def resources(ctx):
    """Shares some helpful resources for improving at chess!"""
    with open(file="data/resources.txt",mode="r") as resourcetext:
        txt = resourcetext.read()
        await ctx.send(content=txt)

@bot.hybrid_command(name="puzzle")
async def puzzle(ctx):
    """Gives a random puzzle to the chat"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        filename2,clue,title,fentxt,solution = randpuzzle()
        await ctx.send(f"Clue: {clue} \nGame: {title} \n||{solution}|| \n (Please use '||' around your answer to keep it hidden)")
        await ctx.send(file=discord.File(filename2))
        os.remove(filename2)
    except Exception as e:
        await ctx.send(f"❌ Error generating puzzle: {str(e)}")
        print(f"Error in puzzle: {e}")
        import traceback
        traceback.print_exc()

@bot.hybrid_command(name="challenge")
@app_commands.describe(limit="Time limit in minutes (default: 5)", inc="Time increment in seconds (default: 0)")
async def challenge(ctx, limit: int = 5, inc: int = 0):
    """Creates an open challenge for 2 players to join"""
    #I'd like to add the name and rated parts of the api call at some point, but that requires some berserk manipulation.
    challenge_result = lichallenge(limit=limit,increment=inc)
    await ctx.send(f"{challenge_result['url']}")


@bot.hybrid_command(name="onlinenow")
async def onlinenow(ctx):
    """Lists the current players I see online now."""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        onlinemessage = OnlineNow()
        await ctx.send(f"{onlinemessage}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
        print(f"Error in onlinenow: {e}")
        import traceback
        traceback.print_exc()

@bot.hybrid_command(name="performance")
@app_commands.describe(score="Your tournament score (points)", opp_ratings="Space-separated opponent ratings (e.g., '1614 1195 1964 1900')")
async def performance(ctx, score: int, opp_ratings: str):
     """Calculates Performance Rating from a tournament"""
     args = [int(a.strip()) for a in opp_ratings.split() if a.strip().isdigit()]
     perfTxt = performanceRatingCalculator(score, args)
     await ctx.send(f"{perfTxt}")
    

#-----Chess.com Commands-----

@bot.hybrid_command(name="profile")
@app_commands.describe(name="Discord username (optional, defaults to you)")
async def profile(ctx, name: str = None):  
    """Grabs chess.com and lichess profiles"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
       Name = str(ctx.author) if not name else name.strip()
       User = UpdateSheetDiscordID(Name)
       # Check if user has usernames registered
       if not User.get('cdc') or User['cdc'] == "":
           await ctx.send(f"❌ Error: No Chess.com username found. Use `/addcdc` to add your Chess.com username.")
           return
       if not User.get('lichess') or User['lichess'] == "":
           await ctx.send(f"❌ Error: No Lichess username found. Use `/addli` to add your Lichess username.")
           return
       ratings = chessdotcomstats(User['cdc'])
       liratings = ratinghistory(User['lichess'])
       await ctx.send(f"**Chess.com** *{User['cdc']}*\n{ratings['txt']}\n<https://www.chess.com/member/{User['cdc']}>\n\n**Lichess.org** *{User['lichess']}*\n{liratings['txt']}\n<https://lichess.org/@/{User['lichess']}>")
    except Exception as e:
       await ctx.send(f"❌ Error: Could not find your profile. Use the $addcdc command to add a username. Error: {str(e)}")
       print(f"Error in profile: {e}")
       import traceback
       traceback.print_exc()


@bot.hybrid_command(name="cdcprofile")
@app_commands.describe(name="Discord username (optional, defaults to you)")
async def cdcprofile(ctx, name: str = None):
    """Grabs a chess.com profile and stats"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        Name = str(ctx.author) if not name else name.strip()
        User = UpdateSheetDiscordID(Name)
        if not User.get('cdc') or User['cdc'] == "":
            await ctx.send(f"❌ Error: No Chess.com username found. Use `/addcdc` to add your Chess.com username.")
            return
        ratings = chessdotcomstats(User['cdc'])
        await ctx.send(f"{ratings['txt']} \n<https://www.chess.com/member/{User['cdc']}>")
    except Exception as e:
        await ctx.send(f"❌ Error: Could not find profile. Use $addcdc to add a username. Error: {str(e)}")
        print(f"Error in cdcprofile: {e}")
        import traceback
        traceback.print_exc()


@bot.hybrid_command(name="addcdc")
@app_commands.describe(cdc_name="Your Chess.com username", irl_name="Your real name (optional)")
async def addcdc(ctx, cdc_name: str, irl_name: str = None):
    """Add your chess.com username"""
    try:
        member = str(ctx.author)
        memberid  = ctx.author.id
        Sheetinfo = UpdateSheetDiscordID(member,memberid,IRLname=irl_name,cdcname=cdc_name)
        await ctx.send(f"Chess.com username: {Sheetinfo['cdc']} added to your info. Real Name: {Sheetinfo['IRLname']}")
    except:
        await ctx.send(f"Hmm, I don't see you in my records. Please make sure to enter a Chess.com Username after your command.(Ex. $addcdc username)")

@bot.hybrid_command(name="lastcdc")
@app_commands.describe(name="Chess.com username (optional)")
async def lastcdc(ctx, name: str = None):
    """Grabs your last chess.com game"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        Name = str(ctx.author)
        memberId = ctx.author.id
        User = UpdateSheetDiscordID(Name, memberId)
        cdcname = User['cdc'] if name == None else name.strip()
        lastgame = chessdotcomlastgame(cdcname)
        await ctx.send(f"{lastgame['result']}\n{lastgame['vstxt']}\n<{lastgame['url']}>")
        await ctx.send(file=discord.File("temp/chess.gif"))

    except Exception as e:
        await ctx.send(f"❌ Error fetching game: {str(e)}")
        print(f"Error in lastcdc: {e}")
        import traceback
        traceback.print_exc()

@bot.hybrid_command(name="cdcleaderboard")
@app_commands.describe(perf="Performance type: streak, bullet, blitz, rapid, classical, or correspondence")
async def cdcleaderboard(ctx, perf: str = 'blitz'):
    """Chess.com Leaderboard generator"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        from functions import cdc_leaderboard
        cdc_derboard = cdc_leaderboard(perf)
        await ctx.send(f"{cdc_derboard}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
        print(f"Error in cdcleaderboard: {e}")
        import traceback
        traceback.print_exc()

#-----Lichess.org Commands-----

@bot.hybrid_command(name="lipuzzle")
async def lipuzzle(ctx):
    """Gives a random puzzle from lichess"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        puzzle = lichesspuzzle()
        await ctx.send(f"Game: <{puzzle['gameurl']}> \nRating: {puzzle['rating']} \nThemes: ||{puzzle['themes']}|| \nSolution: ||{puzzle['solution']}|| \n{puzzle['toPlay']}")
        await ctx.send(file=discord.File(puzzle['img']))
        os.remove(puzzle['img'])
    except Exception as e:
        await ctx.send(f"❌ Error generating puzzle: {str(e)}")
        print(f"Error in lipuzzle: {e}")
        import traceback
        traceback.print_exc()


@bot.hybrid_command(name="liprofile")
@app_commands.describe(name="Lichess username (optional, case sensitive)")
async def liprofile(ctx, name: str = None):
    """Grabs a lichess profile"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        if name:
            name = name.strip()
        else:
            User = UpdateSheetDiscordID(str(ctx.author))
            if not User.get('lichess') or User['lichess'] == "":
                await ctx.send(f"❌ Error: No Lichess username found. Use `/addli` to add your Lichess username.")
                return
            name = User['lichess']
        ratings = ratinghistory(name)
        await ctx.send(f"{ratings['txt']}\n<https://lichess.org/@/{name}> \n<https://lichess.org/insights/{name}/result/opening>")
    except Exception as e:
        await ctx.send(f"❌ Error: Could not find profile. Use $addli to add a username. Error: {str(e)}")
        print(f"Error in liprofile: {e}")
        import traceback
        traceback.print_exc()


@bot.hybrid_command(name="findli")
@app_commands.describe(user1="First lichess username", user2="Second lichess username")
async def findli(ctx, user1: str, user2: str):
    """Finds the most recently started game between 2 lichess users"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        p1, p2 = user1.strip(), user2.strip()
        gameinfo = lichesslink(p1,p2)
        infotext = "Most Recent Game"
        if gameinfo['live']:
            infotext = "Live Game"
        await ctx.send(f"{infotext}: <{gameinfo['link']}> \n{gameinfo['opening']}")
        with open('game.gif', 'wb') as f:
            f.write(requests.get(gameinfo['giflink']).content)
        await ctx.send(file=discord.File('game.gif'))
        os.remove('game.gif')
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
        print(f"Error in findli: {e}")
        import traceback
        traceback.print_exc()


@bot.hybrid_command(name="lastli")
@app_commands.describe(skipno="Number of games to skip (0 = most recent, default: 0)")
async def lastli(ctx, skipno: int = None):
    """Grabs your last lichess game"""
    # For slash commands, we need to defer if this might take more than 3 seconds
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    member = str(ctx.author)
    memberid = ctx.author.id
    try:
        Sheetinfo = UpdateSheetDiscordID(member,memberid)
    except Exception as e:
        await ctx.send(f"❌ Error: Could not find your user information. Error: {str(e)}")
        return
    
    # Check if user has a lichess username
    if not Sheetinfo.get('lichess') or Sheetinfo['lichess'] == "":
        await ctx.send(f"❌ Error: You don't have a Lichess username registered. Use `/addli` to add your Lichess username first.")
        return
        
    try:
        skipno = int(skipno) if skipno is not None else 0
        lastone = lastgame(Sheetinfo['lichess'],skipno)
    except Exception as e:
        #maybe we add a None check to make this a smoother process but it works now.
        try:
            lastone = lastgame(Sheetinfo['lichess'],0)
        except Exception as e2:
            await ctx.send(f"❌ Error fetching game data: {str(e2)}")
            print(f"Error in lastli: {e2}")
            import traceback
            traceback.print_exc()
            return

    result = str()
    if lastone['status'] == 'draw':
        result = "\nResult: 1/2-1/2"
    elif 'winner' in lastone.keys():
        if lastone['winner'] == 'white':
            result = "\nResult: 1-0"
        elif lastone['winner'] == 'black':
            result = "\nResult: 0-1"
    analysis = str()
    if lastone['analysis'] != None:
        analysis = (f"Average Centipawn Loss: {lastone['analysis']['acpl']} \nInaccuracies({lastone['analysis']['inaccuracy']}): {', '.join(lastone['badmoves']['inaccuracy'])} \nMistakes({lastone['analysis']['mistake']}): {', '.join(lastone['badmoves']['mistake'])} \nBlunders({lastone['analysis']['blunder']}): {', '.join(lastone['badmoves']['blunder'])}")
    await ctx.send(f"{lastone['perf']}: <{lastone['link']}> \n{lastone['opening']}\n{analysis}{result} [{lastone['end']}]")
    await ctx.send(lastone['gif'])

@bot.hybrid_command(name="addli")
@app_commands.describe(lichess_name="Your Lichess username", irl_name="Your real name (optional)")
async def addli(ctx, lichess_name: str, irl_name: str = None):
    """Add your lichess username"""
    member = str(ctx.author)
    memberid  = ctx.author.id
    if irl_name:
        Sheetinfo = AddLiSheet(lichess_name.strip(), member, memberid, irl_name.strip())
    else:
        Sheetinfo = AddLiSheet(lichess_name.strip(), member, memberid, irl_name)

    await ctx.send(f"lichess username: {Sheetinfo['lichess']} added to your info.")
    
@bot.hybrid_command(name="lileaderboard")
@app_commands.describe(perf="Performance type: streak, bullet, blitz, rapid, classical, or correspondence")
async def lileaderboard(ctx, perf: str = 'blitz'):
    """Lichess Leaderboard generator"""
    # For slash commands, defer if this might take time
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.defer()
    
    try:
        from functions import leaderboard
        li_derboard = leaderboard(perf)
        await ctx.send(f"{li_derboard}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
        print(f"Error in lileaderboard: {e}")
        import traceback
        traceback.print_exc()
     

bot.run(TOKEN)
