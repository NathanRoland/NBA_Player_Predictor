from flask import Flask, render_template
from flask_socketio import SocketIO

from nbaAPI import getPlayer, getFixtures, getTeamPlayers, getExpandedTeamsPlayers, getLast5GamesPlayers
from APItoData import *
from APItoDataTeams import *
from webscraping import *
from APIBoxScoresIntoDatabase import *
from RegressionModel import *
#socketio = SocketIO(app)
from dbFunctions import *
import string
from thefuzz import fuzz
import time
#@app.route("/")
#def home():
    #createTeamRosters()

    #return render_template('welcome.html', title = 'Home')

def mainPage():
    print('Fixtures')
    mins_1 = mins_projector_2()
    teams = {}
    for player in mins_1:
        try:
            player_ID = getPlayerID(player)[0][0]
            team = getPlayerDeets(player_ID)[0][2]
            if team not in teams and team != '0':
                team_mins = {}
                players = getTeamPlayers(team)
                for team_player in players:
                    name = team_player[1]
                    player_id = team_player[0]
                    if name in mins_1:
                        team_mins[player_id] = float(mins_1.get(name))
                    else:
                        score = 0
                        mins = 0.0
                        for player_name in mins_1:
                            if score < fuzz.ratio(name, player_name) and fuzz.ratio(name, player_name) > 85:
                                score = fuzz.ratio(name, player_name)
                                mins = float(mins_1.get(player_name))
                        team_mins[player_id] = mins
                teams[team] = team_mins
        except:
            continue
    #print(teams)
    link, games = get_games()
    #while True:
    #try:
    number = int(input("Choose a fixture: "))
    game = link[number]
    gameID = getGameID(games[number][0], games[number][1])[0]
    home_team = getHomeTeam(gameID)[0][0]
    #print(home_team)
    home_team_players = getTeamPlayers(home_team)
    #print(home_team_players)
    away_team = getAwayTeam(gameID)[0][0]
    #print(away_team)
    away_team_players = getTeamPlayers(away_team)
    markets = sportsbet_webscrape(game)
    
    for (player, market) in markets.items():
        #try:
            print("\n"+str(player))
            try:
                player_ID = getPlayerID(player)[0][0]
            except:
                score = 0
                player_ID = None
                for player_name in home_team_players:
                    #print(player_name[1])
                    #print(fuzz.ratio(name, player_name[1]))
                    if score < fuzz.ratio(name, player_name[1]):
                        score = fuzz.ratio(name, player_name[1])
                        player_ID = getPlayerID(player_name[1])
                for player_name in away_team_players:
                    if score < fuzz.ratio(name, player_name[1]):
                        score = fuzz.ratio(name, player_name[1])
                        player_ID = getPlayerID(player_name[1])
            try:
                if player_ID in teams.get(home_team):
                    mins = (teams.get(home_team)).get(player_ID)
                elif player_ID in teams.get(away_team):
                    mins = (teams.get(away_team)).get(player_ID)
                else:
                    continue
            except:
                continue
            print(player_ID, mins)
            player_deets = getPlayerDeets(player_ID)[0]
            team_mins = teams.get(player_deets[2])
            for (name, details) in market.items():
                try:
                    print('\n'+str(name))
                    print("Line:", details.get('player_line'))
                    print("Over:", details.get('above'))
                    print("Under:", details.get('below'))
                    prediction, diff = predict_stats(player, mins, name, details.get('player_line'), team_mins, player_ID, gameID)
                    print("Prediction:", prediction)
                    print("Difference:", diff)
                except:
                    print("calculation error")
        #except:
        #   continue
    #except:
        #print("Error in choosing Fixtures")
        #continue
    return

def predict_stats(playerName, mins, Market, Line, teamMates, playerID, gameID):
    prediction = None
    diff = None
    match Market:
        case 'Player Points Markets':
            #player points
            #print(playerID, mins, teamMates, gameID)
            prediction = get_points_curve(playerID, mins, teamMates, gameID)

        case 'Player Rebounds Markets':
            prediction = get_rebounds_curve(str(playerID), mins, teamMates, str(gameID))
        case 'Player Assists Markets':
            prediction = get_assists_curve(playerID, mins, teamMates)
        case 'Player Three Point Markets':
            prediction = predict_three_points(playerID, mins, teamMates, gameID)
        case 'Player Points, Rebounds and Assists Markets':
            prediction = get_points_curve(playerID, mins, teamMates, gameID) + get_assists_curve(playerID, mins, teamMates) + get_rebounds_curve(playerID, mins, teamMates, gameID)
        case 'Player Points and Rebounds Markets':
            prediction = get_points_curve(playerID, mins, teamMates, gameID) + get_rebounds_curve(playerID, mins, teamMates, gameID)
        case 'Player Points and Assists Markets':
            prediction =get_points_curve(playerID, mins, teamMates, gameID) + get_assists_curve(playerID, mins, teamMates)
        case 'Player Rebounds and Assists Markets':
            prediction = get_assists_curve(playerID, mins, teamMates) + get_rebounds_curve(playerID, mins, teamMates, gameID)
    diff = prediction - float(Line)
    return prediction, diff

    
def refill_player_data_bases():
    resetTeamPlayers()
    try:
        for i in range(0, 30):
            updateTeamPlayers(i)
            time.sleep(65)
    except:
        print('finished')
    get_rest_of_active_players()

def refill_team_data_bases():
    TeamRankings()
    TeamShotLocation()
    OppShots()
    TeamRankingsL5()
    TeamShotLocationL5()
    OppShotsL5()

#@app.route("/getLast5")
def last5():
    last = getLast5GamesPlayers()
    return last

#@app.route("/getOdds")
def getOdds():
    return "Odds"

def generateBoxScores():
    box_score_usage()
    box_score_traditional()
    box_score_scoring()
    box_scoring_advanced()
    box_score_misc()
    box_score_player_track()
    

def generateAverages():
    season_averages()
    last_5_averages()
    last_10_averages()
    #rebounding()
    #player_shot_types()
    #player_shot_areas()

def updateBoxScoresDatabase():
    updateBoxScores()
    position_diffs()
    TeamRankingsL5()
    TeamShotLocationL5()
    OppShotsL5()




#refill_player_data_bases()
#generateAverages()
generateBoxScores()
refill_team_data_bases()

mainPage()

