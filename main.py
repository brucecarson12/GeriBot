import discord
import discord.ext.commands as commands
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
        print(f"   Response: {e.response}")
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
    if isinstance(error, discord.app_commands.CommandInvokeError):
        await interaction.response.send_message(
            f"An error occurred while executing the command: {str(error.original)}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"An error occurred: {str(error)}",
            ephemeral=True
        )

@bot.hybrid_command(name="test")
async def test(ctx):
    """Test command to verify hybrid commands are working"""
    await ctx.send("✅ Hybrid commands are working! Both slash and prefix commands should function.")

@bot.hybrid_command(name="sync")
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Manually sync slash commands (Admin only)"""
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
    filename2,clue,title,fentxt,solution = randpuzzle()
    await ctx.send(f"Clue: {clue} \nGame: {title} \n||{solution}|| \n (Please use '||' around your answer to keep it hidden)")
    await ctx.send(file=discord.File(filename2))
    os.remove(filename2)

@bot.hybrid_command(name="challenge")
async def challenge(ctx, limit: int = 5, inc: int = 0):
    """Creates an open challenge for 2 players to join. Ex. $challenge time increment"""
    #I'd like to add the name and rated parts of the api call at some point, but that requires some berserk manipulation.
    challenge_result = lichallenge(limit=limit,increment=inc)
    await ctx.send(f"{challenge_result['url']}")


@bot.hybrid_command(name="onlinenow")
async def onlinenow(ctx):
    """Lists the current players I see online now."""
    onlinemessage = OnlineNow()
    await ctx.send(f"{onlinemessage}")

@bot.hybrid_command(name="performance")
async def performance(ctx, score: int, opp_ratings: str):
     """Calculates Performance Rating from a tournament based on score and opponent ratings. Ex. $performance 3 1614 1195 1964 1900"""
     args = [int(a.strip()) for a in opp_ratings.split() if a.strip().isdigit()]
     perfTxt = performanceRatingCalculator(score, args)
     await ctx.send(f"{perfTxt}")
    

#-----Chess.com Commands-----

@bot.hybrid_command(name="profile")
async def profile(ctx, name: str = None):  
    """Grabs chess.com and lichess profiles of the name given or the one who calls the command."""
    try:
       Name = str(ctx.author) if not name else name.strip()
       User = UpdateSheetDiscordID(Name)
       ratings = chessdotcomstats(User['cdc'])
       liratings = ratinghistory(User['lichess'])
       await ctx.send(f"**Chess.com** *{User['cdc']}*\n{ratings['txt']}\n<https://www.chess.com/member/{User['cdc']}>\n\n**Lichess.org** *{User['lichess']}*\n{liratings['txt']}\n<https://lichess.org/@/{User['lichess']}>")
    except:
       await ctx.send(f"Hmm, I couldn't find your name. Use the $addcdc command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command(Ex. $cdcprofile plsBnyce).")


@bot.hybrid_command(name="cdcprofile")
async def cdcprofile(ctx, name: str = None):
    """Grabs a chess.com profile and stats. example: $cdcprofile username"""
    try:
        Name = str(ctx.author) if not name else name.strip()
        User = UpdateSheetDiscordID(Name)
        ratings = chessdotcomstats(User['cdc'])
        await ctx.send(f"{ratings['txt']} \n<https://www.chess.com/member/{User['cdc']}>")
    except:
        await ctx.send(f"Hmm, I couldn't find your name. Use the $addcdc command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command(Ex. $cdcprofile plsBnyce).")


@bot.hybrid_command(name="addcdc")
async def addcdc(ctx, cdc_name: str, irl_name: str = None):
    """Add your chess.com username. Ex. $addcdc yourusername IRLName[Optional]"""
    try:
        member = str(ctx.author)
        memberid  = ctx.author.id
        Sheetinfo = UpdateSheetDiscordID(member,memberid,IRLname=irl_name,cdcname=cdc_name)
        await ctx.send(f"Chess.com username: {Sheetinfo['cdc']} added to your info. Real Name: {Sheetinfo['IRLname']}")
    except:
        await ctx.send(f"Hmm, I don't see you in my records. Please make sure to enter a Chess.com Username after your command.(Ex. $addcdc username)")

@bot.hybrid_command(name="lastcdc")
async def lastcdc(ctx, name: str = None):
    """Grabs your last chess.com game if Geri has your username."""
    try:
        Name = str(ctx.author)
        memberId = ctx.author.id
        User = UpdateSheetDiscordID(Name, memberId)
        cdcname = User['cdc'] if name == None else name.strip()
        lastgame = chessdotcomlastgame(cdcname)
        await ctx.send(f"{lastgame['result']}\n{lastgame['vstxt']}\n<{lastgame['url']}>")
        await ctx.send(file=discord.File("temp/chess.gif"))

    except:
        await ctx.send(f"Still testing this one. bear with me.")

@bot.hybrid_command(name="cdcleaderboard")
async def cdcleaderboard(ctx, perf: str = 'blitz'):
    """Chess.com Leaderboard generator. Defaults to Blitz. perf options = ['streak','bullet','blitz','rapid','classical','correspondence']"""
    from functions import cdc_leaderboard
    cdc_derboard = cdc_leaderboard(perf)
    await ctx.send(f"{cdc_derboard}")

#-----Lichess.org Commands-----

@bot.hybrid_command(name="lipuzzle")
async def lipuzzle(ctx):
    """Gives a random puzzle from lichess"""
    puzzle = lichesspuzzle()
    await ctx.send(f"Game: <{puzzle['gameurl']}> \nRating: {puzzle['rating']} \nThemes: ||{puzzle['themes']}|| \nSolution: ||{puzzle['solution']}|| \n{puzzle['toPlay']}")
    await ctx.send(file=discord.File(puzzle['img']))
    os.remove(puzzle['img'])


@bot.hybrid_command(name="liprofile")
async def liprofile(ctx, name: str = None):
    """Grabs a lichess profile. example: $liprofile username [CaSe SeNsItIvE usernames!]""" 
    try:
        if name:
            name = name.strip()
        else:
            User = UpdateSheetDiscordID(str(ctx.author))
            name = User['lichess']
        ratings = ratinghistory(name)
        await ctx.send(f"{ratings['txt']}\n<https://lichess.org/@/{name}> \n<https://lichess.org/insights/{name}/result/opening>")
    except:
        await ctx.send(f"Hmm, I couldn't find your name. Use the $addli command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command(Ex. $liprofile bnyce).")


@bot.hybrid_command(name="findli")
async def findli(ctx, user1: str, user2: str):
    """Finds the most recently started game between 2 lichess users. Ex: $findli user1 user2"""
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


@bot.hybrid_command(name="lastli")
async def lastli(ctx, skipno: int = None):
    """This command grabs your last lichess game(based on start date)."""
    member = str(ctx.author)
    memberid = ctx.author.id
    Sheetinfo = UpdateSheetDiscordID(member,memberid)
    try:
        skipno = int(skipno) if skipno is not None else 0
        lastone = lastgame(Sheetinfo['lichess'],skipno)
    except:
        #maybe we add a None check to make this a smoother process but it works now.
        lastone = lastgame(Sheetinfo['lichess'],0)

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
async def addli(ctx, lichess_name: str, irl_name: str = None):
    """Add your lichess username. Ex. $addli yourusername IRLName[Optional]"""
    member = str(ctx.author)
    memberid  = ctx.author.id
    if irl_name:
        Sheetinfo = AddLiSheet(lichess_name.strip(), member, memberid, irl_name.strip())
    else:
        Sheetinfo = AddLiSheet(lichess_name.strip(), member, memberid, irl_name)

    await ctx.send(f"lichess username: {Sheetinfo['lichess']} added to your info.")
    
@bot.hybrid_command(name="lileaderboard")
async def lileaderboard(ctx, perf: str = 'blitz'):
    """Lichess Leaderboard generator. Defaults to Blitz. perf options = ['streak','bullet','blitz','rapid','classical','correspondence']"""
    from functions import leaderboard
    li_derboard = leaderboard(perf)
    await ctx.send(f"{li_derboard}")
     

bot.run(TOKEN)
