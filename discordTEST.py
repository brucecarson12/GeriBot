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
current_round = []

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel('763912928247414794')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('yo!')

    if message.content.startswith('$maketourney'):  
        #checks that message is from original sender
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        #name the tournament
        await message.channel.send(f"Name Your Tournament!")
        msg1 = await client.wait_for("message",check=check)
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
            tnmtinfo += ("__Round {}:__".format(f+1) + "\n" + str(rlist[f]) + "\n")
        await message.channel.send(tnmtinfo)

     
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

    #addscore is not working as intended
    if message.content.startswith('$addscore'):
       def check(msg):
            return msg.author == message.author and msg.channel == message.channel
       await message.channel.send(f"Who won?(Enter Tournament Name)")
       scname = str()
       scname = await client.wait_for("message", check=check)
       for player in players:
           if player.name == scname:
               player.add_score(1)
               await message.channel.send(f"1 point added to {player.name}")     
        
    if message.content.startswith('$tourney'):
        await message.channel.send(tnmtinfo)
  

""" @client.event
async def on_reaction_add(reaction, user):
    if reaction == ":thumbsup:":
        await message.channel.send('Nice!')
 """    

client.run(TOKEN)
