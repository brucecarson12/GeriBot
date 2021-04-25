import discord
from dotenv import load_dotenv
import os
from RRTSchedule import *
from functions import *
import requests

TOKEN = os.getenv("DiscToken")
client = discord.Client()
tnmtinfo = str()
people = []
players=[]
rlist=[]
complete_rounds =[]
current_round = []
tournament = str()
tourney_status = 'None'


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel('763912928247414794')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='$Geri'))

@client.event
async def on_message(message):
    if message.author == client.user:
    
        return

    if message.content.startswith('$hello'):
        await message.channel.send("Hey! Did you know 1.Nf3 is the ultimate compromise? \nAre you reti?")
    
    #sends the bot's name inspiration
    if message.content.startswith('$Geri'):
        with open(file="Geri-intro.txt",mode="r") as introtext:
            txtinfo = introtext.read()
            embed = discord.Embed(description = '[My namesake.](https://www.youtube.com/watch?v=uMVtpCPx8ow)')
            await message.channel.send(content=txtinfo, embed=embed)
    
    if message.content.startswith('$resources'):
        with open(file="resources.txt",mode="r") as resourcetext:
            txt = resourcetext.read()
            await message.channel.send(content=txt)

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
            regmsg = await message.channel.send(f"@everyone React with 👍 to join! 0 players joined")
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
            
                if str(reaction.emoji) == "🛑" and user == msg1.author:
                    reg = False


            #turn people into Player()s
            global people
            global players
            players = MakePlayers(players2list)
            for player in players:
                people.append(player.name)
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
    


    #add lichess username to players info
    if message.content.startswith('$addli'):
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        await message.channel.send(f"What's your lichess username?")
        lichessname = await client.wait_for("message", check=check)
        liname = lichessname.content.strip()
        DiscName = str(message.author)
        ID = message.author.id
        for player in players:
            if player.name == DiscName:
                player.add_lichess(liname)                
        player1 = UpdateSheetDiscordID(DiscName,discID=ID,lichessname=liname)
        await message.channel.send(f"Lichess username: {player1['lichess']}")

    #add lichess username to players info
    if message.content.startswith('$findli'):
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        await message.channel.send(f"Please provide 2 lichess usernames. (p1,p2)")
        lichessnames = await client.wait_for("message", check=check)
        player1, player2 = lichessnames.content.split(',')
        gameinfo = lichesslink(player1,player2)
        infotext = "Most Recent Game"
        if gameinfo['live']:
            infotext = "Live Game"
        await message.channel.send(f"{infotext}: <{gameinfo['link']}> \n{gameinfo['opening']}")
        await message.channel.send(gameinfo['giflink'])
        #with open('game.gif', 'wb') as f:
        #    f.write(requests.get(gameinfo['giflink']).content)
        #await message.channel.send(file=discord.File('game.gif'))
        #os.remove('game.gif')
    
    #displays manually updated current tournament file
    if message.content.startswith('$tournament'):
        with open(file="current-tournament.txt",mode="r") as tourntext:
            txtinfo = tourntext.read()
            await message.channel.send(content=txtinfo)

    
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

    if message.content.startswith('$round'):
        rdtxt = "The current round is:"+"\n"
        for match in current_round:
            rdtxt += match.vstxt + ",  "
        await message.channel.send(rdtxt)



    #sends a random puzzle to the chat
    if message.content.startswith('$puzzle'):
        filename2,clue,title,fentxt,solution = randpuzzle()
        await message.channel.send(f"Clue: {clue} \nGame: {title} \n||{solution}|| \n (Please use '||' around your answer to keep it hidden)")
        await message.channel.send(file=discord.File(filename2))
        #os.remove(title + ".svg")
        os.remove(filename2)
    
    #returns last game of message sender
    if message.content.startswith('$lastli'):
        member = str(message.author)
        memberid = message.author.id
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
        await message.channel.send(f"<{lastone['link']}> \n{lastone['opening']}\n{analysis}{result}")
        await message.channel.send(lastone['gif'])

    #ratings and peak for discord users
    if message.content.startswith('$ratings'):
        member = str(message.author)
        memberid = message.author.id
        Sheetinfo = UpdateSheetDiscordID(member,memberid)
        stats = ratinghistory(Sheetinfo['lichess'])
        ratings = f'**Variant**(# games): Current ELO, _Peak ELO_ \n'
        for i in stats:
            if i['peak']:
                ratings += f"**{i['name']}**: {i['currentelo']}, _{i['peak']}_ \n"
        await message.channel.send(ratings)

    #Brings up LiChess profile link using Gsheet for input(Name)
    if message.content.startswith('$liprofile'):
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        await message.channel.send(f"Whose profile would you like?")
        Stuff = await client.wait_for("message", check=check)
        Name = Stuff.content.strip()
        User = UpdateSheetDiscordID(Name)
        LiChessName = User['lichess']
        if LiChessName:
            await message.channel.send(f"<https://lichess.org/@/{LiChessName}> \n <https://lichess.org/insights/{LiChessName}/result/opening>")
        else:
            await message.channel.send(f"This person has not yet added their LiChess name to the bot. Shame Shame Shame.")
    
    if message.content.startswith('$stats'):
        member = str(message.author)
        memberid = message.author.id
        Stats = GetStats(str(memberid))
        Name = Stats['Name']
        TotalWins = Stats['TotalWins']
        TotalLoss = Stats['TotalLoss']
        TotalDraw = Stats['TotalDraws']
        Wins = Stats['TourneyWins']
        await message.channel.send(f"{Name} : {TotalWins}/{TotalLoss}/{TotalDraw} \n Total number of tournament wins: {Wins} ")



@client.event
async def on_reaction_add(reaction, user):
    if reaction == ":thumbsup:":
        await message.channel.send('Nice!')
    

client.run(TOKEN)
