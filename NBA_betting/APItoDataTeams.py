from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguedashteamshotlocations, leaguedashteamstats, leaguedashoppptshot, boxscoremiscv3, boxscoreplayertrackv3
import requests
import urllib3
#import schedule
import os
from bs4 import BeautifulSoup
from thefuzz import fuzz
import numpy as np

import sqlite3

def TeamRankings():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS TeamRankings")
    table = """ CREATE TABLE TeamRankings (
                TeamID CHAR(25) NOT NULL,
                Games INTEGER,
                Win INTEGER,
                Loss INTEGER,
                FGM INTEGER,
                FGA INTEGER,
                FG_PCT REAL,
                FG3M INTEGER,
                FG3A INTEGER,
                FG3_PCT	REAL,
                OREB INTEGER, 
                DREB INTEGER, 
                REB INTEGER,
                AST INTEGER, 
                TOV	INTEGER,
                STL	INTEGER,
                BLK	INTEGER,
                PTS	INTEGER,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                );"""

    c.execute(table)
    for team in vars(leaguedashteamstats.LeagueDashTeamStats().league_dash_team_stats).get("data").get("data"):
        c.execute('''INSERT INTO TeamRankings (TeamID, Games, Win, Loss, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, OREB, DREB, REB, AST, TOV, STL, BLK, PTS) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (team[0], team[2], team[3], team[4], team[7], team[8], team[9], 
                   team[10], team[11], team[12], team[16], team[17], team[18], team[19],
                   team[20], team[21], team[22], team[26]))

    conn.commit()
    conn.close()

def TeamShotLocation():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS TeamShotLocation")
    table = """ CREATE TABLE TeamShotLocation (
                TeamID CHAR(25) NOT NULL,
                RA_FGM INTEGER,
                RA_FGA INTEGER,
                RA_FGPCT REAL,
                PAINT_FGM INTEGER,
                PAINT_FGA INTEGER,
                PAINT_FGPCT REAL,
                MID_FGM INTEGER,
                MID_FGA INTEGER,
                MID_FGPCT REAL,
                LC3_FGM REAL,
                LC3_FGA REAL,
                LC3_FGPCT REAL,
                RC3_FGM INTEGER,
                RC3_FGA INTEGER,
                RC3_FGPCT REAL,
                AB3_FGM INTEGER,
                AB3_FGA INTEGER,
                AB3_FGPCT REAL,
                C3_FGM INTEGER,
                C3_FGA INTEGER,
                C3_FGPCT REAL,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID))
                """
    c.execute(table)
    for team in vars(leaguedashteamshotlocations.LeagueDashTeamShotLocations().shot_locations).get("data").get("data"):
        print(team)
        c.execute('''INSERT INTO TeamShotLocation (TeamID, RA_FGM, RA_FGA, RA_FGPCT, PAINT_FGM, PAINT_FGA, PAINT_FGPCT, MID_FGM, MID_FGA, MID_FGPCT, 
                  LC3_FGM, LC3_FGA, LC3_FGPCT, RC3_FGM, RC3_FGA, RC3_FGPCT, AB3_FGM, AB3_FGA, AB3_FGPCT, C3_FGM, C3_FGA, C3_FGPCT) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (team[0], team[2], team[3], team[4], team[5], team[6], team[7], team[8], team[9], team[10], team[11], team[12], team[13], team[14],
                   team[15], team[16], team[17], team[18], team[19], team[-3], team[-2], team[-1]))

    conn.commit()
    conn.close()

def OppShots():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS OppShots")
    table = """ CREATE TABLE OppShots (
                TeamID CHAR(25) NOT NULL,
                FGM INTEGER,
                FGA INTEGER,
                FG_PCT REAL,
                F2GM INTEGER,
                F2GA INTEGER,
                F2G_PCT REAL,
                FG3M INTEGER,
                FG3A INTEGER,
                FG3_PCT	REAL,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID))"""
    c.execute(table)
    for team in vars(leaguedashoppptshot.LeagueDashOppPtShot().league_dash_ptshots).get("data").get("data"):
        print(team)
        c.execute(''' INSERT INTO OppShots (TeamID, FGM, FGA, FG_PCT, F2GM, F2GA, F2G_PCT, FG3M, FG3A, FG3_PCT)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                  (team[0], team[6], team[7], team[8], team[11], team[12], team[13], team[15], team[16],team[17]))
    conn.commit()
    conn.close()

#last -5 

def TeamRankingsL5():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS TeamRankingsL5")
    table = """ CREATE TABLE TeamRankingsL5 (
                TeamID CHAR(25) NOT NULL,
                Games INTEGER,
                Win INTEGER,
                Loss INTEGER,
                FGM INTEGER,
                FGA INTEGER,
                FG_PCT REAL,
                FG3M INTEGER,
                FG3A INTEGER,
                FG3_PCT	REAL,
                OREB INTEGER, 
                DREB INTEGER, 
                REB INTEGER,
                AST INTEGER, 
                TOV	INTEGER,
                STL	INTEGER,
                BLK	INTEGER,
                PTS	INTEGER,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                );"""

    c.execute(table)
    for team in vars(leaguedashteamstats.LeagueDashTeamStats(last_n_games=5).league_dash_team_stats).get("data").get("data"):
        print(team)
        c.execute('''INSERT INTO TeamRankingsL5 (TeamID, Games, Win, Loss, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, OREB, DREB, REB, AST, TOV, STL, BLK, PTS) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (team[0], team[2], team[3], team[4], team[7], team[8], team[9], 
                   team[10], team[11], team[12], team[16], team[17], team[18], team[19],
                   team[20], team[21], team[22], team[26]))

    conn.commit()
    conn.close()

def TeamShotLocationL5():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS TeamShotLocationL5")
    table = """ CREATE TABLE TeamShotLocationL5 (
                TeamID CHAR(25) NOT NULL,
                RA_FGM INTEGER,
                RA_FGA INTEGER,
                RA_FGPCT REAL,
                PAINT_FGM INTEGER,
                PAINT_FGA INTEGER,
                PAINT_FGPCT REAL,
                MID_FGM INTEGER,
                MID_FGA INTEGER,
                MID_FGPCT REAL,
                LC3_FGM REAL,
                LC3_FGA REAL,
                LC3_FGPCT REAL,
                RC3_FGM INTEGER,
                RC3_FGA INTEGER,
                RC3_FGPCT REAL,
                AB3_FGM INTEGER,
                AB3_FGA INTEGER,
                AB3_FGPCT REAL,
                C3_FGM INTEGER,
                C3_FGA INTEGER,
                C3_FGPCT REAL,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID))
                """
    c.execute(table)
    for team in vars(leaguedashteamshotlocations.LeagueDashTeamShotLocations(last_n_games=5).shot_locations).get("data").get("data"):
        print(team)
        c.execute('''INSERT INTO TeamShotLocationL5 (TeamID, RA_FGM, RA_FGA, RA_FGPCT, PAINT_FGM, PAINT_FGA, PAINT_FGPCT, MID_FGM, MID_FGA, MID_FGPCT, 
                  LC3_FGM, LC3_FGA, LC3_FGPCT, RC3_FGM, RC3_FGA, RC3_FGPCT, AB3_FGM, AB3_FGA, AB3_FGPCT, C3_FGM, C3_FGA, C3_FGPCT) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (team[0], team[2], team[3], team[4], team[5], team[6], team[7], team[8], team[9], team[10], team[11], team[12], team[13], team[14],
                   team[15], team[16], team[17], team[18], team[19], team[-3], team[-2], team[-1]))

    conn.commit()
    conn.close()

def OppShotsL5():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS OppShotsL5")
    table = """ CREATE TABLE OppShotsL5 (
                TeamID CHAR(25) NOT NULL,
                FGM INTEGER,
                FGA INTEGER,
                FG_PCT REAL,
                F2GM INTEGER,
                F2GA INTEGER,
                F2G_PCT REAL,
                FG3M INTEGER,
                FG3A INTEGER,
                FG3_PCT	REAL,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID))"""
    c.execute(table)
    for team in vars(leaguedashoppptshot.LeagueDashOppPtShot(last_n_games_nullable=5).league_dash_ptshots).get("data").get("data"):
        print(team)
        c.execute(''' INSERT INTO OppShotsL5 (TeamID, FGM, FGA, FG_PCT, F2GM, F2GA, F2G_PCT, FG3M, FG3A, FG3_PCT)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                  (team[0], team[6], team[7], team[8], team[11], team[12], team[13], team[15], team[16],team[17]))
    conn.commit()
    conn.close()



#another dataset
#- rebound chances given up (offensive rebound)
#- types of shots, (fast break, turnover, SECOND CHANCE, PAINT)Reb_Cha_GU
#Reb_Cha_GU - HOW MANY DEFENSIVE REBOUND CHANCES ARE THEY GIVING UP
#Reb_Cha_CL - HOW MANY CHANCES DO THEY HAVE TO CLAIM OFFENSIVE REBOUNDS
def team_defensive_rankings():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS TeamDefenseRankings")
    table = """ CREATE TABLE TeamDefenseRankings (
                TeamID CHAR(25) NOT NULL, 
                Reb_Cha_GU INTEGER, 
                Reb_Cha_CL INTEGER,
                Fst_Brk INTEGER,
                Turn INTEGER,
                Sch INTEGER,
                Pnt INTEGER,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                );"""
    c.execute(table)
    teams = c.execute("SELECT TeamID FROM Teams").fetchall()
    for team in teams:
        games = c.execute("SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ? ORDER BY gameDate DESC", (team[0], team[0])).fetchall()
        recorded_games = c.execute("SELECT DISTINCT gameID from BoxScoreScoring").fetchall()
        recorded_games_list = [row[0] for row in recorded_games]
        games_list = [row[0] for row in games]
        finished_games = [x for x in games_list if x in recorded_games_list]

        team_deets = {"TeamID": team[0], "Reb_Cha_GU": 0, "Reb_Cha_CL": 0, "Fst_Brk": 0, "Turn": 0, "Sch": 0, "Pnt": 0}
        for game in finished_games:
            box_scores_misc = c.execute("SELECT * FROM BoxScoreMisc WHERE gameID = ?", (game,)).fetchall()
            box_scores_track = c.execute("SELECT * FROM BoxScoreTrack WHERE gameID = ?", (game,)).fetchall()
            for box_score in box_scores_misc:
                if box_score[2] != team[0]:
                    team_deets["Turn"] += box_score[4]
                    team_deets["Sch"] += box_score[5]
                    team_deets["Fst_Brk"] += box_score[6]
                    team_deets["Pnt"] += box_score[7]
            
            for box_score in box_scores_track:
                if box_score[2] != team[0]:
                    team_deets["Reb_Cha_GU"] += box_score[4]
                else:
                    team_deets["Reb_Cha_CL"] += box_score[5]
        print(team_deets)
        c.execute("""INSERT INTO TeamDefenseRankings (TeamID, Reb_Cha_GU, Reb_Cha_CL, Fst_Brk, Turn, Sch, Pnt) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (team_deets["TeamID"], team_deets["Reb_Cha_GU"], team_deets["Reb_Cha_CL"], team_deets["Fst_Brk"], team_deets["Turn"], team_deets['Sch'], team_deets["Pnt"]))
    conn.commit()
    conn.close()
#- also do for last 5

def team_defensive_rankings_l5():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS TeamDefenseRankingsL5")
    table = """ CREATE TABLE TeamDefenseRankingsL5 (
                TeamID CHAR(25) NOT NULL, 
                Reb_Cha_GU INTEGER, 
                Reb_Cha_CL INTEGER,
                Fst_Brk INTEGER,
                Turn INTEGER,
                Sch INTEGER,
                Pnt INTEGER,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                );"""
    c.execute(table)
    teams = c.execute("SELECT TeamID FROM Teams").fetchall()
    for team in teams:
        games = c.execute("SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ? ORDER BY gameDate DESC", (team[0], team[0])).fetchall()
        recorded_games = c.execute("SELECT DISTINCT gameID from BoxScoreScoring").fetchall()
        recorded_games_list = [row[0] for row in recorded_games]
        games_list = [row[0] for row in games]
        l5_games = [x for x in games_list if x in recorded_games_list][0:5]
        team_deets = {"TeamID": team[0], "Reb_Cha_GU": 0, "Reb_Cha_CL": 0, "Fst_Brk": 0, "Turn": 0, "Sch": 0, "Pnt": 0}
        for game in l5_games:
            box_scores_misc = c.execute("SELECT * FROM BoxScoreMisc WHERE gameID = ?", (game,)).fetchall()
            box_scores_track = c.execute("SELECT * FROM BoxScoreTrack WHERE gameID = ?", (game,)).fetchall()
            for box_score in box_scores_misc:
                if box_score[2] != team[0]:
                    team_deets["Turn"] += box_score[4]
                    team_deets["Sch"] += box_score[5]
                    team_deets["Fst_Brk"] += box_score[6]
                    team_deets["Pnt"] += box_score[7]
            for box_score in box_scores_track:
                if box_score[2] != team[0]:
                    team_deets["Reb_Cha_GU"] += box_score[4]
                else:
                    team_deets["Reb_Cha_CL"] += box_score[5]
        print(team_deets)
        c.execute("""INSERT INTO TeamDefenseRankingsL5 (TeamID, Reb_Cha_GU, Reb_Cha_CL, Fst_Brk, Turn, Sch, Pnt) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (team_deets["TeamID"], team_deets["Reb_Cha_GU"], team_deets["Reb_Cha_CL"], team_deets["Fst_Brk"], team_deets["Turn"], team_deets['Sch'], team_deets["Pnt"]))
    conn.commit()
    conn.close()

#positional differences

def position_diffs():
    file_path = os.path.join('database', "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PositionStatsDef")
    table = """ CREATE TABLE PositionStatsDef (
                TeamID CHAR(25) NOT NULL, 
                pts_diff_C REAL,
                avg_pts_C REAL,
                rebs_diff_C REAL,
                avg_rebs_C REAL,
                pts_diff_SF REAL,
                avg_pts_SF REAL,
                rebs_diff_SF REAL,
                avg_rebs_SF REAL,
                pts_diff_PF REAL,
                avg_pts_PF REAL,
                rebs_diff_PF REAL,
                avg_rebs_PF REAL,
                pts_diff_SG REAL,
                avg_pts_SG REAL,
                rebs_diff_SG REAL,
                avg_rebs_SG REAL,
                pts_diff_PG REAL,
                avg_pts_PG REAL,
                rebs_diff_PG REAL,
                avg_rebs_PG REAL,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                );"""
    c.execute(table)
    teams = c.execute("SELECT TeamID FROM Teams").fetchall()
    for team in teams:
        team_totals = {'C': {'rebT': 0, 'pts': 0, 'pts_diff': 0, 'reb_diff': 0}, 
                       'SF': {'rebT': 0, 'pts': 0, 'pts_diff': 0, 'reb_diff': 0}, 
                       'PF': {'rebT': 0, 'pts': 0, 'pts_diff': 0, 'reb_diff': 0}, 
                       'SG': {'rebT': 0, 'pts': 0, 'pts_diff': 0, 'reb_diff': 0}, 
                       'PG': {'rebT': 0, 'pts': 0, 'pts_diff': 0, 'reb_diff': 0}}
        print(team)
        games = c.execute("SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ?", (team[0], team[0])).fetchall()
        games_num = 0
        for game in games:
            box_scores = c.execute("SELECT mins, rebT, pts, Player_ID, TeamID FROM BoxScoreTraditional WHERE gameID = ?", (game[0],)).fetchall()
            games_num += 1
            for box_score in box_scores:
                if box_score[4] != team[0]:
                    time = 0
                    try:
                        mins, sec = box_score[0].split(":")
                        time = int(mins) + float(sec)/60
                    except:
                        continue
                    mins_list = c.execute("SELECT mins FROM BoxScoreTraditional WHERE Player_ID = ?", (box_score[3],)).fetchall()
                    
                    time_list = []
                    for game_min in mins_list:
                        try:
                            g_mins, g_sec = game_min[0].split(":")
                            g_time = int(g_mins) + float(g_sec)/60
                            time_list.append(g_time)
                        except:
                            continue
                    data = np.array(g_time)

                    position = c.execute("SELECT Main_Position FROM PlayerProfiles WHERE Player_ID = ?", (box_score[3],)).fetchone()
                    try:
                        team_totals[position[0]]["rebT"] += box_score[1]
                        team_totals[position[0]]["pts"] += box_score[2]
                    except:
                        continue

                    if (time > np.percentile(data, 25) and np.average(data) >= 6):
                        
                        avg_points, avg_reb = c.execute("SELECT AV_PTS, AV_REB FROM PlayerSeason WHERE Player_ID = ?", (box_score[3],)).fetchone()
                        if avg_points ==None:
                            avg_points = 0
                            avg_reb = 0
                        team_totals[position[0]]["pts_diff"] += box_score[2] - avg_points
                        team_totals[position[0]]["reb_diff"] += box_score[1] - avg_reb 
                else:
                    continue

        for position, value in team_totals.items():
            team_totals[position]["avg_pts_diff"] = value.get("pts_diff") / games_num
            team_totals[position]["avg_pts"] = value.get("pts") / games_num
            team_totals[position]["avg_reb_diff"] = value.get("reb_diff") / games_num
            team_totals[position]["avg_reb"] = value.get("rebT") / games_num
        

        c.execute(""" INSERT INTO PositionStatsDef 
                  (TeamID, pts_diff_C, avg_pts_C, rebs_diff_C, avg_rebs_C, pts_diff_SF, avg_pts_SF, rebs_diff_SF, avg_rebs_SF,
                  pts_diff_PF, avg_pts_PF, rebs_diff_PF, avg_rebs_PF, pts_diff_SG, avg_pts_SG, rebs_diff_SG, avg_rebs_SG, pts_diff_PG, avg_pts_PG, rebs_diff_PG, avg_rebs_PG)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                  (team[0], team_totals.get("C").get("avg_pts_diff"), team_totals.get("C").get("avg_pts"), team_totals.get("C").get("avg_reb_diff"), team_totals.get("C").get("avg_reb"),
                   team_totals.get("SF").get("avg_pts_diff"), team_totals.get("SF").get("avg_pts"), team_totals.get("SF").get("avg_reb_diff"), team_totals.get("SF").get("avg_reb"),
                   team_totals.get("PF").get("avg_pts_diff"), team_totals.get("PF").get("avg_pts"), team_totals.get("PF").get("avg_reb_diff"), team_totals.get("PF").get("avg_reb"),
                   team_totals.get("SG").get("avg_pts_diff"), team_totals.get("SG").get("avg_pts"), team_totals.get("SG").get("avg_reb_diff"), team_totals.get("SG").get("avg_reb"),
                   team_totals.get("PG").get("avg_pts_diff"), team_totals.get("PG").get("avg_pts"), team_totals.get("PG").get("avg_reb_diff"), team_totals.get("PG").get("avg_reb")))
        
    conn.commit()
    conn.close()