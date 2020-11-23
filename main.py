import discord
from dotenv import load_dotenv
import os
from RRTSchedule import *

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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('yo! Did you know that d4 is the best opening?')

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
            players = list(map(Player,people))
            #create rounds for the tournament
            global rlist
            rlist = rounds(people)
            global current_round
            current_round = rlist[0]
            #create tourney info textarea
            global tnmtinfo
            tnmtinfo = tournament + "\n"
            for f in range(len(rlist)):
                tnmtinfo += ("\n"+"__Round {}:__".format(f+1) + "\n")
                for i in range(len(rlist[f])):
                    tnmtinfo += (str(rlist[f][i].vstxt))
                    if i != len(rlist[f])-1:
                        tnmtinfo += ",   "
            await message.channel.send(tnmtinfo)

    if message.content.startswith('$stoptourney'): 
         tourney_status = 'none'
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
        await message.channel.send(f"What's your Tournament Name, lichess username?")
        lichessname = await client.wait_for("message", check=check)
        names = lichessname.content.split(',')
        for player in players:
            if player.name == str(names[0]).strip():
                player.add_lichess(str(names[1]).strip())
                await message.channel.send(f"Lichess username, {player.li}, added to {player.name}.")

    #
    if message.content.startswith('$addwinner'):
       def check(msg):
            return msg.author == message.author and msg.channel == message.channel
       await message.channel.send(f"Who won?(Enter Player Name or Draw)")       
       scname = await client.wait_for("message", check=check)
       #Draw case
       if scname.content == 'Draw':
           await message.channel.send("Pleae name one player in the game!")
           scname2 = await client.wait_for("message", check=check)
           for match in current_round:
                if scname2.content == match.wplayer or scname2.content == match.bplayer:
                   match.winner(scname.content) #Calls the winner function for match class
                   for player in players:
                       if player.name == match.wplayer or player.name == match.bplayer: #updates player scores
                           player.add_score(0.5)
                           await message.channel.send(f"0.5 points added to {player.name}") #We can work on this being one message later.
                   break
                else: 
                    continue      #probably not needed, but i "grew up" on python 2 sooooo ¯\_(ツ)_/¯
       else:  #winner case
            for match in current_round:
                if scname.content == match.wplayer or scname.content == match.wplayer:
                    match.winner(scname.content)
                    break
            error_check = 0
            for player in players:
                if player.name == scname.content.strip():
                    player.add_score(1)
                    await message.channel.send(f"1 point added to {player.name}")    
                    error_check = 1
                    break
                
            if error_check ==0:
                    await message.channel.send(f"Player name {scname} not found.") 
       TempList = 0 #TempList counts the number of completed matches. 
       for match in current_round:
           if match.status == 'ongoing':
               break
           else:
               TempList += 1
       if TempList == len(current_round): #If all matches in the current_round are complete, the next round becomes the current round.
           complete_rounds.append(current_round)           
           if len(complete_rounds) == len(rlist): # I havent tested this yet, but in theory this should check to see that the tourney is over. We can add the results here.
               await message.channel.send(f"Tournament {tournament} is over!")
               tourney_status = 'complete'
           else:
               current_round = rlist[len(complete_rounds)]
               rdtxt = "@chess The next round has started!"+"\n"
               for match in current_round:
                   rdtxt += match.vstxt + ",  "
               await message.channel.send(rdtxt)



        
        
    if message.content.startswith('$tourney'):
        await message.channel.send(tnmtinfo)
  

""" @client.event
async def on_reaction_add(reaction, user):
    if reaction == ":thumbsup:":
        await message.channel.send('Nice!')
 """    


client.run(TOKEN)
