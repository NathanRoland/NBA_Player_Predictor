import os
import sqlite3
from nba_api.stats.endpoints import boxscoreusagev3, boxscoretraditionalv3, boxscorescoringv3, boxscoreadvancedv3, boxscoremiscv3, boxscoreplayertrackv3

def box_score_usage():
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS BoxScoreUsage")
    table = """ CREATE TABLE BoxScoreUsage (
                Player_ID VARCHAR(255) NOT NULL,
                gameID CHAR(25) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                minutes REAL,
                usage_per REAL,
                fgm_per REAL,
                fga_per REAL,
                fg3m_per REAL,
                fg3a_per REAL,
                rebO_per REAL,
                rebD_per REAL,
                rebT_per REAL,
                ast_per REAL,
                pts_per REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID),
                FOREIGN KEY (gameID) REFERENCES Fixtures(gameID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
            ); """
    c.execute(table)

    games = c.execute("SELECT gameID, gameDate FROM Fixtures").fetchall()
    for game in games:
        try:
            players = vars(boxscoreusagev3.BoxScoreUsageV3(game_id=game[0]).player_stats).get("data").get("data")
            for player in players:
                mins = player[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreUsage (Player_ID, gameID, TeamID, minutes, usage_per, fgm_per, fga_per, fg3m_per, fg3a_per, rebO_per, rebD_per, rebT_per, ast_per, pts_per)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, 
                          (player[6], player[0], player[1], mins, player[15], player[16], player[17], player[18], player[19], player[22], player[23], player[24], player[25], player[32]))
        except:
            print("Error" , game[1])
            continue
    conn.commit()
    conn.close()

def box_score_traditional():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS BoxScoreTraditional")
    table = """ CREATE TABLE BoxScoreTraditional (
                Player_ID VARCHAR(255) NOT NULL,
                gameID CHAR(25) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                mins REAL,
                fgm INTEGER,
                fga INTEGER,
                fg_pct REAL,
                fg3m INTEGER,
                fg3a INTEGER,
                fg3_pct REAL,
                rebO INTEGER,
                rebD INTEGER,
                rebT INTEGER,
                ast REAL,
                pts REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID),
                FOREIGN KEY (gameID) REFERENCES Fixtures(gameID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                ); """
    c.execute(table)
    games = c.execute("SELECT gameID, gameDate FROM Fixtures").fetchall()
    for game in games:
        try:
            game_box_scores = vars(boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game[0]).player_stats).get("data").get("data")
            for box_score in game_box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreTraditional (Player_ID, gameID, TeamID, mins, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, rebO, rebD, rebT, ast, pts)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          (box_score[6], box_score[0], box_score[1], mins, box_score[15], box_score[16], box_score[17], box_score[18], box_score[19], box_score[20],
                          box_score[24], box_score[25], box_score[26], box_score[27], box_score[32]))
        except:
            print("Error", game[1])
            continue
    conn.commit()
    conn.close()

def box_score_scoring():
    file_path = os.path.join('database', "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS BoxScoreScoring")
    table = """ CREATE TABLE BoxScoreScoring (
                Player_ID VARCHAR(255) NOT NULL,
                gameID CHAR(25) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                mins REAL,
                pct_fg2a REAL,
                pct_fg3a REAL,
                pct_fg2_pts REAL,
                pct_mid_fg2_pts REAL,
                pct_fg3_pts REAL,
                pct_pts_fb REAL,
                pct_pts_turn REAL,
                pct_pts_paint REAL,
                pct_fg2_pts_ast REAL,
                pct_fg2_pts_unast REAL,
                pct_fg3_pts_ast REAL,
                pct_fg3_pts_unast REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID),
                FOREIGN KEY (gameID) REFERENCES Fixtures(gameID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                ); """
    c.execute(table)
    games = c.execute("SELECT gameID, gameDate FROM FIXTURES").fetchall()
    for game in games:
        try:
            box_scores = vars(boxscorescoringv3.BoxScoreScoringV3(game_id=game[0]).player_stats).get("data").get('data')
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreScoring (Player_ID, gameID, TeamID, mins, pct_fg2a, pct_fg3a, pct_fg2_pts, pct_mid_fg2_pts, pct_fg3_pts, 
                                pct_pts_fb, pct_pts_turn, pct_pts_paint, pct_fg2_pts_ast, pct_fg2_pts_unast, pct_fg3_pts_ast, pct_fg3_pts_unast)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[15], box_score[16], box_score[17], box_score[18], box_score[19],
                                    box_score[20], box_score[22], box_score[23], box_score[24], box_score[25], box_score[26], box_score[27]))
        except:
            print("Error", game[1])
            continue
    conn.commit()
    conn.close()

def box_scoring_advanced():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS BoxScoringAdvanced")
    table = """ CREATE TABLE BoxScoringAdvanced (
                Player_ID VARCHAR(255) NOT NULL,
                gameID CHAR(25) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                mins REAL,
                ast_pct REAL,
                off_reb_pct REAL,
                def_reb_pct REAL,
                reb_pct REAL,
                efg_pct REAL,
                usg_pct REAL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID),
                FOREIGN KEY (gameID) REFERENCES Fixtures(gameID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                ); """
    c.execute(table)
    games = c.execute("SELECT gameID, gameDate FROM Fixtures").fetchall()
    for game in games:
        try:
            box_scores = vars(boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=game[0]).player_stats).get("data").get("data")
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoringAdvanced (Player_ID, gameID, TeamID, mins, ast_pct, off_reb_pct, def_reb_pct, reb_pct, efg_pct, usg_pct)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[21], box_score[24], box_score[25], box_score[26], box_score[28], box_score[30]))
        except:
            print("error:", game[1])

    conn.commit()
    conn.close()

def box_score_misc():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS BoxScoreMisc")
    table = """ CREATE TABLE BoxScoreMisc (
                Player_ID VARCHAR(255) NOT NULL,
                gameID CHAR(25) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                mins REAL,
                pts_to INTEGER,
                pts_sec INTEGER,
                pts_fbk INTEGER,
                pts_pnt INTEGER,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID),
                FOREIGN KEY (gameID) REFERENCES Fixtures(gameID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                );"""
    c.execute(table)
    games = c.execute("SELECT gameID, gameDate FROM Fixtures").fetchall()
    for game in games:
        try:
            box_scores = vars(boxscoremiscv3.BoxScoreMiscV3(game_id=game[0]).player_stats).get("data").get("data")
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreMisc (Player_ID, gameID, TeamID, mins, pts_to, pts_sec, pts_fbk, pts_pnt)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?) """, 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[15], box_score[16], box_score[17], box_score[18]))
        except:
            print("error:", game[1])
    conn.commit()
    conn.close()

def box_score_player_track():
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS BoxScoreTrack")
    table = """ CREATE TABLE BoxScoreTrack (
                Player_ID VARCHAR(255) NOT NULL,
                gameID CHAR(25) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                mins REAL,
                reb_C_Off INTEGER,
                reb_C_Def INTEGER,
                reb_C_Tot INTEGER,
                passes INTEGER,
                assists INTEGER,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID),
                FOREIGN KEY (gameID) REFERENCES Fixtures(gameID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
                );"""
    c.execute(table)
    games = c.execute("SELECT gameID, gameDate FROM Fixtures").fetchall()
    for game in games:
        try:
            box_scores = vars(boxscoreplayertrackv3.BoxScorePlayerTrackV3(game_id=game[0]).player_stats).get("data").get("data")
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreTrack (Player_ID, gameID, TeamID, mins, reb_C_Off, reb_C_Def, reb_C_Tot, passes, assists)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[17], box_score[18], box_score[19], box_score[23], box_score[24]))
        except:
            print("Error: ", game[1])

    conn.commit()
    conn.close()

def updateBoxScores():
    #fix this there is an errorrrrrrr
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    games = c.execute("SELECT gameID from Fixtures ORDER BY gameDate DESC").fetchall()
    recorded_games = c.execute("SELECT DISTINCT gameID from BoxScoreScoring").fetchall()
    recorded_games_list = [row[0] for row in recorded_games]
    games_list = [row[0] for row in games]
    unrecorded_games = [x for x in games_list if x not in recorded_games_list][::-1]
   #print(unrecorded_games)
    for game in unrecorded_games:
        try:
            box_scores = vars(boxscoreplayertrackv3.BoxScorePlayerTrackV3(game_id=game).player_stats).get("data").get("data")
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreTrack (Player_ID, gameID, TeamID, mins, reb_C_Off, reb_C_Def, reb_C_Tot, passes, assists)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[17], box_score[18], box_score[19], box_score[23], box_score[24]))
            
            box_scores = vars(boxscoremiscv3.BoxScoreMiscV3(game_id=game).player_stats).get("data").get("data")
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreMisc (Player_ID, gameID, TeamID, mins, pts_to, pts_sec, pts_fbk, pts_pnt)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?) """, 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[15], box_score[16], box_score[17], box_score[18]))

            box_scores = vars(boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=game).player_stats).get("data").get("data")
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoringAdvanced (Player_ID, gameID, TeamID, mins, ast_pct, off_reb_pct, def_reb_pct, reb_pct, efg_pct, usg_pct)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[21], box_score[24], box_score[25], box_score[26], box_score[28], box_score[30]))

            box_scores = vars(boxscorescoringv3.BoxScoreScoringV3(game_id=game[0]).player_stats).get("data").get('data')
            for box_score in box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreScoring (Player_ID, gameID, TeamID, mins, pct_fg2a, pct_fg3a, pct_fg2_pts, pct_mid_fg2_pts, pct_fg3_pts, 
                                pct_pts_fb, pct_pts_turn, pct_pts_paint, pct_fg2_pts_ast, pct_fg2_pts_unast, pct_fg3_pts_ast, pct_fg3_pts_unast)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                (box_score[6], box_score[0], box_score[1], mins, box_score[15], box_score[16], box_score[17], box_score[18], box_score[19],
                                    box_score[20], box_score[22], box_score[23], box_score[24], box_score[25], box_score[26], box_score[27]))
                
            game_box_scores = vars(boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game).player_stats).get("data").get("data")
            for box_score in game_box_scores:
                mins = box_score[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreTraditional (Player_ID, gameID, TeamID, mins, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, rebO, rebD, rebT, ast, pts)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          (box_score[6], box_score[0], box_score[1], mins, box_score[15], box_score[16], box_score[17], box_score[18], box_score[19], box_score[20],
                          box_score[24], box_score[25], box_score[26], box_score[27], box_score[32]))
                
            players = vars(boxscoreusagev3.BoxScoreUsageV3(game_id=game).player_stats).get("data").get("data")
            for player in players:
                mins = player[14]
                if len(mins) <= 0:
                    mins= 0
                c.execute(""" INSERT INTO BoxScoreUsage (Player_ID, gameID, TeamID, minutes, usage_per, fgm_per, fga_per, fg3m_per, fg3a_per, rebO_per, rebD_per, rebT_per, ast_per, pts_per)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, 
                          (player[6], player[0], player[1], mins, player[15], player[16], player[17], player[18], player[19], player[22], player[23], player[24], player[25], player[32]))
        except:
            print(game)
            break

    conn.commit()
    conn.close()
