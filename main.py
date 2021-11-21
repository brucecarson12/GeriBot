import discord
import discord.ext.commands as commands
from dotenv import load_dotenv
import os
from RRTSchedule import *
from functions import *
import requests
import asyncio
import nest_asyncio

nest_asyncio.apply()

TOKEN = os.getenv("DiscToken")
client = discord.Client()
bot = commands.Bot('$')
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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Oops! Looks like you didn't give me enough info.")

@bot.command()
async def hello(ctx):
    await ctx.send('Hey! Type $Geri to learn more about me!')

@bot.command()
async def Geri(ctx):
    """an alternate help command"""
    with open(file="Geri-intro.txt",mode="r") as introtext:
            txtinfo = introtext.read()
            embed = discord.Embed(description = '[My namesake.](https://www.youtube.com/watch?v=uMVtpCPx8ow)')
            await ctx.send(content=txtinfo, embed=embed)

@bot.command()
async def resources(ctx):
    """shares some helpful resources for improving at chess!"""
    with open(file="resources.txt",mode="r") as resourcetext:
        txt = resourcetext.read()
        await ctx.send(content=txt)

@bot.command()
async def puzzle(ctx):
    """gives a random puzzle to the chat"""
    filename2,clue,title,fentxt,solution = randpuzzle()
    await ctx.send(f"Clue: {clue} \nGame: {title} \n||{solution}|| \n (Please use '||' around your answer to keep it hidden)")
    await ctx.send(file=discord.File(filename2))
    os.remove(filename2)

@bot.command()
async def challenge(ctx,limit=5,inc=0):
    """Creates an open challenge for 2 players to join. Ex. $challenge time increment, """
    #I'd like to add the name and rated parts of the api call at some point, but that requires some berserk manipulation.
    challenge = lichallenge(limit=limit,increment=inc)
    await ctx.send(f"{challenge['url']}")


@bot.command()
async def onlinenow(ctx,):
    """Lists the current players I see online now."""
    onlinemessage = OnlineNow()
    await ctx.send(f"{onlinemessage}")

#-----Chess.com Commands-----

@bot.command()
async def profile(ctx, name=None):  
    """grabs chess.com and lichess profiles of the name given or the one who calls the command. """
    try:
       Name = str(ctx.author) if not name else name.strip()
       User = UpdateSheetDiscordID(Name)
       ratings = chessdotcomstats(User['cdc'])
       liratings = ratinghistory(User['lichess'])
       await ctx.send(f"**Chess.com**\n{ratings['txt']}\n<https://www.chess.com/member/{User['cdc']}>\n\n**Lichess.org**\n{liratings['txt']}\n<https://lichess.org/@/{User['lichess']}>")
    except:
       await ctx.send(f"Hmm, I couldn't find your name. Use the $addcdc command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command(Ex. $cdcprofile plsBnyce).")


@bot.command()
async def cdcprofile(ctx, name=None):
    """grabs a chess.com profile and stats. example: $cdcprofile username"""
    try:
        Name = str(ctx.author) if not name else name.strip()
        User = UpdateSheetDiscordID(Name)
        ratings = chessdotcomstats(User['cdc'])
        await ctx.send(f"{ratings['txt']} \n<https://www.chess.com/member/{User['cdc']}>")
    except:
        await ctx.send(f"Hmm, I couldn't find your name. Use the $addcdc command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command(Ex. $cdcprofile plsBnyce).")


@bot.command()
async def addcdc(ctx,cdcName, IRLname=None):
    """add your chess.com username  Ex. $addcdc yourusername IRLName[Optional]"""
    try:
        member = str(ctx.author)
        memberid  = ctx.author.id
        Sheetinfo = UpdateSheetDiscordID(member,memberid,IRLname=IRLname,cdcname=cdcName)
        await ctx.send(f"Chess.com username: {Sheetinfo['cdc']} added to your info. Real Name: {Sheetinfo['IRLname']}")
    except:
        await ctx.send(f"Hmm, I don't see you in my records. Please make sure to enter a Chess.com Username after your command.(Ex. $addcdc username)")

@bot.command()
async def lastcdc(ctx,name=None):
    """grabs your last chess.com  game if Geri has your username."""
    try:
        Name = str(ctx.author)
        User = UpdateSheetDiscordID(Name)
        cdcname = User['cdc'] if name == None else name.strip()
        lastgame = chessdotcomlastgame(cdcname)
        await ctx.send(f"{lastgame['result']}\n{lastgame['vstxt']}\n<{lastgame['url']}>")
        await ctx.send(file=discord.File("temp/chess.gif"))

    except:
        await ctx.send(f"Still testing this one. bear with me.")

#-----Lichess.org Commands-----

@bot.command()
async def lipuzzle(ctx):
    """gives a random puzzle from lichess"""
    puzzle = lichesspuzzle()
    await ctx.send(f"Game: <{puzzle['gameurl']}> \nRating: {puzzle['rating']} \nThemes: ||{puzzle['themes']}|| \nSolution: ||{puzzle['solution']}|| \n{puzzle['toPlay']}")
    await ctx.send(file=discord.File(puzzle['img']))
    os.remove(puzzle['img'])


@bot.command()
async def liprofile(ctx, name=None):
    """grabs a lichess profile. example: $liprofile username [CaSe SeNsItIvE usernames!]""" 
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


@bot.command()
async def findli(ctx,user1,user2):
    """finds the most recently started game between 2 lichess users. Ex: $findli user1 user2"""
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


@bot.command()
async def lastli(ctx,skipno=0):
    """This command grabs your last lichess game(based on start date)."""
    member = str(ctx.author)
    memberid = ctx.author.id
    Sheetinfo = UpdateSheetDiscordID(member,memberid)
    if not skipno.is_integer():
        print('string not #')
        skipno = 0  
    lastone = lastgame(Sheetinfo['lichess'],skipno)
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
    await ctx.send(f"<{lastone['link']}> \n{lastone['opening']}\n{analysis}{result}")
    await ctx.send(lastone['gif'])

@bot.command()
async def addli(ctx, Lichessname , IRLname=None):
    """add your lichess username  Ex. $addli yourusername IRLName[Optional]"""
    member = str(ctx.author)
    memberid  = ctx.author.id
    if IRLname:
        Sheetinfo = AddLiSheet(Lichessname.strip(), member, memberid,IRLname.strip())
    else:
        Sheetinfo = AddLiSheet(Lichessname.strip(), member, memberid,IRLname)

    await ctx.send(f"lichess username: {Sheetinfo['lichess']} added to your info.")
     

bot.run(TOKEN)
