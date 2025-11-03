import discord
import discord.ext.commands as commands
from dotenv import load_dotenv
import os
from functions import *
import requests
import asyncio
import nest_asyncio

nest_asyncio.apply()

TOKEN = os.getenv("DiscToken")
bot = commands.Bot('$', intents= discord.Intents.all())
tnmtinfo = str()
people = []
players=[]
rlist=[]
complete_rounds =[]
current_round = []
tournament = str()
tourney_status = 'None'


#------Generic Commands-----
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    channel = bot.get_channel('763912928247414794')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='$Geri'))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Oops! Looks like you didn't give me enough info.")

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
