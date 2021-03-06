import discord
import discord.ext.commands as commands
from dotenv import load_dotenv
import os
from RRTSchedule import *
from functions import *
import requests
import asyncio

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


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    channel = bot.get_channel('763912928247414794')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='$Geri'))

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
    #os.remove(title + ".svg")
    os.remove(filename2)

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
    #add logic to pull your own profile if no username is specified
    Name = str()
    if name:
        Name = name.strip()
    else:
        Name = str(ctx.author)
    User = UpdateSheetDiscordID(Name)
    LiChessName = User['lichess']
    ratings = ratinghistory(LiChessName)
    if LiChessName:
        await ctx.send(f"{ratings['txt']} \n<https://lichess.org/@/{LiChessName}> \n <https://lichess.org/insights/{LiChessName}/result/opening>")
    else:
        await ctx.send(f"This person has not yet added their LiChess name to the bot. Shame Shame Shame.")

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
async def lastli(ctx):
    """This command grabs your last lichess game(based on start date)."""
    member = str(ctx.author)
    memberid = ctx.author.id
    Sheetinfo = UpdateSheetDiscordID(member,memberid)
    lastone = lastgame(Sheetinfo['lichess'])
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
    """add your lichess username  Ex. $addli yourusername"""
    member = str(ctx.author)
    memberid  = ctx.author.id
    if IRLname:
        Sheetinfo = AddLiSheet(Lichessname.strip(), member, memberid,IRLname.strip())
    else:
        Sheetinfo = AddLiSheet(Lichessname.strip(), member, memberid,IRLname)

    await ctx.send(f"lichess username: {Sheetinfo['lichess']} added to your info.")
     

bot.run(TOKEN)
