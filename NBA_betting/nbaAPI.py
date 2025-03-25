from nba_api.stats.endpoints import leagueplayerondetails
from nba_api.stats.endpoints import playercareerstats, playernextngames
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import teamgamelog, commonteamroster, playerindex, commonplayerinfo, playergamelogs, teamdetails
import requests



def getPlayer(playerID):
    career = commonplayerinfo.CommonPlayerInfo(playerID)
    career = career.get_dict()
    return career

def getPlayerbyName(find_players_by_full_name):
    full_player_details = commonplayerinfo

def getResults():
    #leagueplayerondetails
    fixtures = teamgamelog.TeamGameLog("1610612742")
    print("test")
    fixtures = fixtures.get_dict().get("resultSets")[0].get("rowSet")
    print("test")
    return fixtures

def getFixtures():
    #leagueplayerondetails
    fixtures = requests.get('https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2023/league/00_full_schedule_week_tbds.json')
    fixtures = fixtures.json()
    #geting month
    fixtures = fixtures.get("lscd")[1].get("mscd").get("g")
    gamedayFixtures = []
    for fixture in fixtures:
        fixturedate = fixture.get("gdtutc")
        if fixturedate == "2024-02-16":
            try:
                htid = teams.find_team_name_by_id(fixture.get("h").get("tid")).get("full_name")
                atid = teams.find_team_name_by_id(fixture.get("v").get("tid")).get("full_name")
                gamedayFixtures.append([htid, atid])
            except:
                next
    #print("test")
    #print(fixtures)
    #AllTeams = teams.get_teams()
    #fixtures = []
    #for team in AllTeams:
    #    roster = getTeamPlayers(team.get("id"))
    #    print(roster)
    #    player = roster[0]
    #    print(player)
    #    playerID = player[-2]
    #    print(playerID)
    #    fixture = playernextngames.PlayerNextNGames(playerID)
    #    fixture = fixture
    #    print(fixture)
    #    fixtures.append([team.get("full_name"), fixture])
    return gamedayFixtures

def getTeamPlayers():
    team = commonteamroster.CommonTeamRoster("1610612742")
    team = team.get_dict()
    team = team.get("resultSets")[0].get("rowSet")
    print(team)
    return team

def getPlayerExpandeedDetails(playerID):
    stats = []
    return stats

def getExpandedTeamsPlayers(teamid):
    players = []
    team = getTeamPlayers(teamid)
    for player in team:
        playerDetails = []
        playerDetails.append(player[3])
        playerDetails.append(player[7])
        playerID = player[-2]
        career = getPlayer(playerID)
        career = career.get("resultSets")[1].get("rowSet")[0]
        playerDetails.append(career[-4])
        playerDetails.append(career[-3])
        playerDetails.append(career[-2])
        players.append(playerDetails)
    return players

def getLast5GamesPlayers():
    #teamID = "1610612742"
    #results = getResults()
    players = []
    team = getTeamPlayers("1610612742")
    for player in team:
        playerDetails = []
        playerDetails.append(player[3])
        playerDetails.append(player[7])
        playerID = player[-2]
        last5games = playergamelogs.PlayerGameLogs(playerID, "5") 
        last5games = last5games.get_dict().get("resultSets")[0].get("rowSet")
        currgames = len(last5games)
        while len(last5games) < 5:
            currgames += 1
            if currgames > 45:
                break
            print(currgames)
            last5games = playergamelogs.PlayerGameLogs(playerID, currgames + 5) 
            last5games = last5games.get_dict().get("resultSets")[0].get("rowSet")
        #for game in last5games:
        points = 0
        games = 0
        rebounds = 0
        assists = 0
        last5gameStats = []
        for game in last5games:
            games += 1
            points += game[31]
            rebounds += game[23]
            assists += game[24]
            last5gameStats.append([game[31], game[23], game[24]])
        points = points/games
        rebounds = rebounds/games
        assists = assists/ games
        playerDetails.append([points, rebounds, assists])
        playerDetails.append(last5gameStats)
        players.append(playerDetails)
        
    return players