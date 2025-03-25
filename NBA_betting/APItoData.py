from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import commonplayerinfo, leaguegamefinder, playerdashptshots, playerdashboardbyshootingsplits, playerdashboardbylastngames, boxscoretraditionalv3, playerdashptreb, commonteamroster
import requests
import urllib3
#import schedule
import time
from bs4 import BeautifulSoup
from thefuzz import fuzz
import pandas
import numpy as np
import os
import sqlite3
import statistics
import json


    #22024 - 2024/25
    #22023 - 2023/24
    #22022 - 2022/23
    #22021 - 2021/22
yearIDs = {"2024-25": 22024, "2023-24": 22023, "2022-23": 22022, "2021-22": 22021}

def averages_and_iqr(data_list):
    Total_Points_Diff = []
    Total_Rebound_Diff = []
    Total_Assists_Diff = []
    Total_FGA_Diff = []
    Total_FGM_Diff = []
    Total_FG_PCT_Diff = []
    Total_FG3A_Diff = []
    Total_FG3M_Diff = []
    Total_FG3_PCT_Diff = []
    for item in data_list:
        Total_Points_Diff.append(item[0])
        Total_Rebound_Diff.append(item[1])
        Total_Assists_Diff.append(item[2])
        Total_FGA_Diff.append(item[3])
        Total_FGM_Diff.append(item[4])
        Total_FG_PCT_Diff.append(item[5])
        Total_FG3A_Diff.append(item[6])
        Total_FG3M_Diff.append(item[7])
        Total_FG3_PCT_Diff.append(item[8])
    Avg_Points_Diff = round(statistics.mean(Total_Points_Diff),2)
    Std_Points_Diff = round(statistics.pstdev(Total_Points_Diff), 2)
    IQR1_Points_Diff, IQR3_Points_Diff = np.percentile(Total_Points_Diff, [75 ,25])
    Avg_Rebound_Diff = round(statistics.mean(Total_Rebound_Diff), 2)
    Std_Rebound_Diff = round(statistics.pstdev(Total_Rebound_Diff), 2)
    IQR1_Rebound_Diff, IQR3_Rebound_Diff = np.percentile(Total_Rebound_Diff, [75 ,25])
    Avg_Assist_Diff = round(statistics.mean(Total_Assists_Diff), 2)
    Std_Assist_Diff = round(statistics.pstdev(Total_Assists_Diff), 2)
    IQR1_Assist_Diff, IQR3_Assist_Diff = np.percentile(Total_Assists_Diff, [75 ,25])
    Avg_FGA_Diff = round(statistics.mean(Total_FGA_Diff), 2)
    Avg_FGM_Diff = round(statistics.mean(Total_FGM_Diff), 2)
    Avg_FG_PCT_Diff = round(statistics.mean(Total_FG_PCT_Diff), 2)
    Avg_FG3A_Diff = round(statistics.mean(Total_FG3A_Diff), 2)
    Avg_FG3M_Diff = round(statistics.mean(Total_FG3M_Diff), 2)
    Avg_FG3_PCT_Diff = round(statistics.mean(Total_FG3_PCT_Diff), 2)
    return Avg_Points_Diff, IQR1_Points_Diff, IQR3_Points_Diff, Std_Points_Diff, Avg_Rebound_Diff, IQR1_Rebound_Diff, IQR3_Rebound_Diff, Std_Rebound_Diff, Avg_Assist_Diff, IQR1_Assist_Diff, IQR3_Assist_Diff, Std_Assist_Diff, Avg_FGA_Diff, Avg_FGM_Diff, Avg_FG_PCT_Diff, Avg_FG3A_Diff, Avg_FG3M_Diff, Avg_FG3_PCT_Diff

def convertDate(dateString):
    dateString, year = dateString.split(",")
    month, day = dateString.split(" ")
    month_converter = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    new_month = month_converter.get(month)
    new_date = year + "-"+ new_month +"-"+ day
    return new_date

def createTeams():
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Teams")
    table = """ CREATE TABLE Teams (
                Team_Name VARCHAR(255) NOT NULL,
                Abbreviation CHAR(3) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                PRIMARY KEY (TeamID)
            ); """
    c.execute(table)

    nba_teams = teams.get_teams()
    for team in nba_teams:
        name = team.get("full_name")
        abbreviation = team.get("abbreviation")
        teamID = team.get("id")
        c.execute('''INSERT INTO Teams (Team_Name, Abbreviation, TeamID) VALUES (?, ?, ?)''', (name, abbreviation, teamID))

    conn.commit()
    conn.close()

team_abb = ['BOS', 'OKC', 'CLE', 'NYK', 'MEM', 'HOU', 'DEN', 'DAL', 'ORL', 'LAL', 'LAC', 'MIL', 'MIA', 'ATL', 'MIN', 'SAS', 'GSW', 'IND', 'PHX', 'DET', 'CHI', 'SAC', 'PHI', 'BKN', 'POR', 'TOR', 'CHA', 'UTA', 'WAS', 'NOP']
team_links = ['https://www.basketball-reference.com/teams/BOS/2025.html', 'https://www.basketball-reference.com/teams/OKC/2025.html', 
              'https://www.basketball-reference.com/teams/CLE/2025.html', 'https://www.basketball-reference.com/teams/NYK/2025.html', 
              'https://www.basketball-reference.com/teams/MEM/2025.html', 'https://www.basketball-reference.com/teams/HOU/2025.html', 
              'https://www.basketball-reference.com/teams/DEN/2025.html', 'https://www.basketball-reference.com/teams/DAL/2025.html', 
              'https://www.basketball-reference.com/teams/ORL/2025.html', 'https://www.basketball-reference.com/teams/LAL/2025.html', 
              'https://www.basketball-reference.com/teams/LAC/2025.html', 'https://www.basketball-reference.com/teams/MIL/2025.html', 
              'https://www.basketball-reference.com/teams/MIA/2025.html', 'https://www.basketball-reference.com/teams/ATL/2025.html', 
              'https://www.basketball-reference.com/teams/MIN/2025.html', 'https://www.basketball-reference.com/teams/SAS/2025.html', 
              'https://www.basketball-reference.com/teams/GSW/2025.html', 'https://www.basketball-reference.com/teams/IND/2025.html', 
              'https://www.basketball-reference.com/teams/PHO/2025.html', 'https://www.basketball-reference.com/teams/DET/2025.html', 
              'https://www.basketball-reference.com/teams/CHI/2025.html', 'https://www.basketball-reference.com/teams/SAC/2025.html', 
              'https://www.basketball-reference.com/teams/PHI/2025.html', 'https://www.basketball-reference.com/teams/BRK/2025.html', 
              'https://www.basketball-reference.com/teams/POR/2025.html', 'https://www.basketball-reference.com/teams/TOR/2025.html', 
              'https://www.basketball-reference.com/teams/CHO/2025.html', 'https://www.basketball-reference.com/teams/UTA/2025.html', 
              'https://www.basketball-reference.com/teams/WAS/2025.html', 'https://www.basketball-reference.com/teams/NOP/2025.html']

def resetTeamPlayers():
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PlayerProfiles")
    table = """ CREATE TABLE PlayerProfiles (
                Player_ID VARCHAR(255) NOT NULL,
                Player_Name VARCHAR(255) NOT NULL,
                TeamID CHAR(25),
                Abbreviation CHAR(3),
                Main_Position VARCHAR(2) NOT NULL,
                Second_Position VARCHAR(2),
                PRIMARY KEY (Player_ID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
            ); """
    c.execute(table)
    conn.commit()
    conn.close()

def updateTeamPlayers(num):
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    i = -1
    id = 1
    #for team in team_links:
    team = team_links[num]
    r = requests.get(team)
    soup = BeautifulSoup(r.content, 'html.parser')
    t = soup.find('div', id="all_roster")
    rows = t.find_all('tr')
    for row in rows:
        new_row = ([el.text.strip() for el in row.find_all('td')])
        if len(new_row) == 0:
            i += 1
            continue
        name = new_row[0]
        main_pos = new_row[1]

        #if they are two way players
        link = 'https://www.basketball-reference.com' + row.find('a').get('href')
        player_page_content = requests.get(link)
        player_page = BeautifulSoup(player_page_content.content, 'html.parser')
        divs = player_page.find('div', id="info")
        content_div = divs.find_all('div')[2]
        position_div = content_div.find_all('p')
        all_positions = ""
        sec_pos = None
        for random_div in position_div:
            all_positions = random_div.text.strip()
            if "Position:" not in all_positions:
                continue
            all_positions = all_positions.replace("Point Guard", "PG")
            all_positions = all_positions.replace("Shooting Guard", "SG")
            all_positions = all_positions.replace("Power Forward", "PF")
            all_positions = all_positions.replace("Small Forward", "SF")
            all_positions = all_positions.replace("Center", "C")
            all_positions = all_positions.replace("\n", "").split("▪")[0].split("    ")[1].split(" and ")
            break

        if len(all_positions) > 1:
            if all_positions[0] == main_pos:
                sec_pos = all_positions[1]
            else:
                sec_pos = all_positions[0]
        team_abbrev = team_abb[num]
        team_ID = teams.find_team_by_abbreviation(team_abbrev).get('id')

        player_deets = players.find_players_by_full_name(name)
        
        if len(player_deets) == 0:
            name = name.split()[0] + " " + name.split()[1]
            player_deets = players.find_players_by_full_name(name)
            if len(player_deets) == 0:
                score = 0
                curr_player = {}
                team = vars(commonteamroster.CommonTeamRoster(team_id=team_ID).common_team_roster).get("data").get("data")
                for player in team:
                    if score < fuzz.ratio(name, player[3]):
                        score = fuzz.ratio(name, player[3])
                        curr_player['id'] = player[-2]
                        curr_player['full_name'] = player[3]
                player_deets = curr_player
            else:
                player_deets = player_deets[0]
        else:
            player_deets = player_deets[0]


        print(player_deets)
        player_ID = player_deets.get('id')
        player_name = name
        
        abbreviation = team_abbrev
        main_position = main_pos
        second_position = sec_pos
        c.execute('''INSERT INTO PlayerProfiles 
                (Player_ID, Player_Name, TeamID, Abbreviation, Main_Position, Second_Position) 
                VALUES (?, ?, ?, ?, ?, ?)''', 
                (player_ID, player_name, team_ID, abbreviation, main_position, second_position))            
    conn.commit()
    conn.close()

def get_rest_of_active_players():
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    players_active = players.get_active_players()
    for player in players_active:
        sql = '''SELECT *
                FROM PlayerProfiles
                WHERE Player_ID=?
                '''
        myresult = c.execute(sql, (player.get('id'),)).fetchall()
        if len(myresult) == 0:
            career = commonplayerinfo.CommonPlayerInfo(player.get('id'))
            career = career.get_dict()
            team_data = career.get("resultSets")[0].get("rowSet")[0]
            positions = team_data[15]
            positions = positions.split("-")
            first_position = str(positions[0])
            second_position = None
            if len(positions) > 1:
                second_position = str(positions[1])
                second_position = second_position.replace("Center", "C")
                second_position = second_position.replace("Forward", "F")
                second_position = second_position.replace("Guard", "G")
            first_position = first_position.replace("Center", "C")
            first_position = first_position.replace("Forward", "F")
            first_position = first_position.replace("Guard", "G")
            c.execute('''INSERT INTO PlayerProfiles
                (Player_ID, Player_Name, TeamID, Abbreviation, Main_Position, Second_Position) 
                VALUES (?, ?, ?, ?, ?, ?)''', 
                (player.get('id'), player.get('full_name'), 0, "NA", first_position, second_position,))            
    conn.commit()
    conn.close()

def getAllFixtures():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Fixtures")
    table = """ CREATE TABLE Fixtures (
                gameID CHAR(25) NOT NULL,
                homeTeamID CHAR(25) NOT NULL,
                awayTeamID CHAR(25) NOT NULL,
                gameDate DATE NOT NULL,
                PRIMARY KEY (gameID),
                FOREIGN KEY (homeTeamID) REFERENCES Teams(TeamID),
                FOREIGN KEY (awayTeamID) REFERENCES Teams(TeamID)
            ); """
    
    c.execute(table)
    
    game_deets = {}
    nba_games = []
    league_games_data = (vars(leaguegamefinder.LeagueGameFinder(season_nullable='2024-25').league_game_finder_results)).get("data").get("data")
    for game in league_games_data:
        if game[2] in team_abb:
            nba_games.append(game)
    for game in nba_games:
        if game[4] in game_deets:
            game_details = game_deets.get(game[4])
            if "home" in game_details:
                game_details["away"] = game[1]
            else:
                game_details["home"] = game[1]
            game_deets[game[4]] = game_details

        else:
            game_details = {}
            if "@" in game[6]:
                game_details["away"] = game[1]
            else:
                game_details["home"] = game[1]
            game_details["date"] = game[5]
            game_deets[game[4]] = game_details
    game_deets.pop("0012400060")
    game_deets.pop("0012400029")
    game_deets.pop("0012400011")
    game_deets.pop("0012400002")

    r = requests.get("https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2024/league/00_full_schedule.json")
    remaining_fixtures = r.json()
    months = remaining_fixtures.get("lscd")
    for month in months:
        mscd = month.get("mscd")
        games = mscd.get("g")
        for game in games:
            gid = game.get("gid")
            date = game.get("gdte")
            home_id = game.get("h").get("tid")
            away_id = game.get("v").get("tid")
            print(gid, date, home_id, away_id)
            if gid not in game_deets:
                print("checl")
                game_deets[gid] = {"date": date, "home": home_id, "away": away_id}
    for key, val in game_deets.items():
        c.execute('''INSERT INTO Fixtures 
                (gameID, homeTeamID, awayTeamID, gameDate) 
                VALUES (?, ?, ?, ?)''', 
                (key, val.get('home'), val.get("away"), val.get("date")))        
    conn.commit()
    conn.close()

def example2():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    game_box_scores = vars(boxscoretraditionalv3.BoxScoreTraditionalV3(game_id='0022400572').player_stats).get("data").get("data")
    for box_score in game_box_scores:
        c.execute(""" INSERT INTO BoxScoreTraditional (Player_ID, gameID, TeamID, mins, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, rebO, rebD, rebT, ast, pts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                    (box_score[6], box_score[0], box_score[1], box_score[14], box_score[15], box_score[16], box_score[17], box_score[18], box_score[19], box_score[20],
                    box_score[24], box_score[25], box_score[26], box_score[27], box_score[32]))
    conn.commit()
    conn.close()
    
def box_score_adv():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PlayerExpandedBoxScores")
    table = """ CREATE TABLE PlayerExpandedBoxScores (
                gameID CHAR(25) NOT NULL,
                teamID CHAR(25) NOT NULL,
                playerID CHAR(25) NOT NULL,
                minutes VARCHAR(6),
                offRating VARCHAR(6),
                defRating VARCHAR(6),
                netRating VARCHAR(7),

                ) """

def player_shot_types():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PlayerShotTypes")
    table = """ CREATE TABLE PlayerShotTypes (
                Player_ID VARCHAR(255) NOT NULL,
                SHOT_TYPE VARCHAR(55),
                FREQ REAL,
                FGM INTEGER,
                FGA INTEGER,
                FG_PCT REAL,
                EFG_PCT REAL,
                FG2_FREQ REAL,
                FG2M INTEGER,
                FG2A INTEGER,
                FG2_PCT REAL,
                FG3_FREQ REAL,
                FG3M INTEGER,
                FG3A INTEGER,
                FG3_PCT REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(PlayerID)
                ); """
    c.execute(table)
    players = c.execute("SELECT Player_ID, TeamID FROM PlayerProfiles").fetchall()
    for player in players:
        try:
            shots = vars(playerdashptshots.PlayerDashPtShots(player_id=player[0], team_id=player[1]).general_shooting).get("data").get("data")
            for shot in shots:
                Player_ID = shot[0]
                shot_type = shot[5]
                freq = shot[6]
                fgm = shot[7]
                fga = shot[8]
                fg_pct = shot[9]
                efg_pct = shot[10]
                fg2_freq = shot[11]
                fg2m = shot[12]
                fg2a = shot[13]
                fg2_pct = shot[14]
                fg3_freq = shot[15]
                fg3m = shot[16]
                fg3a = shot[17]
                fg3_pct = shot[18]
                c.execute(''' INSERT INTO PlayerShotTypes (Player_ID, SHOT_TYPE, FREQ, FGM, FGA, FG_PCT, EFG_PCT, FG2_FREQ, FG2M, FG2A, FG2_PCT, FG3_FREQ, FG3M, FG3A, FG3_PCT) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                  (Player_ID, shot_type, freq, fgm, fga, fg_pct, efg_pct, fg2_freq, fg2m, fg2a, fg2_pct, fg3_freq, fg3m, fg3a, fg3_pct))
        except:
            print("continue")
            c.execute("""INSERT INTO PlayerShotTypes (Player_ID) VALUES (?)""", (player[0],))
            continue
            
    conn.commit()
    conn.close()

def player_shot_areas():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PlayerShotAreas")
    table = """ CREATE TABLE PlayerShotAreas (
                Player_ID VARCHAR(255) NOT NULL,
                Shot_Area VARCHAR(127),
                FGM INTEGER,
                FGA INTEGER,
                FG_PCT REAL,
                FG3M INTEGER,
                FG3A INTEGER,
                FG3_PCT REAL,
                EFG_PCT REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(PlayerID)
                );
            """
    c.execute(table)
    players = c.execute("SELECT Player_ID, TeamID FROM PlayerProfiles").fetchall()
    for player in players:
        try:
            shooting_splits = vars((playerdashboardbyshootingsplits.PlayerDashboardByShootingSplits(player_id=player[0]).shot_area_player_dashboard)).get("data").get("data")
            for splits in shooting_splits:
                c.execute(''' INSERT INTO PlayerShotAreas (Player_ID, Shot_Area, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, EFG_PCT)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                            (player[0], splits[1], splits[2], splits[3], splits[4], splits[5], splits[6], splits[7], splits[8]))
        except:
            print("no")
            c.execute("""INSERT INTO PlayerShotAreas (Player_ID) VALUES (?)""", (player[0],))
            
            continue

    conn.commit()
    conn.close()

#player last 5 and 10 games

def season_averages():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PlayerSeason")
    table = """ CREATE TABLE PlayerSeason (
                Player_ID VARCHAR(255) NOT NULL,
                Games INTEGER,
                Min REAL,
                AV_Min REAL,
                FGM INTEGER,
                AV_FGM REAL,
                FGA INTEGER,
                AV_FGA REAL,
                FG_PCT real,
                FG3M INTEGER,
                AV_FG3M REAL,
                FG3A INTEGER,
                AV_FG3A REAL,
                FG3_PCT REAL,
                REB INTEGER,
                AV_REB REAL,
                AST INTEGER,
                AV_AST REAL,
                PTS INTEGER,
                AV_PTS REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(PlayerID)
                );
            """
    c.execute(table)
    players = c.execute("SELECT Player_ID FROM PlayerProfiles").fetchall()
    for player in players:
        try:
            dashboard = vars((playerdashboardbylastngames.PlayerDashboardByLastNGames(player_id=player[0]).overall_player_dashboard)).get("data").get("data")[0]
            c.execute(''' INSERT INTO PlayerSeason (Player_ID, Games, Min, AV_Min, FGM, AV_FGM, FGA, AV_FGA, FG_PCT, FG3M, AV_FG3M, FG3A, AV_FG3A, FG3_PCT, REB, AV_REB, AST, AV_AST, PTS, AV_PTS)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                        (player[0], dashboard[2], dashboard[6], dashboard[6]/dashboard[2], dashboard[7], dashboard[7]/dashboard[2], dashboard[8], dashboard[8]/dashboard[2], dashboard[9], dashboard[10], dashboard[10]/dashboard[2], dashboard[11], dashboard[11]/dashboard[2], dashboard[12], dashboard[18], dashboard[18]/dashboard[2], dashboard[19], dashboard[19]/dashboard[2], dashboard[26], dashboard[26]/dashboard[2]))
        except:
            print(player[0])
            c.execute(""" INSERT INTO PlayerSeason (Player_ID) VALUES (?) """, (player[0],))
            continue
    conn.commit()
    conn.close()
    
#def last_5_games():
def last_5_averages():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS LastFiveAverages")
    table = """ CREATE TABLE LastFiveAverages (
                Player_ID VARCHAR(255) NOT NULL,
                Games INTEGER,
                Min REAL,
                AV_Min REAL,
                FGM INTEGER,
                AV_FGM REAL,
                FGA INTEGER,
                AV_FGA REAL,
                FG_PCT REAL,
                FG3M INTEGER,
                AV_FG3M REAL,
                FG3A INTEGER,
                AV_FG3A REAL,
                FG3_PCT REAL,
                REB INTEGER,
                AV_REB REAL,
                AST INTEGER,
                AV_AST REAL,
                PTS INTEGER,
                AV_PTS REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(PlayerID)
                );
            """
    c.execute(table)
    players = c.execute("SELECT Player_ID FROM PlayerProfiles").fetchall()
    for player in players:
        try:
            dashboard = vars((playerdashboardbylastngames.PlayerDashboardByLastNGames(player_id=player[0], last_n_games=5).overall_player_dashboard)).get("data").get("data")[0]
            print(dashboard)
            c.execute(''' INSERT INTO LastFiveAverages (Player_ID, Games, Min, AV_Min, FGM, AV_FGM, FGA, AV_FGA, FG_PCT, FG3M, AV_FG3M, FG3A, AV_FG3A, FG3_PCT, REB, AV_REB, AST, AV_AST, PTS, AV_PTS)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                        (player[0], dashboard[2], dashboard[6], dashboard[6]/dashboard[2], dashboard[7], dashboard[7]/dashboard[2], dashboard[8], dashboard[8]/dashboard[2], dashboard[9], dashboard[10], dashboard[10]/dashboard[2], dashboard[11], dashboard[11]/dashboard[2], dashboard[12], dashboard[18], dashboard[18]/dashboard[2], dashboard[19], dashboard[19]/dashboard[2], dashboard[26], dashboard[26]/dashboard[2]))
        except:
            print(player[0])
            c.execute("""INSERT INTO LastFiveAverages (Player_ID) VALUES (?)""", (player[0],))
            continue
    conn.commit()
    conn.close()

#def last_10_games():
def last_10_averages():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS LastTenAverages")
    table = """ CREATE TABLE LastTenAverages (
                Player_ID VARCHAR(255) NOT NULL,
                Games INTEGER,
                Min REAL,
                AV_Min REAL,
                FGM INTEGER,
                AV_FGM REAL,
                FGA INTEGER,
                AV_FGA REAL,
                FG_PCT REAL,
                FG3M INTEGER,
                AV_FG3M REAL,
                FG3A INTEGER,
                AV_FG3A REAL,
                FG3_PCT REAL,
                REB INTEGER,
                AV_REB REAL,
                AST INTEGER,
                AV_AST REAL,
                PTS INTEGER,
                AV_PTS REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(PlayerID)
                );
            """
    c.execute(table)
    players = c.execute("SELECT Player_ID FROM PlayerProfiles").fetchall()
    for player in players:
        try:
            dashboard = vars((playerdashboardbylastngames.PlayerDashboardByLastNGames(player_id=player[0], last_n_games=10).overall_player_dashboard)).get("data").get("data")[0]
            print(dashboard)
            c.execute(''' INSERT INTO LastTenAverages (Player_ID, Games, Min, AV_Min, FGM, AV_FGM, FGA, AV_FGA, FG_PCT, FG3M, AV_FG3M, FG3A, AV_FG3A, FG3_PCT, REB, AV_REB, AST, AV_AST, PTS, AV_PTS)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                        (player[0], dashboard[2], dashboard[6], dashboard[6]/dashboard[2], dashboard[7], dashboard[7]/dashboard[2], dashboard[8], dashboard[8]/dashboard[2], dashboard[9], dashboard[10], dashboard[10]/dashboard[2], dashboard[11], dashboard[11]/dashboard[2], dashboard[12], dashboard[18], dashboard[18]/dashboard[2], dashboard[19], dashboard[19]/dashboard[2], dashboard[26], dashboard[26]/dashboard[2]))
        except:
            print(player[0])
            c.execute("""INSERT INTO LastTenAverages (Player_ID) VALUES (?)""", (player[0],))
            continue
    conn.commit()
    conn.close()

def rebounding():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Rebounding")
    table = """ CREATE TABLE Rebounding (
                Player_ID VARCHAR(255) NOT NULL,
                Reb_Freq_5 REAL,
                Reb_Freq_10 REAL,
                Reb_Freq_OVER REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID)
            );"""
    c.execute(table)

    players = c.execute("SELECT Player_ID, TeamID FROM PlayerProfiles").fetchall()
    for player in players:
        try:
            l5_rebounding = vars(playerdashptreb.PlayerDashPtReb(player_id=player[0], team_id=player[1], last_n_games=5).overall_rebounding).get("data").get("data")[0]
            l10_rebounding = vars(playerdashptreb.PlayerDashPtReb(player_id=player[0], team_id=player[1], last_n_games=10).overall_rebounding).get("data").get("data")[0]
            overall_rebounding = vars(playerdashptreb.PlayerDashPtReb(player_id=player[0], team_id=player[1]).overall_rebounding).get("data").get("data")[0]
            c.execute("""INSERT INTO Rebounding (Player_ID, Reb_Freq_5, Reb_Freq_10, Reb_Freq_OVER) VALUES (?, ?, ?, ?)""", (player[0], l5_rebounding[4], l10_rebounding[4], overall_rebounding[4]))
        except:
            c.execute("""INSERT INTO Rebounding (Player_ID) VALUES (?)""", (player[0],))
            continue
    conn.commit()
    conn.close()


def test():
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    team = vars(commonteamroster.CommonTeamRoster(team_id=1610612760).common_team_roster).get("data").get("data")
    for player in team:
        print(player)
        