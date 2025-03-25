import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import os
import sqlite3


#predict for each player

def get_opponent(TeamID, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    opp_game_id = None
    games = c.execute(""" SELECT homeTeamID, awayTeamID FROM Fixtures WHERE gameID = ?""", (gameID,)).fetchall()[0]
    if games[0] == TeamID:
        opp_game_id = games[1]
    if games[1] == TeamID:
        opp_game_id = games[0]
    conn.commit()
    conn.close()
    return opp_game_id

def get_points_curve(playerID, player_mins, teamMates, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    
    #variables: mins, three points shot, two points shot, points to, points sec, points fbk, points paint, 
    #points is target

    #variables Box Score for 2 pointers:
    #BoxScoreMisc: pts_to, pts_sec, pts_fbk, pts_paint
    #BoxScoreScoring: pct_fg2_pts, pct_pts_paint, pct_pts_turn, pct_pts_fb
    #BoxScoreTraditional: fgm, fga, fg3a, fg3m, (deduce new fg% and pts from that)
    #BoxScoreUsage: usage_per, fgm_per, fga_per, pts_per

    #TeamStats: 
    #PositionStats: pts_diff_C, avg_pts_C, pts_diff_SF, avg_pts_SF, pts_diff_PF, avg_pts_PF, pts_diff_SG, avg_pts_SG, pts_diff_PG, avg_pts_PG
    #PlayerShotAreas: all but include where clause(restricted area, paint, midrange)
    #OppShots: FG2M, FG2A, FG2_PCT
    #TeamDefenseRankings
    #TeamShotLocation
    three_pointers = predict_three_points(playerID, player_mins, teamMates, gameID)
    two_pointers = predict_two_points(playerID, player_mins, teamMates, gameID)
    fts = predict_free_throws(playerID, player_mins, teamMates, gameID)
    total_points = three_pointers * 3 + two_pointers * 2 + fts

    #print(total_points)
    conn.commit()
    conn.close()
    return total_points

def predict_two_points(playerID, player_mins, teamMates, gameID):
    fg2a = two_point_attempts(playerID, player_mins, teamMates, gameID)
    fg2_pct = predict_two_point_pct(playerID, gameID, fg2a)
    #print(fg2a * fg2_pct)
    return fg2a * fg2_pct

def two_point_attempts(playerID, player_mins, teamMates, gameID):
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    
    fg2a_y = []
    fg2a_x = []
    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    box_scores = c.execute("""SELECT BoxScoreMisc.gameID, minutes, pts_pnt,
                           pct_fg2a, pct_fg2_pts, pct_pts_paint,
                           fga, fg3a, usage_per, fgm_per, fga_per, pts_per FROM BoxScoreMisc 
                           INNER JOIN BoxScoreScoring ON (BoxScoreMisc.Player_ID = BoxScoreScoring.Player_ID AND BoxScoreMisc.gameID = BoxScoreScoring.gameID)
                           INNER JOIN BoxScoreTraditional ON (BoxScoreMisc.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreMisc.gameID = BoxScoreTraditional.gameID)
                           INNER JOIN BoxScoreUsage ON (BoxScoreMisc.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreMisc.gameID = BoxScoreUsage.gameID)
                           WHERE BoxScoreMisc.Player_id = ?""", (playerID,)).fetchall()
    
    for box_score in box_scores:
        try:
            mins, sec = box_score[1].split(":")
            time = int(mins) + float(sec)/60
            opp_team = get_opponent(TeamID[0], box_score[0])
            opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.F2GM, OppShots.F2GA, OppShots.F2G_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                    INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShots.TeamID = ?""", (opp_team,)).fetchall()[0]
            fg2a_box_score = box_score[6] - box_score[7]
            fg2a_x.append([time, box_score[3], box_score[4], box_score[8], box_score[9], box_score[10], box_score[11], opposing_team_stats[2]/opposing_team_stats[4]])
            fg2a_y.append(fg2a_box_score)
        except:
            continue
        
    pct_fg2a, pct_fg2_pts, usage_per, fga_per, fgm_per, pts_per = predict_two_point_variables(playerID, player_mins, teamMates, gameID)
    opp_team = get_opponent(TeamID[0], gameID)
    opposing_team_stats_l5 = c.execute("""SELECT OppShotsL5.TeamID, OppShotsL5.F2GM, OppShotsL5.F2GA, OppShotsL5.F2G_PCT, COUNT(DISTINCT gameID) FROM OppShotsL5 
                            INNER JOIN BoxScoreTraditional ON (OppShotsL5.TeamID = BoxScoreTraditional.TeamID)
                            WHERE OppShotsL5.TeamID = ?""", (opp_team,)).fetchall()[0]
    #predictions
    X_train, X_test, y_train, y_test = train_test_split(fg2a_x, fg2a_y, test_size=0.1, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    fg2a = mlr_model.predict([[player_mins, pct_fg2a[0], pct_fg2_pts[0], usage_per[0], fga_per[0], fgm_per[0], pts_per[0], opposing_team_stats_l5[2]/5]])
    #print(fg2a)
    conn.commit()
    conn.close()
    return fg2a[0]

def predict_two_point_variables(playerID, minutes, teamMates, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()

    pct_fg2a_x = []
    pct_fg2a_y = []
    pct_fg2_pts_x = []
    pct_fg2_pts_y = []
    usage_per_x= []
    usage_per_y = []
    fgm_per_x = []
    fgm_per_y = []
    fga_per_x = []
    fga_per_y = []
    pts_per_x = []
    pts_per_y = []

    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    players = c.execute(""" SELECT Player_ID FROM PlayerProfiles WHERE TeamID = ?""", (TeamID[0],)).fetchall()
    players = [str(player[0]) for player in players]
    for player in players:
            if player not in teamMates.keys():
                teamMates[player] = 0.0
    teamMates = sorted(teamMates.items())
    teamMates_list = [float(tuple[1]) for tuple in teamMates]

    games = c.execute(""" SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ?""", (TeamID[0], TeamID[0],)).fetchall()
    for game in games:
            opp_team = get_opponent(TeamID[0], game[0])
            opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.FG3M, OppShots.FG3A, OppShots.F2GA, OppShots.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                        INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                        WHERE OppShots.TeamID = ?""", (opp_team,)).fetchall()[0]
            if opposing_team_stats[0] is None:
                continue
            game_data = {}
            pct_fg2a_x_row = []
            pct_fg2_pts_x_row =[]
            fgm_per_x_row = []
            fga_per_x_row = []
            pts_per_x_row = []
            try:
                data_unfiltered_player = c.execute("""SELECT BoxScoreMisc.mins, pct_fg2a, pct_fg2_pts, usage_per, fgm_per, fga_per, pts_per FROM BoxScoreMisc 
                            INNER JOIN BoxScoreScoring ON (BoxScoreMisc.Player_ID = BoxScoreScoring.Player_ID AND BoxScoreMisc.gameID = BoxScoreScoring.gameID)
                            INNER JOIN BoxScoreTraditional ON (BoxScoreMisc.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreMisc.gameID = BoxScoreTraditional.gameID)
                            INNER JOIN BoxScoreUsage ON (BoxScoreMisc.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreMisc.gameID = BoxScoreUsage.gameID)
                            WHERE BoxScoreMisc.Player_ID = ? AND BoxScoreMisc.gameID = ?""", (playerID, game[0],)).fetchall()[0]
                mins, sec = data_unfiltered_player[0].split(":")
                time = int(mins) + float(sec)/60
                if time != 0.0:
                    pct_fg2a_y.append(data_unfiltered_player[1])
                    pct_fg2_pts_y.append(data_unfiltered_player[2])
                    usage_per_y.append(data_unfiltered_player[3])
                    fgm_per_y.append(data_unfiltered_player[4])
                    fga_per_y.append(data_unfiltered_player[5])
                    pts_per_y.append(data_unfiltered_player[6])
                    game_data[str(playerID)] = time
                    fga_per_x_row.append(time)
                    fga_per_x_row.append(data_unfiltered_player[3])
                    pct_fg2a_x_row.append(time)
                    pct_fg2_pts_x_row.append(data_unfiltered_player[1])
                    fgm_per_x_row.append(data_unfiltered_player[5])
                    pts_per_x_row.append(data_unfiltered_player[2])
                    pts_per_x_row.append(data_unfiltered_player[4])
                else:
                    continue
            except:
                continue
    
            data_unfiltered = c.execute(""" SELECT mins, Player_ID from BoxScoreTraditional WHERE gameID = ? AND TeamID = ? AND Player_ID != ?""",
                                    (game[0], TeamID[0], playerID)).fetchall()
            for row in data_unfiltered:
                try:
                    if row[1] in players:
                        mins, sec = row[0].split(":")
                        time = int(mins) + float(sec)/60
                        game_data[str(row[1])] = time
                except:
                    continue
            for player in players:
                if player not in game_data.keys():
                    game_data[player] = 0.0
            
            game_data = sorted(game_data.items())
            game_data_list = [tuple[1] for tuple in game_data]
            fga_per_x_row.append(opposing_team_stats[2]/opposing_team_stats[-1])
            fga_per_x.append(fga_per_x_row)
            pct_fg2a_x_row.append(opposing_team_stats[2]/opposing_team_stats[-1])
            pct_fg2a_x_row.append(opposing_team_stats[3]/opposing_team_stats[-1])
            pct_fg2a_x.append(pct_fg2a_x_row)
            pct_fg2_pts_x_row.append(opposing_team_stats[1]/opposing_team_stats[-1])
            pct_fg2_pts_x.append(pct_fg2_pts_x_row)
            fgm_per_x_row.append(opposing_team_stats[1]/opposing_team_stats[-1])
            fgm_per_x_row.append(opposing_team_stats[-2])
            fgm_per_x.append(fgm_per_x_row)
            pts_per_x.append(pts_per_x_row)
            usage_per_x.append(game_data_list)

    opp_team = get_opponent(TeamID[0], gameID)
    opposing_team_stats_l5 = c.execute("""SELECT OppShotsL5.TeamID, OppShotsL5.FG3M, OppShotsL5.FG3A, OppShotsL5.F2GA, OppShotsL5.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShotsL5 
                                INNER JOIN BoxScoreTraditional ON (OppShotsL5.TeamID = BoxScoreTraditional.TeamID)
                                WHERE OppShotsL5.TeamID = ?""", (opp_team,)).fetchall()[0]

    #print("pctfg2a")
    pred_pctfg2a_x = [[minutes, opposing_team_stats_l5[2]/5, opposing_team_stats_l5[3]/5]]
    X_train, X_test, y_train, y_test = train_test_split(pct_fg2a_x, pct_fg2a_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pct_fg2a = mlr_model.predict(pred_pctfg2a_x)
    #print(pct_fg2a)

    #print("pct_fg2_pts")
    pred_pct_fg2_pts_x = [[pct_fg2a[0], opposing_team_stats_l5[1]/5]]
    X_train, X_test, y_train, y_test = train_test_split(pct_fg2_pts_x, pct_fg2_pts_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pct_fg2_pts = mlr_model.predict(pred_pct_fg2_pts_x)
    #print(pct_fg2_pts)

    #print("usage_per")
    pred_usage_per_x = [teamMates_list]
    X_train, X_test, y_train, y_test = train_test_split(usage_per_x, usage_per_y, test_size=0.1, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    usage_per = mlr_model.predict(pred_usage_per_x)
    #print(usage_per)

    #print("fga_per_x")
    pred_fga_per_x = [[minutes, usage_per[0], opposing_team_stats_l5[2]/5]]
    X_train, X_test, y_train, y_test = train_test_split(fga_per_x, fga_per_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    fga_per = mlr_model.predict(pred_fga_per_x)
    #print(fga_per)

    #print("fgm_per_x")
    pred_fgm_per_x = [[fga_per[0], opposing_team_stats_l5[1]/5, opposing_team_stats_l5[-2]]]
    X_train, X_test, y_train, y_test = train_test_split(fgm_per_x, fgm_per_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    fgm_per = mlr_model.predict(pred_fgm_per_x)
    #print(fgm_per)

    #print("pts_per_x")
    pred_pts_per_x = [[pct_fg2_pts[0], fgm_per[0]]]
    X_train, X_test, y_train, y_test = train_test_split(pts_per_x, pts_per_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pts_per = mlr_model.predict(pred_pts_per_x)
    #print(pts_per)

    conn.commit()
    conn.close()
    return pct_fg2a, pct_fg2_pts, usage_per, fga_per, fgm_per, pts_per

def predict_two_point_pct(playerID, gameID, fga):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    box_scores = c.execute(""" SELECT fgm, fga, fg3m, fg3a, gameID FROM BoxScoreTraditional WHERE Player_ID = ?""", (playerID,)).fetchall()
    fg2_pct_scores = []
    fg2_pct_x_data = []
    for box_score in box_scores:
        try:
            opp_team = get_opponent(TeamID[0], box_score[4])
            opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.F2GM, OppShots.F2GA, OppShots.F2G_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                    INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShots.TeamID = ?""", (opp_team,)).fetchall()[0]
            if opposing_team_stats[0] is None:
                continue
            fg2a_test = box_score[1] - box_score[3]
            fg2m = box_score[0] - box_score[2]
            if fg2a_test == 0:
                fg2_pct = 0
            else:
                fg2_pct = fg2m/fg2a_test
            fg2_pct_x_data.append([fg2a_test, opposing_team_stats[3]])
            fg2_pct_scores.append(fg2_pct)
        except:
            continue
    
    X_train, X_test, y_train, y_test = train_test_split(fg2_pct_x_data, fg2_pct_scores, test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    y_pred=mlr_model.predict(X_test)
    #print("fg2a")
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    
    opp_team_l5 = get_opponent(TeamID[0], gameID)
    opposing_team_stats_L5 = c.execute("""SELECT OppShotsL5.TeamID, OppShotsL5.F2GM, OppShotsL5.F2GA, OppShotsL5.F2G_PCT, COUNT(DISTINCT gameID) FROM OppShotsL5 
                                    INNER JOIN BoxScoreTraditional ON (OppShotsL5.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShotsL5.TeamID = ?""", (opp_team_l5,)).fetchall()[0]
    fg2_pct = mlr_model.predict([[fga, opposing_team_stats_L5[3]]])
    conn.commit()
    conn.close()
    return fg2_pct[0]

def predict_free_throws(playerID, player_mins, teamMates, gameID):
    file_path = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    fts_y = []
    usage_y = []
    fts_x = []
    usage_x = []

    #usage:
    teamID = c.execute(""" SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchone()
    players = c.execute(""" SELECT Player_ID FROM PlayerProfiles WHERE TeamID = ?""", (teamID[0],)).fetchall()
    players = [str(player[0]) for player in players]
    for player in players:
            if player not in teamMates.keys():
                teamMates[player] = 0.0
    teamMates = sorted(teamMates.items())
    teamMates_list = [float(tuple[1]) for tuple in teamMates]
    games = c.execute(""" SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ?""", (teamID[0], teamID[0],)).fetchall()
    for game in games:
        game_data = {}
        try:
            data_unfiltered_player = c.execute(""" SELECT BoxScoreScoring.mins, usage_per FROM BoxScoreScoring 
                           INNER JOIN BoxScoreUsage ON (BoxScoreScoring.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreScoring.gameID = BoxScoreUsage.gameID)
                           WHERE BoxScoreScoring.Player_ID = ? AND BoxScoreScoring.gameID = ? """, (playerID, game[0],)).fetchall()[0]
            mins, sec = data_unfiltered_player[0].split(":")
            time = int(mins) + float(sec)/60
            if time != 0.0:
                game_data[str(playerID)] = time
                usage_y.append(data_unfiltered_player[1])
            else:
                continue
        except:
            continue
        data_unfiltered = c.execute(""" SELECT mins, Player_ID from BoxScoreTraditional WHERE gameID = ? AND TeamID = ? AND Player_ID != ?""",
                                    (game[0], teamID[0], playerID)).fetchall()
        for row in data_unfiltered:
            try:
                if row[1] in players:
                    mins, sec = row[0].split(":")
                    time = int(mins) + float(sec)/60
                    game_data[str(row[1])] = time
            except:
                continue
        for player in players:
            if player not in game_data.keys():
                game_data[player] = 0.0
        game_data = sorted(game_data.items())
        game_data_list = [tuple[1] for tuple in game_data]
        usage_x.append(game_data_list)

    X_train, X_test, y_train, y_test = train_test_split(usage_x, usage_y, test_size=0.1, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    usage_per = mlr_model.predict([teamMates_list])[0]
    #print(usage_per)
    
    #free throws
    box_scores= c.execute("""SELECT mins, usage_per, fgm, fga, fg3m, fg3a, pts FROM BoxScoreTraditional 
                          INNER JOIN BoxScoreUsage ON (BoxScoreTraditional.Player_ID = BoxScoreUsage.Player_ID) 
                          WHERE BoxScoreTraditional.Player_ID = ?""", (playerID,)).fetchall()
    
    for boxscore in box_scores:
        try:
            mins, sec = boxscore[0].split(":")
            time = int(mins) + float(sec)/60
            if time != 0.0:
                fts_x_row = [time, boxscore[1]]
                fg2m = boxscore[2] - boxscore[4]
                
                ft = boxscore[6] - fg2m*2 - boxscore[4]*3
                fts_y.append(ft)
                fts_x.append(fts_x_row)
            else:
                continue
        except:
            continue
    
    X_train, X_test, y_train, y_test = train_test_split(fts_x, fts_y, test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    fts = mlr_model.predict([[player_mins, usage_per]])
    
    #print(fts)
    conn.commit()
    conn.close()
    return fts[0]

def predict_three_points(playerID, player_mins, teamMates, gameID):
    fg3a = new_three_point_attempts(playerID, player_mins, teamMates, gameID)
    fg3_pct = predict_three_point_pct(playerID, gameID, fg3a)
    fg3m = fg3a * fg3_pct
    #print(fg3m)
    #print(fg3m * 3)
    return fg3m

def predict_three_point_pct(playerID, gameID, fga):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    
    current_team_stats = c.execute("""SELECT TeamRankings.FG3M, TeamRankings.FG3A, TeamRankings.FG3_PCT, AB3_FGM, AB3_FGA, AB3_FGPCT, C3_FGM, C3_FGA, C3_FGPCT, COUNT(DISTINCT gameID) 
                                   FROM TeamRankings
                                   INNER JOIN BoxScoreTraditional ON (TeamRankings.TeamID = BoxScoreTraditional.TeamID)
                                   INNER JOIN TeamShotLocation ON (TeamRankings.TeamID = TeamShotLocation.TeamID) WHERE TeamRankings.TeamID = ?"""
                                   , (TeamID[0],)).fetchall()[0]
    box_scores = c.execute(""" SELECT fg3_pct, fg3a, gameID FROM BoxScoreTraditional WHERE Player_ID = ?""", (playerID,)).fetchall()
    
    fg3_pct_scores = []
    fg3_pct_x_data = []
    for box_score in box_scores:
        try:
            opp_team = get_opponent(TeamID[0], box_score[2])
            opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.FG3M, OppShots.FG3A, OppShots.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                    INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShots.TeamID = ?""", (opp_team,)).fetchall()[0]
            
            if opposing_team_stats[0] is None:
                continue
            fg3_pct_x_data.append([box_score[1], opposing_team_stats[3]])
            fg3_pct_scores.append(box_score[0])
        except:
            continue
    
    X_train, X_test, y_train, y_test = train_test_split(fg3_pct_x_data, fg3_pct_scores, test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)

    opp_team = get_opponent(TeamID[0], gameID)
    opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.FG3M, OppShots.FG3A, OppShots.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                    INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShots.TeamID = ?""", (opp_team,)).fetchall()[0]
    fg3_pct = mlr_model.predict([[fga, opposing_team_stats[3]]])
    conn.commit()
    conn.close()
    return fg3_pct[0]

def new_three_point_attempts(playerID, player_mins, teamMates, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    opp_team = get_opponent(TeamID[0], gameID)
    
    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    box_scores = c.execute(""" SELECT BoxScoreScoring.mins, pct_fg3a, pct_fg3_pts, fg3a, fg3m, fg3_pct, usage_per, fg3m_per, fg3a_per, BoxScoreScoring.gameID FROM BoxScoreScoring 
                           INNER JOIN BoxScoreTraditional ON (BoxScoreScoring.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreScoring.gameID = BoxScoreTraditional.gameID)
                           INNER JOIN BoxScoreUsage ON (BoxScoreScoring.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreScoring.gameID = BoxScoreUsage.gameID)
                           WHERE BoxScoreScoring.Player_ID = ?""", (playerID,)).fetchall()
    
    fg3a_data = []
    fg3m_data = []
    fg3a_x_data = []
    fg3_pct_data = []
    pct_fg3a, pct_fg3_pts, usage_per, fg3m_per, fg3a_per = pred_three_point_variables(playerID, teamMates, gameID, player_mins)
    for box_score in box_scores:
        try:
            mins, sec = box_score[0].split(":")
            time = int(mins) + float(sec)/60
            # opposing_team_stats[1]/opposing_team_stats[-1], opposing_team_stats[2]/opposing_team_stats[-1], opposing_team_stats[3],
            #                     current_team_stats[0]/current_team_stats[9], current_team_stats[1]/current_team_stats[9], current_team_stats[2],
            #                     current_team_stats[3]/current_team_stats[9], current_team_stats[4]/current_team_stats[9], current_team_stats[5],
            #                     current_team_stats[6]/current_team_stats[9], current_team_stats[7]/current_team_stats[9], current_team_stats[8]
            fg3a_x_data.append([time, box_score[1], box_score[2], box_score[6], box_score[7], box_score[8]])
            fg3m_data.append(box_score[4])
            fg3a_data.append(box_score[3])
            fg3_pct_data.append(box_score[5])
        except:
            continue
        
    X_train, X_test, y_train, y_test = train_test_split(fg3a_x_data, fg3a_data, test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)

    fg3a = mlr_model.predict([[player_mins, pct_fg3a[0], pct_fg3_pts[0], usage_per[0], fg3m_per[0], fg3a_per[0]]])
    #print(fg3a)
    conn.commit()
    conn.close()
    return fg3a[0]

def old_pred_three_pts(playerID, player_mins, teamMates, gameID):
    #Variables:
    #BoxScoreScoring: pct_fg3a, pct_fg3_pts, (pct_fg3_ast, pct_fg3_unast) (decide on last 2 ones)
    #BoxScoreTraditional: fg3a, fg3m, fg3_pct
    #BoxScoreUsage: usage_per, fg3m_per, fg3a_per
    #PlayerShotAreas: Shot_Area (LEFT-CORNER, RIGHT CORNER, ABOVE the break), FG3M, FG3A, FG3_PCT
    #PlayerShotTypes: SHOT_TYPE (Catch and shoot), FG3_FREQ, FG3M, FG3A, FG3_PCT    

    #Team Stats
    #OppShots; FG3M, FG3A, FG3_PCT
    #TeamRankings: FG3M, FG3A, FG3_PCT
    #TeamShotLocation: AB3_FGM, AB3_FGA, AB3_FGPCT, C3_FGM, C3_FGA, C3_FGPCT

    #use for predictions: opp shots l5, TEAM RANKINGS LAST 5
    #fg3a = pred_three_point_variables()
    #fg3_pct = pred_three_pt_pct()

    pct_fg3a, pct_fg3_pts, fg3_pct, usage_per, fg3m_per, fg3a_per = pred_three_point_variables(playerID, teamMates, gameID)
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    box_scores = c.execute(""" SELECT BoxScoreScoring.mins, pct_fg3a, pct_fg3_pts, fg3a, fg3m, fg3_pct, usage_per, fg3m_per, fg3a_per, BoxScoreScoring.gameID FROM BoxScoreScoring 
                           INNER JOIN BoxScoreTraditional ON (BoxScoreScoring.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreScoring.gameID = BoxScoreTraditional.gameID)
                           INNER JOIN BoxScoreUsage ON (BoxScoreScoring.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreScoring.gameID = BoxScoreUsage.gameID)
                           WHERE BoxScoreScoring.Player_ID = ?""", (playerID,)).fetchall()
    
    opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.FG3M, OppShots.FG3A, OppShots.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                    INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShots.TeamID != ?""", (TeamID[0],)).fetchall()


    current_team_stats = c.execute("""SELECT TeamRankings.FG3M, TeamRankings.FG3A, TeamRankings.FG3_PCT, AB3_FGM, AB3_FGA, AB3_FGPCT, C3_FGM, C3_FGA, C3_FGPCT, COUNT(DISTINCT gameID) 
                                   FROM TeamRankings
                                   INNER JOIN BoxScoreTraditional ON (TeamRankings.TeamID = BoxScoreTraditional.TeamID)
                                   INNER JOIN TeamShotLocation ON (TeamRankings.TeamID = TeamShotLocation.TeamID) WHERE TeamRankings.TeamID = ?"""
                                   , (TeamID[0],)).fetchall()[0]

    fg3a_data = []
    fg3m_data = []
    fg3a_x_data = []

    for box_score in box_scores:
        try:
            mins, sec = box_score[0].split(":")
            time = int(mins) + float(sec)/60
            opp_team = get_opponent(TeamID[0], box_score[9])
            opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.FG3M, OppShots.FG3A, OppShots.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                    INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShots.TeamID = ?""", (opp_team,)).fetchall()[0]
            # opposing_team_stats[1]/opposing_team_stats[-1], opposing_team_stats[2]/opposing_team_stats[-1], opposing_team_stats[3],
            #                     current_team_stats[0]/current_team_stats[9], current_team_stats[1]/current_team_stats[9], current_team_stats[2],
            #                     current_team_stats[3]/current_team_stats[9], current_team_stats[4]/current_team_stats[9], current_team_stats[5],
            #                     current_team_stats[6]/current_team_stats[9], current_team_stats[7]/current_team_stats[9], current_team_stats[8]
            fg3a_x_data.append([time, box_score[1], box_score[2], box_score[5], box_score[6], box_score[7], box_score[8]])
            fg3m_data.append(box_score[4])
            fg3a_data.append(box_score[3])
        except:
            continue
    
    
    
    #print(fg3a_x_data)
    #print(fg3a_data)
    #print(fg3m_data)
    X_train, X_test, y_train, y_test = train_test_split(fg3a_x_data, fg3a_data, test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)

    opp_team = get_opponent(TeamID[0], box_score[9])
    opposing_team_stats_l5 = c.execute("""SELECT OppShotsL5.TeamID, OppShotsL5.FG3M, OppShotsL5.FG3A, OppShotsL5.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShotsL5 
                            INNER JOIN BoxScoreTraditional ON (OppShotsL5.TeamID = BoxScoreTraditional.TeamID)
                            WHERE OppShotsL5.TeamID = ?""", (opp_team,)).fetchall()[0]
    
    current_team_stats_l5 = c.execute("""SELECT TeamRankingsL5.FG3M, TeamRankingsL5.FG3A, TeamRankingsL5.FG3_PCT, AB3_FGM, AB3_FGA, AB3_FGPCT, C3_FGM, C3_FGA, C3_FGPCT, COUNT(DISTINCT gameID) 
                                   FROM TeamRankingsL5
                                   INNER JOIN BoxScoreTraditional ON (TeamRankingsL5.TeamID = BoxScoreTraditional.TeamID)
                                   INNER JOIN TeamShotLocationL5 ON (TeamRankingsL5.TeamID = TeamShotLocationL5.TeamID) WHERE TeamRankingsL5.TeamID = ?"""
                                   , (TeamID[0],)).fetchall()[0]

    fg3a = mlr_model.predict([[player_mins, pct_fg3a[0], pct_fg3_pts[0], fg3_pct[0], usage_per[0], fg3m_per[0], fg3a_per[0],
                            opposing_team_stats_l5[1]/5, opposing_team_stats_l5[2]/5, opposing_team_stats_l5[3],
                            current_team_stats_l5[0]/5, current_team_stats_l5[1]/5, current_team_stats_l5[2],
                            current_team_stats_l5[3]/5, current_team_stats_l5[4]/5, current_team_stats_l5[5],
                            current_team_stats_l5[6]/5, current_team_stats_l5[7]/5, current_team_stats_l5[8]]])
    #print([[player_mins, pct_fg3a[0], pct_fg3_pts[0], fg3_pct[0], usage_per[0], fg3m_per[0], fg3a_per[0],
     #                       opposing_team_stats_l5[1]/5, opposing_team_stats_l5[2]/5, opposing_team_stats_l5[3],
      #                      current_team_stats_l5[0]/5, current_team_stats_l5[1]/5, current_team_stats_l5[2],
       #                     current_team_stats_l5[3]/5, current_team_stats_l5[4]/5, current_team_stats_l5[5],
        #                    current_team_stats_l5[6]/5, current_team_stats_l5[7]/5, current_team_stats_l5[8]]])
    fg3m = fg3a * fg3_pct
    fg3_pts = fg3m * 3
    #print(fg3a)
    #print(fg3m)
    #print(fg3_pct)
    #print(fg3_pts)
    return fg3m, fg3_pts

def pred_three_point_variables(playerID, teamMates, gameID, player_mins_pred):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()  

    TeamID = c.execute("SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?", (playerID,)).fetchall()[0]
    #player_analytics = c.execute(""" SELECT FG3M, FG3A, FG3_PCT FROM PlayerShotAreas WHERE Shot_Area = 'Left Corner 3' OR Shot_Area = 'Right Corner 3' OR Shot_Area = 'Above the Break 3'""").fetchall()
    #player_shot_types = c.execute("SELECT F3_FREQ, FG3M, FG3A, FG3_PCT").fetchall()
    
    players = c.execute(""" SELECT Player_ID FROM PlayerProfiles WHERE TeamID = ?""", (TeamID[0],)).fetchall()
    players = [str(player[0]) for player in players]

    for player in players:
            if player not in teamMates.keys():
                teamMates[player] = 0.0

    teamMates = sorted(teamMates.items())
    #print(teamMates)
    teamMates_list = [float(tuple[1]) for tuple in teamMates]

    games = c.execute(""" SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ?""", (TeamID[0], TeamID[0],)).fetchall()

    pct_fg3a_y = [] 
    pct_fg3_pts_y = []
    fg3_pct_y = [] 
    usage_per_y = [] 
    fg3m_per_y = []
    fg3a_per_y = []
    x_data = []
    fg3a_x_data = []
    fg3_pct_x = []
    pct_fg3a_x_data = []
    pct_fg3m_x_data = []
    usage_x_data = []
    fg3m_per_x_data = []
    #print(playerID)
    for game in games:
        opp_team = get_opponent(TeamID[0], game[0])
        opposing_team_stats = c.execute("""SELECT OppShots.TeamID, OppShots.FG3M, OppShots.FG3A, OppShots.F2GA, OppShots.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShots 
                                    INNER JOIN BoxScoreTraditional ON (OppShots.TeamID = BoxScoreTraditional.TeamID)
                                    WHERE OppShots.TeamID = ?""", (opp_team,)).fetchall()[0]
        if opposing_team_stats[0] is None:
            continue
        
        game_data = {}
        fg_pct_x_row = []
        fg3_pct_x_row =[]
        pct_fg3a_x_data_row = []
        pct_fg3m_x_data_row = []
        fg3m_per_x_data_row = []
        try:
            #print(game[0])
            data_unfiltered_player = c.execute(""" SELECT BoxScoreScoring.mins, pct_fg3a, pct_fg3_pts, BoxScoreTraditional.fg3_pct, usage_per, fg3m_per, fg3a_per FROM BoxScoreScoring 
                            INNER JOIN BoxScoreTraditional ON (BoxScoreScoring.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreScoring.gameID = BoxScoreTraditional.gameID)
                            INNER JOIN BoxScoreUsage ON (BoxScoreScoring.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreScoring.gameID = BoxScoreUsage.gameID)
                            WHERE BoxScoreScoring.Player_ID = ? AND BoxScoreScoring.gameID = ? """, (playerID, str(game[0]),)).fetchall()[0]
            #print(data_unfiltered_player)
            mins, sec = data_unfiltered_player[0].split(":")
            time = int(mins) + float(sec)/60
            #print(time)
            if time != 0.0:
                pct_fg3a_y.append(data_unfiltered_player[1])
                pct_fg3_pts_y.append(data_unfiltered_player[2])
                fg3_pct_y.append(data_unfiltered_player[3])
                usage_per_y.append(data_unfiltered_player[4])
                fg3m_per_y.append(data_unfiltered_player[5])
                fg3a_per_y.append(data_unfiltered_player[6])
                game_data[str(playerID)] = time
                fg_pct_x_row.append(time)
                fg3_pct_x_row.append(data_unfiltered_player[4])
                pct_fg3a_x_data_row.append(time)
                pct_fg3m_x_data_row.append(data_unfiltered_player[1])
                fg3m_per_x_data_row.append(data_unfiltered_player[6])
                #print("checked")
            else:
                
                continue
        except:
            continue
 
        data_unfiltered = c.execute(""" SELECT mins, Player_ID from BoxScoreTraditional WHERE gameID = ? AND TeamID = ? AND Player_ID != ?""",
                                (game[0], TeamID[0], playerID)).fetchall()

        for row in data_unfiltered:
            try:
                if row[1] in players:
                    mins, sec = row[0].split(":")
                    time = int(mins) + float(sec)/60
                    game_data[str(row[1])] = time
            except:
                continue
        
        for player in players:
            if player not in game_data.keys():
                game_data[player] = 0.0

        game_data = sorted(game_data.items())
        #print(game_data)
        game_data_list = [tuple[1] for tuple in game_data]

        fg3_pct_x_row.append(opposing_team_stats[2]/opposing_team_stats[-1])
        fg3a_x_data.append(fg_pct_x_row+ fg3_pct_x_row)

        pct_fg3a_x_data_row.append(opposing_team_stats[2]/opposing_team_stats[-1])
        pct_fg3a_x_data_row.append(opposing_team_stats[3]/opposing_team_stats[-1])
        pct_fg3a_x_data.append(pct_fg3a_x_data_row)

        pct_fg3m_x_data_row.append(opposing_team_stats[1]/opposing_team_stats[-1])
        pct_fg3m_x_data.append(pct_fg3m_x_data_row)

        fg3m_per_x_data_row.append(opposing_team_stats[1]/opposing_team_stats[-1])
        fg3m_per_x_data_row.append(opposing_team_stats[-2])
        fg3m_per_x_data.append(fg3m_per_x_data_row)
        
        usage_x_data.append(game_data_list)
        x_data.append(game_data_list)

    opp_team = get_opponent(TeamID[0], gameID)
    opposing_team_stats_l5 = c.execute("""SELECT OppShotsL5.TeamID, OppShotsL5.FG3M, OppShotsL5.FG3A, OppShotsL5.FG3_PCT, COUNT(DISTINCT gameID) FROM OppShotsL5 
                                INNER JOIN BoxScoreTraditional ON (OppShotsL5.TeamID = BoxScoreTraditional.TeamID)
                                WHERE OppShotsL5.TeamID = ?""", (opp_team,)).fetchall()[0]
    
    #x_data_pred = [teamMates_list + team_data_list]
    x_data_pred = [teamMates_list]
    #print(x_data_pred)
    pred_pct_fg3a_x = [[player_mins_pred, opposing_team_stats_l5[2]/5, opposing_team_stats_l5[3]/5]]
   
    #pct_fg3a_y
    #print("pctfg3a")
    X_train, X_test, y_train, y_test = train_test_split(pct_fg3a_x_data, pct_fg3a_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pct_fg3a = mlr_model.predict(pred_pct_fg3a_x)
    #print(pct_fg3a)

    #mins dont really matter

    pred_pct_fg3m_x = [[pct_fg3a[0], opposing_team_stats_l5[1]/5]]
    #pct_fg3_pts_y
    #print("pctfgm")
    X_train, X_test, y_train, y_test = train_test_split(pct_fg3m_x_data, pct_fg3_pts_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pct_fg3_pts = mlr_model.predict(pred_pct_fg3m_x)
    #print(pct_fg3_pts)

    #mins dont really matter

    #usage_per_y - needs to be fixed
    #print('usage')
    X_train, X_test, y_train, y_test = train_test_split(usage_x_data, usage_per_y, test_size=0.1, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    usage_per = mlr_model.predict(x_data_pred)
    #print(usage_per)

    #fg3a_per_y
    pred_fg3a_per = [[time, usage_per[0], opposing_team_stats_l5[2]/5]]
    #usage, opp team shots, players?
    X_train, X_test, y_train, y_test = train_test_split(fg3a_x_data, fg3a_per_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print('fg3a_per_y')
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    fg3a_per = mlr_model.predict(pred_fg3a_per)
    #print(fg3a_per)

    #fg3m_per_y
    #print('fg3m_per')
    pred_fg3m_per = [[fg3a_per[0], opposing_team_stats_l5[1]/5, opposing_team_stats_l5[-2]]]
    X_train, X_test, y_train, y_test = train_test_split(fg3m_per_x_data, fg3m_per_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    fg3m_per = mlr_model.predict(pred_fg3m_per)
    #print(fg3m_per)

    conn.commit()
    conn.close()
    return pct_fg3a, pct_fg3_pts, usage_per, fg3m_per, fg3a_per

def get_rebounds_curve(playerID, pred_mins, teamMates, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    
    #variables: rebound chances, total rebounds, opposite team rebounds, rebound usage percentage, who was available
    #BoxScoreTraditional - rebO, rebD, rebT
    #BoxScoreTrack - reb_C_Off, reb_C_Def, reb_C_Tot
    #BoxScoreUsage - rebO_per, rebD_per, rebT_per
    #BoxScoringAdvanced - off_reb_pct, def_reb_pct, reb_pct
    #TeamDefenseRankings - Reb_Cha_GU, Reb_Cha_CL
    #TeamRankings - OREB, DREB, REB

    #predict these variables:
    #BoxScoreTrack - reb_C_Off, reb_C_Def
    #BoxScoreUsage - rebO_per, rebD_per
    #BoxScoringAdvanced - off_reb_pct, def_reb_pct

    reb_C_Off, rebO_per, off_reb_pct = pred_off_reb_var(playerID, teamMates, gameID)
    reb_C_Def, rebD_per, def_reb_pct = pred_def_reb_var(playerID, teamMates, gameID)
    #print(reb_C_Off, rebO_per, off_reb_pct)
    #print(reb_C_Def, rebD_per, def_reb_pct )

    off_reb_data = c.execute(""" SELECT BoxScoreTrack.gameID, BoxScoreTrack.TeamID, BoxScoreTrack.mins, reb_C_Off, rebO, rebO_per, off_reb_pct FROM BoxScoreTrack 
                             INNER JOIN BoxScoreTraditional ON (BoxScoreTrack.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreTrack.gameID = BoxScoreTraditional.gameID)
                             INNER JOIN BoxScoreUsage ON (BoxScoreTrack.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreTrack.gameID = BoxScoreUsage.gameID)
                             INNER JOIN BoxScoringAdvanced ON (BoxScoreTrack.Player_ID = BoxScoringAdvanced.Player_ID AND BoxScoreTrack.gameID = BoxScoringAdvanced.gameID)
                             WHERE BoxScoreTrack.Player_ID = ?""", (playerID,)).fetchall()

    def_reb_data = c.execute(""" SELECT BoxScoreTrack.gameID, BoxScoreTrack.TeamID, BoxScoreTrack.mins, reb_C_Def, rebD, rebD_per, def_reb_pct FROM BoxScoreTrack INNER JOIN 
                             BoxScoreTraditional ON (BoxScoreTrack.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreTrack.gameID = BoxScoreTraditional.gameID)
                             INNER JOIN BoxScoreUsage ON (BoxScoreTrack.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreTrack.gameID = BoxScoreUsage.gameID)
                             INNER JOIN BoxScoringAdvanced ON (BoxScoreTrack.Player_ID = BoxScoringAdvanced.Player_ID AND BoxScoreTrack.gameID = BoxScoringAdvanced.gameID)
                             WHERE BoxScoreTrack.Player_ID = ?""", (playerID,)).fetchall()

    off_reb_y = []
    def_reb_y = []
    off_reb_X_data = []
    def_reb_X_data = []
    for row in off_reb_data:
        try:
            mins, sec = row[2].split(":")
            time = int(mins) + float(sec)/60
            x_row=[time, row[3], row[5], row[6]]
            off_reb_X_data.append(x_row)
            off_reb_y.append(row[4])
        except:
            continue
    
    #fix def rebounds
    for row in def_reb_data:
        try:
            mins, sec = row[2].split(":")
            time = int(mins) + float(sec)/60
            x_row=[time, row[3], row[5], row[6]]
            def_reb_X_data.append(x_row)
            def_reb_y.append(row[4])
        except:
            continue
    

    #offensive rebounds
    X_train, X_test, y_train, y_test = train_test_split(off_reb_X_data, off_reb_y, test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_rebO = mlr_model.predict([[pred_mins, reb_C_Off[0], rebO_per[0], off_reb_pct[0]]])
    
    #defensive rebounds
    X_train, X_test, y_train, y_test = train_test_split(def_reb_X_data, def_reb_y , test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    y_pred=mlr_model.predict(X_test)
    #print("Predictions:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_rebD= mlr_model.predict([[pred_mins, reb_C_Def[0], rebD_per[0], def_reb_pct[0]]])

    pred_reb = pred_rebD + pred_rebO
    #print(pred_rebO)
    #print(pred_rebD)
    #print(pred_reb)

    conn.commit()
    conn.close()
    return pred_reb[0]

def pred_off_reb_var(playerID, teamMates, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    
    teamID = c.execute(""" SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchone()
    players = c.execute(""" SELECT Player_ID FROM PlayerProfiles WHERE TeamID = ?""", (teamID[0],)).fetchall()
    players = [str(player[0]) for player in players]

    for player in players:
            if player not in teamMates.keys():
                teamMates[str(player)] = 0.0
    
    teamMates = sorted(teamMates.items())
    teamMates_list = [float(tuple[1]) for tuple in teamMates]
    games = c.execute(""" SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ?""", (teamID[0], teamID[0],)).fetchall()

    player_team_data = c.execute("""SELECT TeamDefenseRankings.TeamID, Reb_Cha_CL, OREB
                                        FROM TeamDefenseRankings 
                                        INNER JOIN TeamRankings ON (TeamDefenseRankings.TeamID = TeamRankings.TeamID)
                                        INNER JOIN PositionStatsDef ON (TeamDefenseRankings.TeamID = PositionStatsDef.TeamID)
                                        WHERE TeamDefenseRankings.TeamID = ?""", (teamID[0],)).fetchall()[0]

    overall_data_x = []
    reb_C_off_y = []
    rebO_per_y = []
    off_reb_pct_y = []

    for game in games:
        game_data = {}
        try:
            data_unfiltered_player = c.execute(""" SELECT BoxScoreTrack.mins, reb_C_Off, rebO_per, off_reb_pct FROM BoxScoreTrack INNER JOIN 
                            BoxScoreTraditional ON (BoxScoreTrack.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreTrack.gameID = BoxScoreTraditional.gameID)
                            INNER JOIN BoxScoreUsage ON (BoxScoreTrack.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreTrack.gameID = BoxScoreUsage.gameID)
                            INNER JOIN BoxScoringAdvanced ON (BoxScoreTrack.Player_ID = BoxScoringAdvanced.Player_ID AND BoxScoreTrack.gameID = BoxScoringAdvanced.gameID)
                            WHERE BoxScoreTrack.Player_ID = ? AND BoxScoreUsage.gameID=?""", (playerID, game[0],)).fetchall()[0]
            mins, sec = data_unfiltered_player[0].split(":")
            time = int(mins) + float(sec)/60
            if time != 0.0:
                reb_C_off_y.append(data_unfiltered_player[1])
                rebO_per_y.append(data_unfiltered_player[2])
                off_reb_pct_y.append(data_unfiltered_player[3])
                game_data[str(playerID)] = time
            else:
                continue
        except:
            continue
 
        data_unfiltered = c.execute(""" SELECT mins, Player_ID from BoxScoreTraditional WHERE gameID = ? AND TeamID = ? AND Player_ID != ?""",
                                (game[0], teamID[0], playerID)).fetchall()

        for row in data_unfiltered:
            try:
                if row[1] in players:
                    mins, sec = row[0].split(":")
                    time = int(mins) + float(sec)/60
                    game_data[str(row[1])] = time
            except:
                continue
        
        for player in players:
            if player not in game_data.keys():
                game_data[str(player)] = 0.0
        
        opp_team = get_opponent(teamID[0], game[0])
        reb_team_data = c.execute("""SELECT TeamDefenseRankings.TeamID, Reb_Cha_GU, DREB, rebs_diff_C, avg_rebs_C,
                                        rebs_diff_SF, avg_rebs_SF, rebs_diff_PF, avg_rebs_PF, rebs_diff_SG, avg_rebs_SG, rebs_diff_PG, avg_rebs_PG
                                        FROM TeamDefenseRankings 
                                        INNER JOIN TeamRankings ON (TeamDefenseRankings.TeamID = TeamRankings.TeamID)
                                        INNER JOIN PositionStatsDef ON (TeamDefenseRankings.TeamID = PositionStatsDef.TeamID)
                                        WHERE TeamDefenseRankings.TeamID != ?""", (opp_team,)).fetchall()[0]
            
        position = c.execute("""SELECT Main_Position FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchall()

        game_data = sorted(game_data.items())
        game_data_list = [tuple[1] for tuple in game_data]
        team_data_list = []
        if position[0][0] == "C":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[3], reb_team_data[4],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "SF":
            team_data_list= [reb_team_data[1], reb_team_data[2], reb_team_data[5], reb_team_data[6],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "PF":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[7], reb_team_data[8],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "SG":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[9], reb_team_data[10],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "PG":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[11], reb_team_data[12],player_team_data[1], player_team_data[2]]
        overall_data_x.append(game_data_list + team_data_list)



    #predict these variables:
    #BoxScoreTrack - reb_C_Off, reb_C_Def
    #BoxScoreUsage - rebO_per, rebD_per
    #BoxScoringAdvanced - off_reb_pct, def_reb_pct

    opp_team = get_opponent(teamID[0], game[0])
    reb_team_data = c.execute("""SELECT TeamDefenseRankings.TeamID, Reb_Cha_GU, DREB, rebs_diff_C, avg_rebs_C,
                                    rebs_diff_SF, avg_rebs_SF, rebs_diff_PF, avg_rebs_PF, rebs_diff_SG, avg_rebs_SG, rebs_diff_PG, avg_rebs_PG
                                    FROM TeamDefenseRankings 
                                    INNER JOIN TeamRankings ON (TeamDefenseRankings.TeamID = TeamRankings.TeamID)
                                    INNER JOIN PositionStatsDef ON (TeamDefenseRankings.TeamID = PositionStatsDef.TeamID)
                                    WHERE TeamDefenseRankings.TeamID != ?""", (opp_team,)).fetchall()[0]
        
    position = c.execute("""SELECT Main_Position FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchall()
    team_data_list = []
    if position[0][0] == "C":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[3], reb_team_data[4],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "SF":
        team_data_list= [reb_team_data[1], reb_team_data[2], reb_team_data[5], reb_team_data[6],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "PF":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[7], reb_team_data[8],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "SG":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[9], reb_team_data[10],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "PG":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[11], reb_team_data[12],player_team_data[1], player_team_data[2]]
    x_data = teamMates_list + team_data_list

    #reb_C_Def
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, reb_C_off_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_reb_C_Off = mlr_model.predict([x_data])

    #rebD_per_y
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, rebO_per_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_rebO_per = mlr_model.predict([x_data])

    #def_reb_pct_y
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, off_reb_pct_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_off_reb_pct = mlr_model.predict([x_data])
    
    conn.commit()
    conn.close()
    return pred_reb_C_Off, pred_rebO_per, pred_off_reb_pct

def pred_def_reb_var(playerID, teamMates, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    
    teamID = c.execute(""" SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchone()
    players = c.execute(""" SELECT Player_ID FROM PlayerProfiles WHERE TeamID = ?""", (teamID[0],)).fetchall()
    players = [str(player[0]) for player in players]

    for player in players:
            if player not in teamMates.keys():
                teamMates[player] = 0.0
    
    teamMates = sorted(teamMates.items())
    teamMates_list = [float(tuple[1]) for tuple in teamMates]
    games = c.execute(""" SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ?""", (teamID[0], teamID[0],)).fetchall()

    player_team_data = c.execute("""SELECT TeamDefenseRankings.TeamID, Reb_Cha_GU, DREB
                                        FROM TeamDefenseRankings 
                                        INNER JOIN TeamRankings ON (TeamDefenseRankings.TeamID = TeamRankings.TeamID)
                                        INNER JOIN PositionStatsDef ON (TeamDefenseRankings.TeamID = PositionStatsDef.TeamID)
                                        WHERE TeamDefenseRankings.TeamID = ?""", (teamID[0],)).fetchall()[0]

    overall_data_x = []
    reb_C_Def_y = []
    rebD_per_y = []
    def_reb_pct_y = []

    for game in games:
        game_data = {}
        try:
            data_unfiltered_player = c.execute(""" SELECT BoxScoreTrack.mins, reb_C_Def, rebD_per, def_reb_pct FROM BoxScoreTrack INNER JOIN 
                            BoxScoreTraditional ON (BoxScoreTrack.Player_ID = BoxScoreTraditional.Player_ID AND BoxScoreTrack.gameID = BoxScoreTraditional.gameID)
                            INNER JOIN BoxScoreUsage ON (BoxScoreTrack.Player_ID = BoxScoreUsage.Player_ID AND BoxScoreTrack.gameID = BoxScoreUsage.gameID)
                            INNER JOIN BoxScoringAdvanced ON (BoxScoreTrack.Player_ID = BoxScoringAdvanced.Player_ID AND BoxScoreTrack.gameID = BoxScoringAdvanced.gameID)
                            WHERE BoxScoreTrack.Player_ID = ? AND BoxScoreUsage.gameID=?""", (playerID, game[0],)).fetchall()[0]
            mins, sec = data_unfiltered_player[0].split(":")
            time = int(mins) + float(sec)/60
            if time != 0.0:
                reb_C_Def_y.append(data_unfiltered_player[1])
                rebD_per_y.append(data_unfiltered_player[2])
                def_reb_pct_y.append(data_unfiltered_player[3])
                
                game_data[str(playerID)] = time
            else:
                continue
        except:
            continue
 
        data_unfiltered = c.execute(""" SELECT mins, Player_ID from BoxScoreTraditional WHERE gameID = ? AND TeamID = ? AND Player_ID != ?""",
                                (game[0], teamID[0], playerID)).fetchall()

        for row in data_unfiltered:
            try:
                if row[1] in players:
                    mins, sec = row[0].split(":")
                    time = int(mins) + float(sec)/60
                    game_data[str(row[1])] = time
            except:
                continue
        
        for player in players:
            if player not in game_data.keys():
                game_data[player] = 0.0
        
        opp_team = get_opponent(teamID[0], game[0])
        reb_team_data = c.execute("""SELECT TeamDefenseRankings.TeamID, Reb_Cha_CL, OREB, rebs_diff_C, avg_rebs_C,
                                        rebs_diff_SF, avg_rebs_SF, rebs_diff_PF, avg_rebs_PF, rebs_diff_SG, avg_rebs_SG, rebs_diff_PG, avg_rebs_PG
                                        FROM TeamDefenseRankings 
                                        INNER JOIN TeamRankings ON (TeamDefenseRankings.TeamID = TeamRankings.TeamID)
                                        INNER JOIN PositionStatsDef ON (TeamDefenseRankings.TeamID = PositionStatsDef.TeamID)
                                        WHERE TeamDefenseRankings.TeamID != ?""", (opp_team,)).fetchall()[0]
            
        position = c.execute("""SELECT Main_Position FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchall()

        game_data = sorted(game_data.items())
        game_data_list = [tuple[1] for tuple in game_data]
        team_data_list = []
        if position[0][0] == "C":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[3], reb_team_data[4],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "SF":
            team_data_list= [reb_team_data[1], reb_team_data[2], reb_team_data[5], reb_team_data[6],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "PF":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[7], reb_team_data[8],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "SG":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[9], reb_team_data[10],player_team_data[1], player_team_data[2]]
        elif position[0][0] == "PG":
            team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[11], reb_team_data[12],player_team_data[1], player_team_data[2]]
        overall_data_x.append(game_data_list + team_data_list)



    #predict these variables:
    #BoxScoreTrack - reb_C_Off, reb_C_Def
    #BoxScoreUsage - rebO_per, rebD_per
    #BoxScoringAdvanced - off_reb_pct, def_reb_pct

    opp_team = get_opponent(teamID[0], game[0])
    reb_team_data = c.execute("""SELECT TeamDefenseRankings.TeamID, Reb_Cha_CL, OREB, rebs_diff_C, avg_rebs_C,
                                    rebs_diff_SF, avg_rebs_SF, rebs_diff_PF, avg_rebs_PF, rebs_diff_SG, avg_rebs_SG, rebs_diff_PG, avg_rebs_PG
                                    FROM TeamDefenseRankings 
                                    INNER JOIN TeamRankings ON (TeamDefenseRankings.TeamID = TeamRankings.TeamID)
                                    INNER JOIN PositionStatsDef ON (TeamDefenseRankings.TeamID = PositionStatsDef.TeamID)
                                    WHERE TeamDefenseRankings.TeamID != ?""", (opp_team,)).fetchall()[0]
        
    position = c.execute("""SELECT Main_Position FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchall()
    team_data_list = []
    if position[0][0] == "C":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[3], reb_team_data[4],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "SF":
        team_data_list= [reb_team_data[1], reb_team_data[2], reb_team_data[5], reb_team_data[6],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "PF":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[7], reb_team_data[8],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "SG":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[9], reb_team_data[10],player_team_data[1], player_team_data[2]]
    elif position[0][0] == "PG":
        team_data_list = [reb_team_data[1], reb_team_data[2], reb_team_data[11], reb_team_data[12],player_team_data[1], player_team_data[2]]
    x_data = teamMates_list + team_data_list

    #reb_C_Def
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, reb_C_Def_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_reb_C_Def = mlr_model.predict([x_data])

    #rebD_per_y
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, rebD_per_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_rebD_per = mlr_model.predict([x_data])

    #def_reb_pct_y
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, def_reb_pct_y, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)
    pred_def_reb_pct = mlr_model.predict([x_data])
    
    conn.commit()
    conn.close()
    return pred_reb_C_Def, pred_rebD_per, pred_def_reb_pct

def get_assists_curve(playerID, pred_mins, teamMates):
    #playerID, mins, gameID, teamMates

    #teamMates is list
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    #predict usage, and passes
    #maybe also overall usage percentage
    pred_ast_per, pred_ast_pct, pred_passes = predictUsagePassesPCT(playerID, pred_mins, teamMates)

    data_unfiltered = c.execute(""" SELECT minutes, ast_per, ast_pct, passes, assists 
                                FROM BoxScoreUsage INNER JOIN BoxScoringAdvanced
                                ON (BoxScoreUsage.Player_ID = BoxScoringAdvanced.Player_ID AND BoxScoreUsage.gameID = BoxScoringAdvanced.gameID)
                                INNER JOIN BoxScoreTrack
                                ON (BoxScoreUsage.Player_ID = BoxScoreTrack.Player_ID AND BoxScoreUsage.gameID = BoxScoreTrack.gameID) WHERE BoxScoreUsage.Player_ID = ? """,
                                (playerID,)).fetchall()
    #TABLES: BoxScoreUsage(mins, usage for assist), BoxScoringAdvanced(assist percentage), BoxScoreTrack (Passes, assists)
    
    y = []
    X_data = []
    for row in data_unfiltered:
        try:
            mins, sec = row[0].split(":")
            time = int(mins) + float(sec)/60
            x_row = [time, row[1], row[2], row[3]]
            X_data.append(x_row)
            y.append(row[4])
        except:
            continue

    #print(X_data)
    #print('2')
    X_train, X_test, y_train, y_test = train_test_split(X_data, y, test_size=0.2, random_state=0)
    #print("Training data shape:", X_train)
    #print("Testing data shape:", X_test)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    #print("Intercept:", mlr_model.intercept_)
    
    y_pred=mlr_model.predict(X_test)
    #print("Predictinos:", y_pred[:5])
    #print("Actual", y_test[:5])
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    #print("Mean Squared Error:", mse)
    #print("R-squared:", r2)

    
    #print([[pred_mins, pred_ast_per[0], pred_ast_pct[0], pred_passes[0]]])
    y_pred=mlr_model.predict([[pred_mins, pred_ast_per[0], pred_ast_pct[0], pred_passes[0]]])
    
    conn.commit()
    conn.close()
    return y_pred[0]

def predictUsagePassesPCT(playerID, pred_mins, teamMates):
    #teamMates is list of teamMatesID
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()

    teamID = c.execute(""" SELECT TeamID FROM PlayerProfiles WHERE Player_ID = ?""", (playerID,)).fetchone()
    players = c.execute(""" SELECT Player_ID FROM PlayerProfiles WHERE TeamID = ?""", (teamID[0],)).fetchall()
    players = [str(player[0]) for player in players]

    for player in players:
            if player not in teamMates.keys():
                teamMates[str(player)] = 0.0
    
    teamMates = sorted(teamMates.items())
    #print(teamMates)
    teamMates_list = [float(tuple[1]) for tuple in teamMates]
    #print(teamMates_list)
    games = c.execute(""" SELECT gameID FROM Fixtures WHERE homeTeamID = ? OR awayTeamID = ?""", (teamID[0], teamID[0],)).fetchall()
    overall_data_x = []
    ast_per = []
    ast_pct = []
    passes = []

    for game in games:
        game_data = {}
        try:
            data_unfiltered_player = c.execute(""" SELECT minutes, ast_per, ast_pct, passes 
                                    FROM BoxScoreUsage INNER JOIN BoxScoringAdvanced
                                    ON (BoxScoreUsage.Player_ID = BoxScoringAdvanced.Player_ID AND BoxScoreUsage.gameID = BoxScoringAdvanced.gameID)
                                    INNER JOIN BoxScoreTrack
                                    ON (BoxScoreUsage.Player_ID = BoxScoreTrack.Player_ID AND BoxScoreUsage.gameID = BoxScoreTrack.gameID) WHERE BoxScoreUsage.Player_ID = ? AND BoxScoreUsage.gameID=?""",
                                    (playerID, game[0])).fetchall()[0]
            mins, sec = data_unfiltered_player[0].split(":")
            time = int(mins) + float(sec)/60
            if time != 0.0:
                ast_per.append(data_unfiltered_player[1])
                ast_pct.append(data_unfiltered_player[2])
                passes.append(data_unfiltered_player[3])
                
                game_data[str(playerID)] = time
            else:
                continue
        except:
            continue
 
        data_unfiltered = c.execute(""" SELECT mins, Player_ID from BoxScoreTraditional WHERE gameID = ? AND TeamID = ? AND Player_ID != ?""",
                                (game[0], teamID[0], playerID)).fetchall()

        for row in data_unfiltered:
            try:
                if row[1] in players:
                    mins, sec = row[0].split(":")
                    time = int(mins) + float(sec)/60
                    game_data[str(row[1])] = time
            except:
                continue
        
        for player in players:
            if player not in game_data.keys():
                game_data[player] = 0.0

        game_data = sorted(game_data.items())
        game_data_list = [tuple[1] for tuple in game_data]
        overall_data_x.append(game_data_list)
    
    #assist per training
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, ast_per, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    pred_ast_per = mlr_model.predict([teamMates_list])

    #assist percentage training
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, ast_pct, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    pred_ast_pct = mlr_model.predict([teamMates_list])

    #passestraining
    X_train, X_test, y_train, y_test = train_test_split(overall_data_x, passes, test_size=0.2, random_state=0)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train, y_train)
    pred_passes = mlr_model.predict([teamMates_list])
    
    conn.commit()
    conn.close()
    return pred_ast_per, pred_ast_pct, pred_passes

def predict_points(playerID, gameID):
    filepath = os.path.join("database", "main2024.db")
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    
    #
    #points is target


    conn.commit()
    conn.close()
    