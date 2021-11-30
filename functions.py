from csv import reader
import random
import chess
import chess.svg
import cairo
import cairosvg
import gspread
from RRTSchedule import *
import berserk
import os
import sys
import json
import chessdotcom as cdc
import datetime as dt


def randpuzzle():
    rand = random.randint(2,1405)
    clue = str()
    fentxt = str()
    solutiontxt = str()
    ori = chess.WHITE

    with open('puzzles.csv', 'r') as puzzles:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(puzzles)
        # Pass reader object to list() to get a list of lists
        puzzlelist = list(csv_reader)[rand]
        #pprint.pprint(list_of_rows)
        clue = str(puzzlelist[0])
        title = str(puzzlelist[1])
        fentxt = str(puzzlelist[2])
        solutiontxt = str(puzzlelist[3])

    if clue.__contains__('Black'):
        ori = chess.BLACK
    board = chess.Board(fentxt)
    boardsvg = chess.svg.board(board=board,orientation=ori)
    filename = title + '.png'

    cairosvg.svg2png(bytestring=boardsvg, write_to=filename)

    return filename, clue, title, fentxt, solutiontxt


#needs more work but looking to pull puzzles similar to how we do it with the above randpuzzle command. Ideally eliminating Cairo at some point.
def lichesspuzzle():
    rand = random.randint(1,353269)
    lipuzzle = dict() #might be better to use a dict to contain puzzle info like gamelink, clue, toPlay, Solution etc.
    ori = chess.WHITE

    with open('lipuzzlesTEST.csv', 'r') as puzzles:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(puzzles)
        # Pass reader object to list() to get a list of lists
        puzzle = list(csv_reader)[rand]
        #pprint.pprint(list_of_rows)
        lipuzzle['themes'] = str(puzzle[8])
        lipuzzle['gameurl'] = str(puzzle[9])
        lipuzzle['fen'] = str(puzzle[12])
        lipuzzle['toPlay'] = str(puzzle[10])
        lipuzzle['solution'] = str(puzzle[13])
        lipuzzle['ID'] = str(puzzle[0])
        lipuzzle['rating'] = f'{puzzle[4]} +/- {puzzle[5]}'


    if lipuzzle['toPlay'].__contains__('Black'):
        ori = chess.BLACK
    board = chess.Board(lipuzzle['fen'])
    boardsvg = chess.svg.board(board=board,orientation=ori)
    lipuzzle['img'] = f"lipuzzle{lipuzzle['ID']}.png"

    #do we need this part??
    #f = open(f"lipuzzle{lipuzzle['ID']}.SVG", "w")
    #f.write(boardsvg)
    #f.close()
    #I don't see it used, maybe left over from Testing^^

    cairosvg.svg2png(bytestring=boardsvg, write_to=lipuzzle['img'])

    return lipuzzle


#----------------------------Double tourney---------------------------------------------------
def MakeRound(Players):
    Losers =[]
    Winners = []
    #Sort players in Losers and Winners Brackets. Doesnt count players who have >1 loss out
    for player in Players:
        if player.losses == 1:
            Losers.append(player)
        elif player.losses == 0:
            Winners.append(player)
            
    if len(Losers) + len(Winners) == 2: #Checks to see if we are on the last match        
        FinalMatch = Match(Losers[0].name,Winners[0].name)
        return FinalMatch , None
    else:
        Losers.append(Player('BYE',None,'BYE')) if len(Losers)%2 ==1 else False
        Winners.append(Player('BYE',None,'BYE')) if len(Winners)%2 ==1 else False #adds BYE player to odd number brackets
        LMatches = []
        WMatches = []
        i,j=0
        while i <len(Losers):
            LMatches.append(Match(Losers[i].name,Losers[i+1].name))
            i+=2
        while j<len(Winners):
            WMatches.append(Match(Winners[j].name,Winners[j+1].name))
            j+=2
        for match in WMatches:
            match.start()
        for match in LMatches:
            match.start()
        return WMatches, LMatches


#---------------------Gsheet functions--------------------------------------------------------
def MakePlayers(PlayerList):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    players =[]
    for p in PlayerList:
        try: 
            cell = sheet.find(str(p))
            players.append(Player(sheet.row_values(cell.row)[0],sheet.row_values(cell.row)[1],sheet.row_values(cell.row)[2]))
        except:
            current_len = len(sheet.col_values(1))
            new_row = current_len +1
            sheet.update_cell(new_row, 1, p)
            sheet.update_cell(new_row, 3, p)
            sheet.update_cell(new_row, 4, 0)
            sheet.update_cell(new_row, 5, 0)
            sheet.update_cell(new_row, 6, 0)
            sheet.update_cell(new_row, 7, 0)
            players.append(Player( p,None,p))
    return players
  
            


def UpdateSheet(players,tnmtinfo):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    
    for p in players:
        TotalMatches = tnmtinfo.count(p.discord) - tnmtinfo.count(f"{p.discord} vs BYE") - tnmtinfo.count(f"BYE vs {p.discord}") 
        cell = sheet.find(p.discord)
        sheet.update_cell(cell.row,1,p.name)
        sheet.update_cell(cell.row,2,p.li)
        sheet.update_cell(cell.row,5,p.TourneyWins)
        sheet.update_cell(cell.row,7,p.TourneyDraws)
        Losses = TotalMatches - p.TourneyWins - p.TourneyDraws

def UpdateSheetDiscordID(discName,discID=None,IRLname=None,lichessname=None,cdcname=None):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    try:
        cell = sheet.find(discName)
    except:
        cell = sheet.find(str(discID))
        sheet.update_cell(cell.row,3,discName)
    if discID:
        sheet.update_cell(cell.row,8,str(discID))
    if IRLname:
        sheet.update_cell(cell.row,1,IRLname)
    if lichessname:
        sheet.update_cell(cell.row,2,lichessname)
    if cdcname:
        sheet.update_cell(cell.row,9,cdcname)
    senderman = dict()
    senderman['discName']  =  discName
    senderman['discID'] = discID
    senderman['lichess'] = sheet.cell(cell.row,2).value
    senderman['cdc'] = sheet.cell(cell.row,9).value
    senderman['IRLname'] = sheet.cell(cell.row,1).value
    return senderman

def AddLiSheet(lichessname,DiscName, DiscID, IRLname = None):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    headers = sheet.row_values(1)
    print(headers)
    try:
        cell = sheet.find(str(DiscID))
        sheet.update_cell(cell.row,2,lichessname)
        if IRLname:
            sheet.update_cell(cell.row,1,IRLname)
        else:
            sheet.update_cell(cell.row,1,DiscName)
    except:
        sheet.append_row([IRLname, lichessname, DiscName,0,0,0,0,str(DiscID)])
    cell = sheet.find(lichessname)    
    senderman = dict()
    senderman['discName']  =  sheet.cell(cell.row,3).value
    senderman['discID'] = DiscID
    senderman['lichess'] = sheet.cell(cell.row,2).value
    senderman['IRLname'] = sheet.cell(cell.row,1).value

    userlistdict = sheet.get_all_records()
    
    print(userlistdict[0]['Lichess Username'])
    return senderman


def GetStats(discID):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    cell = sheet.find(str(discID))    
    stats = dict()
    stats['Name']= sheet.cell(cell.row,1).value
    stats['TourneyWins']= sheet.cell(cell.row,4).value
    stats['TotalWins']=sheet.cell(cell.row,5).value
    stats['TotalLoss']=sheet.cell(cell.row,6).value
    stats['TotalDraws']=sheet.cell(cell.row,7).value
    return stats

#--------------------lichess functions w/ test statements-------------------
LiTOKEN = os.getenv('LiToken')
session = berserk.TokenSession(LiTOKEN)
client = berserk.Client(session)

def OnlineNow():
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    cell = sheet.find(str('Lichess Username'))
    players = sheet.col_values(cell.col)[1:]
    players2 = [x for x in players if str(x) != '']
    onlinetxt = f"Currently On Lichess: \n"
    for player in players2:
        try:
            playeron = client.users.get_realtime_statuses(player)
            if playeron[0]['online']:
                onlinetxt += f" :green_circle: {playeron[0]['name']} \n"
        except:
            continue
    return onlinetxt

def lichesslink(user1,user2):
    p1 = user1.strip()
    p2 = user2.strip() 
    matchesLi = list(client.games.export_by_player(p1,vs=p2,max=3,ongoing=True))
    recgame = dict()
    recgame['id'] = matchesLi[0]['id']
    recgame['live'] = False
    for match in matchesLi:
        if match['status'] == 'started':
            recgame['id'] = match['id']
            recgame['live'] = True
    recgame['link'] = f"https://lichess.org/{recgame['id']}"
    recgame['giflink'] = f"https://lichess1.org/game/export/gif/{recgame['id']}.gif"
    gameinfo  = client.games.export(recgame['id'])
    recgame['opening'] = f"ECO: {gameinfo['opening']['eco']}, {gameinfo['opening']['name']}"
    return recgame

def lichallenge(limit=5,increment=0):
    limsec = limit * 60 #converts minutes to seconds for clock limit
    challenge = client.challenges.create_open(clock_limit=limsec,clock_increment=increment)['challenge']
    return challenge

def lastgame(user1,skip: int):
    p1 = user1.strip().lower()
    lastgame  = list(client.games.export_by_player(p1,max=5))
    game = dict()
    game['id'] = lastgame[skip]['id']
    game['end'] = lastgame[skip]['status']
    game['perf'] = f"{lastgame[skip]['variant'].title()} {lastgame[skip]['speed'].title()} Game"
    game['side'] = 'white' if lastgame[skip]['players']['white']['user']['name'].lower() == p1 else 'black'
    game['link'] = f"https://lichess.org/{game['id']}"
    game['gif'] = f"https://lichess1.org/game/export/gif/{game['side']}/{game['id']}.gif"
    gameinfo  = client.games.export(lastgame[skip]['id'])
    game['analysis'] = None
    game['opening'] = None
    game['badmoves'] = {'inaccuracy':list(),'mistake':list(),'blunder':list()}
    if 'opening' in gameinfo.keys():
        game['opening'] = f"ECO: {gameinfo['opening']['eco']}, {gameinfo['opening']['name']}"
    game['status'] = lastgame[skip]['status']
    if 'winner' in gameinfo.keys():
        game['winner'] = gameinfo['winner']
    if 'analysis' in gameinfo.keys():
        game['analysis'] = gameinfo['players'][game['side']]['analysis']
        moves = gameinfo['moves'].split(' ')
        startno = 3 if game['side'] == 'black' else 2
        for i in range(startno,len(gameinfo['analysis']),2):
            if 'judgment' in gameinfo['analysis'][i]:
                move = str(f"{str(int((i+2)/2))}. {moves[i]}") if startno == 2 else str(f"{str(int((i+1)/2))}... {moves[i]}")
                name = gameinfo['analysis'][i]['judgment']['name'].lower()
                movecomment = gameinfo['analysis'][i]['judgment']['comment']
                game['badmoves'][name].append(move)
    return game

def ratinghistory(user1):
    p1 = user1.strip().lower()
    ratingsget = client.users.get_by_id(p1)
    stats = dict()
    if client.users.get_public_data(p1)['online'] == True:
        stats['txt'] = ":green_circle: Online Now!\n\n"
    else:
        stats['txt'] = ":red_circle: Offline\n\n"
    modes = ['bullet','blitz','rapid','classical','correspondence']
    emojis = [':gun:',':cloud_lightning:',':alarm_clock:',':clock:',':sunny:']
    for i in modes:
        try:
            indx = modes.index(i)
            stats[i] = ratingsget[0]['perfs'][i]['rating']
            #stats['txt'] += f"{emojis[indx]} {i}: {stats[i]} \n"
            stats['txt'] += f"{emojis[indx]} {stats[i]}  "
        except:
            continue
    return stats

#--------------------chess.com functions--------------------------------------

def chessdotcomstats(user1):
    p1 = user1.strip()
    ratings = cdc.get_player_stats(p1)
    stats = dict()
    modes = ['bullet','blitz','rapid','classical','correspondence']
    emojis = [':gun:',':cloud_lightning:',':alarm_clock:',':clock:',':sunny:']
    try:
        if cdc.is_player_online(p1).json['online'] == True:
            stats['txt'] = ":green_circle: Online Now!\n\n"
        else:
            stats['txt'] = ":red_circle: Offline\n\n"
    except:
        stats['txt'] = "\n"
    for i in modes:
        try:
            indx = modes.index(i)
            search = "chess_" + i
            stats[i] = ratings.json['stats'][search]['last']['rating']
            #stats['txt'] += f"{emojis[indx]} {i}: {stats[i]} \n"
            stats['txt'] += f"{emojis[indx]} {stats[i]}  "

        except:
            continue
    return stats

import pgn2gif
import re
import io
import chess.pgn

def chessdotcomlastgame(user1):
    #Temporarily working but it's slow
    p1 = user1.strip()
    today = dt.datetime.today()
    game = cdc.get_player_games_by_month(p1,year=today.year,month=today.month)
    
    if not game.json['games']:
        game = cdc.get_player_games_by_month(p1,year=today.year,month=today.month-1)
    nogames = len(game.json['games']) -  1
    lastgame = game.json['games'][nogames]
    lastgamedict = {
        'pgn':lastgame['pgn'],
        'url':lastgame['url'],
        'wplayer':{
            'name':lastgame['white']['username'],
            'rating':lastgame['white']['rating']
            },
        'bplayer':{
            'name':lastgame['black']['username'],
            'rating':lastgame['black']['rating']
            },
        'vstxt': f"{lastgame['white']['username']} _{lastgame['white']['rating']}_ vs. {lastgame['black']['username']} _{lastgame['black']['rating']}_",
        'result': f"{lastgame['pgn'][-6]}"
        }

    lastgamedict['pgn4gif'] = re.sub(r'{\[%clk \d+:\d+:\d+(\.\d+)?\]} ','',lastgame['pgn'])
    lastgamedict['pgn4gif'] = re.sub(r' [0-9]\.\.\.|[1-9][0-9]\.\.\. ','',lastgamedict['pgn4gif'])
            
    #creates gif--
    pgn = io.StringIO(lastgamedict['pgn4gif'])
    gamepy = chess.pgn.read_game(pgn)
    print(gamepy, file=open("temp/temp.pgn","w"))
    lastgamedict['result']  = gamepy.headers['Result']
    reverse = 0
    if lastgamedict['bplayer']['name'] == p1:
        reverse = 1
    creator = pgn2gif.pgn2gif.PgnToGifCreator(reverse=reverse, duration=0.5, ws_color='#ebecd0', bs_color='#779556')
    creator.create_gif("temp/temp.pgn", out_path="temp/chess.gif")
    
    return lastgamedict