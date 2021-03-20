import discord
import discord.ext.commands as commands
from dotenv import load_dotenv
import os
from RRTSchedule import *
from functions import *
import requests
import asyncio
import random

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
    await ctx.send(f"<{lastone['link']}> \n{lastone['opening']}")
    with open('game.gif', 'wb') as f:
        f.write(requests.get(lastone['gif']).content)
    await ctx.send(file=discord.File('game.gif'))
    os.remove('game.gif')

@bot.command()
async def addli(ctx,arg):
    """add your lichess username  Ex. $addli : yourusername"""
    member = str(ctx.author)
    memberid  = ctx.author.id
    Sheetinfo = UpdateSheetDiscordID(member,memberid,lichessname=arg)
    await ctx.send(f"lichess username: {Sheetinfo['lichess']} added to your info.")
    
@bot.command()
async def helpme(ctx):
    """alternate help text with pages and reaction changes"""
    contents = ["This is page 1!", "This is page 2!", "This is page 3!", "This is page 4!"]
    pages = 4
    cur_page = 1
    message = await ctx.send(f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

#====================Tourney Commands ========================================
@bot.command()
async def makeytourney(ctx,TourneyName):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet1 = Book.get_worksheet(1)
    sheet2 = Book.get_worksheet(2)
    if sheet1.acell('B2').value == 'ongoing' :
        await ctx.send("There is already an ongoing Tournament!")
    else:
        #name your players/react to join
        sheet1.update('B1',TourneyName)
        sheet1.update('B2','ongoing')
        regmsg = await ctx.send(f"@everyone React with 👍 to join! 0 players joined")
        def check2(reaction, user):
            return user != regmsg.author and str(reaction) in ["👍","🛑"]
            
        await regmsg.add_reaction("👍")

        players2list = []
        reg = True
        regno = 0
        while reg == True:
            reaction, user = await client.wait_for("reaction_add",check=check2)
            if str(reaction.emoji) == "👍" and user.id not in players2list:
                players2list.append(user.id)
                regno += 1
                await regmsg.edit(content=f"@everyone React with 👍 to join! {regno} players joined")             
            
            if str(reaction.emoji) == "🛑" and user == ctx.author:
                reg = False
        random.shuffle(players2list)
        players = MakePlayers(players2list)
        people = []
        for player in players:
            people.append(player.name)        
        rlist = rounds(people)
        tnmtinfo = TourneyName + "\n"
        for f in range(len(rlist)):
            tnmtinfo += ("\n"+"__Round {}:__".format(f+1) + "\n")
            for i in range(len(rlist[f])):
                tnmtinfo += (str(rlist[f][i].vstxt))
                if i != len(rlist[f])-1:
                    tnmtinfo += ", "
        await ctx.send(tnmtinfo)
        #here is where we update the gsheet





####---------------------to be converted-----------##########

@client.event
async def on_message(message):
    if message.author == client.user:
    
        return

    if message.content.startswith('$maketourney'):  
        #checks that message is from original sender
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        #Checks to see if there is still an ongoing tourney
        global tourney_status
        if tourney_status == 'ongoing':
            await message.channel.send("There is already an ongoing tournament!")
            
            
        else:
            tourney_status = 'ongoing'

        
            #name the tournament
            await message.channel.send(f"Name Your Tournament!")
            msg1 = await client.wait_for("message",check=check)
            global tournament
            tournament = "**" + str(msg1.content) + "**"

            #name your players/react to join
            await message.channel.send(f"Name Your players!")
            msg = await client.wait_for("message",check=check)
            #turn people into Player()s
            global people
            people = msg.content.split(',')
            #strip player names
            for i in range(0,len(people)):
                people[i] = people[i].strip()
            global players
            players = MakePlayers(people)
            #create rounds for the tournament
            global rlist
            rlist = rounds(people)
            global current_round
            current_round = rlist[0]
            for match in current_round:
                match.start()
            #create tourney info textarea
            global tnmtinfo
            tnmtinfo = tournament + "\n"
            for f in range(len(rlist)):
                tnmtinfo += ("\n"+"__Round {}:__".format(f+1) + "\n")
                for i in range(len(rlist[f])):
                    tnmtinfo += (str(rlist[f][i].vstxt))
                    if i != len(rlist[f])-1:
                        tnmtinfo += ", "
            await message.channel.send(tnmtinfo)

    if message.content.startswith('$stoptourney'): 
         tourney_status = 'none'
         tnmtinfo = None
         await message.channel.send(f"Tournament {tournament} has been stopped.")

    #lists players
    if message.content.startswith('$players'):
        pinfo = "__Players:__ \n"
        for player in players:
            pinfo += player.info + "\n"
        await message.channel.send(pinfo)
  
    #
    if message.content.startswith('$addwinner'):
        def check(msg):
             return msg.author == message.author and msg.channel == message.channel
        await message.channel.send(f"Who won?(Enter Player Name or Draw)")       
        scname = await client.wait_for("message", check=check)
        #Draw case
        if scname.content == 'Draw':
            await message.channel.send("Please name one player in the game.")
            scname2 = await client.wait_for("message", check=check)
            for match in current_round:
                if scname2.content.lower() == match.wplayer.lower() or scname2.content.lower() == match.bplayer.lower():
                    if match.status == 'complete':
                        await message.channel.send("This game has already been scored!")
                        break
                    else:
                        match.addwinner(scname2.content) #Calls the winner function for match class
                        for player in players:
                            if player.name == match.wplayer or player.name == match.bplayer: #updates player scores
                                player.add_score(0.5)
                                await message.channel.send(f"0.5 points added to {player.name}") #We can work on this being one message later.

                        break                
        else:  #winner case
            for match in current_round:
                if scname.content.lower() == match.wplayer.lower() or scname.content.lower() == match.bplayer.lower():
                    if match.status == 'complete':
                        await message.channel.send("This game has already been scored!")
                        break
                    else:
                        match.addwinner(scname.content)

                        error_check = 0
                    for player in players:
                        if player.name.lower() == scname.content.lower():
                            player.add_score(1)
                            await message.channel.send(f"1 point added to {player.name}")    
                            error_check = 1
                            break
                    
                    if error_check ==0:
                            await message.channel.send(f"Player name {scname.content} not found.") 
                            break
                
        TempList = 0 #TempList counts the number of completed matches. 
        for match in current_round:
            if match.status == 'started':
                break
            else:
                TempList += 1
        if TempList == len(current_round): #If all matches in the current_round are complete, the next round becomes the current round.
            global complete_rounds
            complete_rounds.append(current_round)           
            if len(complete_rounds) == len(rlist): # I havent tested this yet, but in theory this should check to see that the tourney is over. We can add the results here.
                standings = reversed(sorted(players))                
                sinfo = "__Standings:__ \n"
                i=0
                for player in standings:
                    if i ==0:
                        TourneyWinner = player.name
                        i+=1
                    sinfo += player.info + "\n"
                await message.channel.send(f"Tournament {tournament} is over! Congratulations {TourneyWinner}!!")
                await message.channel.send(sinfo)
                UpdateSheet(players,tnmtinfo)
                tourney_status = 'complete'                
                people = []
                players=[]
                rlist=[]
                complete_rounds =[]
                current_round = []
                
            else:
                current_round = rlist[len(complete_rounds)]
                for match in current_round:
                     match.start()
                rdtxt = "@everyone The next round has started!"+"\n"
                for match in current_round:
                    rdtxt += match.vstxt + ",  "
                await message.channel.send(rdtxt)

        
    if message.content.startswith('$tourney'):
        if not tnmtinfo:
            await message.channel.send('There is currently no active Tournament.')
        else:
            await message.channel.send(tnmtinfo)

    if message.content.startswith('$standings'):
        standings = reversed(sorted(players))
        sinfo = "__Standings:__ \n"
        for player in standings:
            sinfo += player.info + "\n"
        await message.channel.send(sinfo)
     


bot.run(TOKEN)
client.run(TOKEN)