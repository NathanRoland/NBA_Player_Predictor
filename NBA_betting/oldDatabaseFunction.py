def createTeamActivePlayers():
    #basics e.g name, playerid, teamid, teamname, position
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PlayerProfiles")
    table = """ CREATE TABLE PlayerProfiles (
                Player_ID VARCHAR(255) NOT NULL,
                Player_Name VARCHAR(255) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                Abbreviation CHAR(3) NOT NULL,
                Main_Position VARCHAR(2) NOT NULL,
                Second_Position VARCHAR(2),
                PRIMARY KEY (Player_ID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
            ); """
    c.execute(table)
    conn.commit()
    conn.close()

def createTeamActivePlayers():
    #basics e.g name, playerid, teamid, teamname, position
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS PlayerProfiles")
    table = """ CREATE TABLE PlayerProfiles (
                Player_ID VARCHAR(255) NOT NULL,
                Player_Name VARCHAR(255) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                Abbreviation CHAR(3) NOT NULL,
                Main_Position VARCHAR(2) NOT NULL,
                Second_Position VARCHAR(2),
                PRIMARY KEY (Player_ID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
            ); """
    c.execute(table)
    conn.commit()
    conn.close()
    
    nba_players = players.get_active_players()
    for nba_player in nba_players:

        player_id = nba_player.get('id')
        player_name = nba_player.get('full_name')

        career = commonplayerinfo.CommonPlayerInfo(player_id)
        career = career.get_dict()
        team_data = career.get("resultSets")[0].get("rowSet")[0]
        team_abbreviaton = team_data[20]
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
        print(first_position)
        print(second_position)
        teamID = team_data[18]

        c.execute('''INSERT INTO PlayerProfiles 
                  (Player_ID, Player_Name, TeamID, Abbreviation, Main_Position, Second_Position) 
                  VALUES (?, ?, ?, ?, ?, ?)''', 
                  (player_id, player_name, teamID, team_abbreviaton, first_position, second_position))
    conn.commit()
    conn.close()




def createPlayerseasons():
    #get averages for past 3 seasons/teams
    # player-id, season year, seasonidm, season Name, team, matches, 
    #averages of these: min, points, reb, assists, fga, fgm, fg_pct, fg3a, fg3m, fg3_pct
    file_path = os.path.join('database','main.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS SeasonLogs")
    
    table = """ CREATE TABLE SeasonLogs (
                Player_ID VARCHAR(255) NOT NULL,
                Seaon_Year VARCHAR(7) NOT NULL,
                Season_ID VARCHAR(25) NOT NULL,
                Season_Name VARCHAR(25) NOT NULL,
                TeamID CHAR(25) NOT NULL,
                Matches INTEGER(2) NOT NULL,
                Minutes INTEGER(4) NOT NULL,
                Points FLOAT(3, 1) NOT NULL,
                Rebounds FLOAT(3, 1) NOT NULL,
                Assists FLOAT(3, 1) NOT NULL,
                FGA FLOAT(3, 1) NOT NULL,
                FGM FLOAT(3, 1) NOT NULL,
                FG_PCT FLOAT(3, 1) NOT NULL,
                FG3A FLOAT(3, 1) NOT NULL,
                FG3M FLOAT(3, 1) NOT NULL,
                FG3_PCT FLOAT(3, 1) NOT NULL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID),
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
            ); """
    
    c.execute(table)
    
    nba_players = players.get_active_players()
    nba_players = nba_players
    for nba_player in nba_players:
        player_id = nba_player.get('id')
        career = commonplayerinfo.CommonPlayerInfo(player_id)
        career = career.get_dict()
        team_data = career.get("resultSets")[0].get("rowSet")[0]
        team_abbreviaton = team_data[20]
        teamID = team_data[18]
    
        #c.execute('''INSERT INTO SeasonLogs (
        #                  Player_ID, Seaon_Year, Season_ID, Season_Name, TeamID, Matches, Minutes, Points, Rebounds, Assists, FGA, FGM, FG_PCT, FG3A, FG3M, FG3_PCT) 
        #                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
        #                  (player_id, "2024-25", "22024", "2024-25" +" "+ team_abbreviaton, teamID, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
       
        
        playerprofile = playerprofilev2.PlayerProfileV2(player_id)
        playerprofile = playerprofile.get_dict()
        playerprofile = playerprofile.get("resultSets")[0].get('rowSet')[::-1]
        seasons_count = 0
        for season in playerprofile:
            seasonID = yearIDs.get(season[1])
            if seasons_count >= 3:
                break
            if season[4] == 'TOT' or seasonID is None:
                next
            else:
                seasons_count += 1
                #print(season)
                Year = season[1]
                Team_ID = season[3]
                
                matches = season[6]
                minutes = season[8]
                Season_Name = Year + " " + season[4]
                fgm = round(season[9] / matches , 2)
                fga = round(season[10] / matches , 2)
                fg_pct = round(season[11] *100, 2)
                fg3m = round(season[12] / matches , 2)
                fg3a = round(season[13] / matches , 2)
                fg3_pct = round(season[14] *100, 2)
                reb = round(season[20] / matches , 2)
                ast = round(season[21] / matches , 2)
                pts = round(season[-1] / matches , 2)
                
                c.execute('''INSERT INTO SeasonLogs (
                          Player_ID, Seaon_Year, Season_ID, Season_Name, TeamID, Matches, Minutes, Points, Rebounds, Assists, FGA, FGM, FG_PCT, FG3A, FG3M, FG3_PCT) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (player_id, Year, seasonID, Season_Name, Team_ID, matches, minutes, pts, reb, ast, fga, fgm, fg_pct, fg3a, fg3m, fg3_pct))
    conn.commit()
    conn.close()


def createPlayerGameLogs():
    #expand to include potential assists, potential rebounds, potential poins etc
    file_path = os.path.join('database','main.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS GameLogs")
    
    table = """ CREATE TABLE GameLogs (
                Player_ID VARCHAR(255) NOT NULL,
                Seaon_Year VARCHAR(7) NOT NULL,
                Season_ID VARCHAR(25) NOT NULL,
                Season_Name VARCHAR(25) NOT NULL,
                Abbreviation VARCHAR(3) NOT NULL,
                Opponent VARCHAR(3) NOT NULL,
                Game_Date DATE,
                Game_ID VARCHAR(255) NOT NULL,
                Minutes INTEGER(4) NOT NULL,
                Points FLOAT(3, 1) NOT NULL,
                Rebounds FLOAT(3, 1) NOT NULL,
                Assists FLOAT(3, 1) NOT NULL,
                FGA FLOAT(3, 1) NOT NULL,
                FGM FLOAT(3, 1) NOT NULL,
                FG_PCT FLOAT(3, 1) NOT NULL,
                FG3A FLOAT(3, 1) NOT NULL,
                FG3M FLOAT(3, 1) NOT NULL,
                FG3_PCT FLOAT(3, 1) NOT NULL,
                Points_Diff FLOAT(3, 1) NOT NULL,
                Rebound_Diff FLOAT(3, 1) NOT NULL,
                Assists_Diff FLOAT(3, 1) NOT NULL,
                FGA_Diff FLOAT(3, 1) NOT NULL,
                FGM_Diff FLOAT(3, 1) NOT NULL,
                FG_PCT_Diff FLOAT(3, 1) NOT NULL,
                FG3A_Diff FLOAT(3, 1) NOT NULL,
                FG3M_Diff FLOAT(3, 1) NOT NULL,
                FG3_PCT_Diff FLOAT(3, 1) NOT NULL,
                FOREIGN KEY (Player_ID) REFERENCES PlayerProfiles(Player_ID)
            ); """
    
    c.execute(table)

    nba_players = players.get_active_players()
    for nba_player in nba_players:
        id = nba_player.get('id')
        career = commonplayerinfo.CommonPlayerInfo(id)
        career = career.get_dict()
        career = career.get("resultSets")[0].get("rowSet")[0]
        playerprofile = playerprofilev2.PlayerProfileV2(id)
        playerprofile = playerprofile.get_dict()
        playerprofile = playerprofile.get("resultSets")[0].get('rowSet')[::-1]
        seasons = []
        matchups = {}
        seasons_count = 0
        for season in playerprofile:
            seasonID = yearIDs.get(season[1])
            if seasons_count >= 3:
                break
            if season[4] == 'TOT' or seasonID is None:
                next
            else:
                seasons_count += 1
                Year = season[1]
                Abb = season[4]
                matches = season[6]
                seasonID = yearIDs.get(season[1])
                
                season_name = season[1] + " " + season[4]

                logs = playergamelog.PlayerGameLog(player_id=id, season=season[1])
                logs = logs.get_dict()
                logs = logs.get("resultSets")[0].get('rowSet')
                for game in logs:
                    matchup = game[4]
                    date = game[3]
                    date = convertDate(date)
                    game_id = game[2]
                    matchup = matchup.split(" ")
                    team = matchup[0]
                    opp = matchup[2]
                    if team != season[4]:
                        next
                    else:
                        fgm = game[7]
                        fga = game[8]
                        fg_pct = round(game[9] * 100, 2)
                        fg3m = game[10]
                        fg3a = game[11]
                        fg3_pct = round(game[12] * 100, 2)
                        reb = game[18]
                        ast = game[19]
                        pts = game[24]
                        mins = game[6]
                        act_vs_exp_fgm = round(fgm - round(season[9] / matches , 2), 2)
                        act_vs_exp_fga = round(fga - round(season[10] / matches , 2), 2)
                        act_vs_exp_fg_pct = round(fg_pct - (season[11]*100), 2)
                        act_vs_exp_fg3m = round(fg3m - round(season[12] / matches , 2), 2)
                        act_vs_exp_fg3a = round(fg3a - round(season[13] / matches , 2), 2)
                        act_vs_exp_fg3_pct = round(fg3_pct - (season[14]*100), 2)
                        act_vs_exp_reb = round(reb - round(season[20] / matches , 2), 2)
                        act_vs_exp_ast = round(ast - round(season[21] / matches , 2), 2)
                        act_vs_exp_pts = round(pts - round(season[-1] / matches , 2), 2)
                        
                        c.execute('''INSERT INTO GameLogs (
                                    Player_ID, Seaon_Year, Season_ID, Season_Name, Abbreviation, Opponent, Game_Date, Game_ID, Minutes, Points,
                                    Rebounds, Assists, FGA, FGM, FG_PCT, FG3A, FG3M, FG3_PCT, Points_Diff, Rebound_Diff, Assists_Diff, FGA_Diff,
                                    FGM_Diff, FG_PCT_Diff, FG3A_Diff, FG3M_Diff, FG3_PCT_Diff
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (id, Year, seasonID, season_name, Abb, opp, date, game_id, mins, pts, reb, ast, fga, fgm, fg_pct, fg3a, fg3m, fg3_pct, act_vs_exp_pts, 
                            act_vs_exp_reb, act_vs_exp_ast, act_vs_exp_fga, act_vs_exp_fgm, act_vs_exp_fg_pct, act_vs_exp_fg3a, act_vs_exp_fg3m, act_vs_exp_fg3_pct))
    conn.commit()
    conn.close()


def Create_Team_Position_Statistics():
    #get how well the team performs against opposition players
    #forward diff in: pts, reb, ast (all use IQR), fga, fgm, fg%, fg3a, fg3m, fg3%
    #guard diff in: pts, reb, ast (all use IQR), fga, fgm, fg%, fg3a, fg3m, fg3%
    #Centre diff in: pts, reb, ast (all use IQR), fga, fgm, fg%, fg3a, fg3m, fg3%
    #more specialised poisitions
    #also compare to rest of league

    file_path = os.path.join('database','main.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Team_Opp_Position_Stats")
    table = """ CREATE TABLE Team_Opp_Position_Stats (
                TeamID CHAR(25) NOT NULL,
                Seaon_Year VARCHAR(7) NOT NULL,
                Season_ID VARCHAR(25) NOT NULL,
                G_Avg_Points_Diff FLOAT(3, 1) NOT NULL,
                G_Q1_Points_Diff FLOAT(3, 1) NOT NULL,
                G_Q3_Points_Diff FLOAT(3, 1) NOT NULL,
                G_STDEV_Points_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_Rebound_Diff FLOAT(3, 1) NOT NULL,
                G_Q1_Rebound_Diff FLOAT(3, 1) NOT NULL,
                G_Q3_Rebound_Diff FLOAT(3, 1) NOT NULL,
                G_STDEV_Revound_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_Assists_Diff FLOAT(3, 1) NOT NULL,
                G_Q1_Assist_Diff FLOAT(3, 1) NOT NULL,
                G_Q3_Assist_Diff FLOAT(3, 1) NOT NULL,
                G_STDEV_Assist_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_FGA_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_FGM_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_FG_PCT_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_FG3A_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_FG3M_Diff FLOAT(3, 1) NOT NULL,
                G_Avg_FG3_PCT_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_Points_Diff FLOAT(3, 1) NOT NULL,
                F_Q1_Points_Diff FLOAT(3, 1) NOT NULL,
                F_Q3_Points_Diff FLOAT(3, 1) NOT NULL,
                F_STDEV_Points_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_Rebound_Diff FLOAT(3, 1) NOT NULL,
                F_Q1_Rebound_Diff FLOAT(3, 1) NOT NULL,
                F_Q3_Rebound_Diff FLOAT(3, 1) NOT NULL,
                F_STDEV_Rebound_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_Assists_Diff FLOAT(3, 1) NOT NULL,
                F_Q1_Assist_Diff FLOAT(3, 1) NOT NULL,
                F_Q3_Assist_Diff FLOAT(3, 1) NOT NULL,
                F_STDEV_Assist_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_FGA_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_FGM_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_FG_PCT_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_FG3A_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_FG3M_Diff FLOAT(3, 1) NOT NULL,
                F_Avg_FG3_PCT_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_Points_Diff FLOAT(3, 1) NOT NULL,
                C_Q1_Points_Diff FLOAT(3, 1) NOT NULL,
                C_Q3_Points_Diff FLOAT(3, 1) NOT NULL,
                C_STDEV_Points_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_Rebound_Diff FLOAT(3, 1) NOT NULL,
                C_Q1_Rebound_Diff FLOAT(3, 1) NOT NULL,
                C_Q3_Rebound_Diff FLOAT(3, 1) NOT NULL,
                C_STDEV_Rebound_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_Assists_Diff FLOAT(3, 1) NOT NULL,
                C_Q1_Assist_Diff FLOAT(3, 1) NOT NULL,
                C_Q3_Assist_Diff FLOAT(3, 1) NOT NULL,
                C_STDEV_Assist_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_FGA_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_FGM_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_FG_PCT_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_FG3A_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_FG3M_Diff FLOAT(3, 1) NOT NULL,
                C_Avg_FG3_PCT_Diff FLOAT(3, 1) NOT NULL,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
            ); """
    c.execute(table)

    #guards- then forwards - then centres
    teamList = c.execute("SELECT Abbreviation, TeamID FROM Teams").fetchall()
    for team in teamList:
        Abbreviation, TeamID = team
        for season in yearIDs:
            seasonID = yearIDs.get(season)
            sql = '''SELECT Points_Diff, Rebound_Diff, Assists_Diff, FGA_Diff, FGM_Diff, FG_PCT_Diff, FG3A_Diff, FG3M_Diff, FG3_PCT_Diff
            FROM GameLogs
            INNER JOIN PlayerProfiles
            ON GameLogs.Player_ID = PlayerProfiles.Player_ID 
            WHERE GameLogs.Opponent=? AND GameLogs.Season_ID=? AND PlayerProfiles.Main_Position="Guard"
            '''
            myresult = c.execute(sql, (Abbreviation, seasonID)).fetchall()
            G_Avg_Points_Diff, G_Q1_Points_Diff, G_Q3_Points_Diff, G_STDEV_Points_Diff, G_Avg_Rebound_Diff, G_Q1_Rebound_Diff, G_Q3_Rebound_Diff, G_STDEV_Revound_Diff, G_Avg_Assists_Diff, G_Q1_Assist_Diff, G_Q3_Assist_Diff, G_STDEV_Assist_Diff, G_Avg_FGA_Diff, G_Avg_FGM_Diff, G_Avg_FG_PCT_Diff, G_Avg_FG3A_Diff, G_Avg_FG3M_Diff, G_Avg_FG3_PCT_Diff = averages_and_iqr(myresult)

            seasonID = yearIDs.get(season)
            sql = '''SELECT Points_Diff, Rebound_Diff, Assists_Diff, FGA_Diff, FGM_Diff, FG_PCT_Diff, FG3A_Diff, FG3M_Diff, FG3_PCT_Diff
            FROM GameLogs
            INNER JOIN PlayerProfiles
            ON GameLogs.Player_ID = PlayerProfiles.Player_ID 
            WHERE GameLogs.Opponent=? AND GameLogs.Season_ID=? AND PlayerProfiles.Main_Position="Forward"
            '''
            myresult = c.execute(sql, (Abbreviation, seasonID)).fetchall()
            F_Avg_Points_Diff, F_Q1_Points_Diff, F_Q3_Points_Diff, F_STDEV_Points_Diff, F_Avg_Rebound_Diff, F_Q1_Rebound_Diff, F_Q3_Rebound_Diff, F_STDEV_Revound_Diff, F_Avg_Assists_Diff, F_Q1_Assist_Diff, F_Q3_Assist_Diff, F_STDEV_Assist_Diff, F_Avg_FGA_Diff, F_Avg_FGM_Diff, F_Avg_FG_PCT_Diff, F_Avg_FG3A_Diff, F_Avg_FG3M_Diff, F_Avg_FG3_PCT_Diff = averages_and_iqr(myresult)

            seasonID = yearIDs.get(season)
            sql = '''SELECT Points_Diff, Rebound_Diff, Assists_Diff, FGA_Diff, FGM_Diff, FG_PCT_Diff, FG3A_Diff, FG3M_Diff, FG3_PCT_Diff
            FROM GameLogs
            INNER JOIN PlayerProfiles
            ON GameLogs.Player_ID = PlayerProfiles.Player_ID 
            WHERE GameLogs.Opponent=? AND GameLogs.Season_ID=? AND PlayerProfiles.Main_Position="Center"
            '''
            myresult = c.execute(sql, (Abbreviation, seasonID)).fetchall()
            C_Avg_Points_Diff, C_Q1_Points_Diff, C_Q3_Points_Diff, C_STDEV_Points_Diff, C_Avg_Rebound_Diff, C_Q1_Rebound_Diff, C_Q3_Rebound_Diff, C_STDEV_Revound_Diff, C_Avg_Assists_Diff, C_Q1_Assist_Diff, C_Q3_Assist_Diff, C_STDEV_Assist_Diff, C_Avg_FGA_Diff, C_Avg_FGM_Diff, C_Avg_FG_PCT_Diff, C_Avg_FG3A_Diff, C_Avg_FG3M_Diff, C_Avg_FG3_PCT_Diff = averages_and_iqr(myresult)

        
            c.execute('''INSERT INTO Team_Opp_Position_Stats 
                      (
                      TeamID, Seaon_Year, Season_ID, 
                      G_Avg_Points_Diff, G_Q1_Points_Diff, G_Q3_Points_Diff, G_STDEV_Points_Diff, 
                      G_Avg_Rebound_Diff, G_Q1_Rebound_Diff, G_Q3_Rebound_Diff, G_STDEV_Revound_Diff, 
                      G_Avg_Assists_Diff, G_Q1_Assist_Diff, G_Q3_Assist_Diff, G_STDEV_Assist_Diff, 
                      G_Avg_FGA_Diff, G_Avg_FGM_Diff, G_Avg_FG_PCT_Diff, G_Avg_FG3A_Diff, G_Avg_FG3M_Diff, G_Avg_FG3_PCT_Diff, 
                      F_Avg_Points_Diff, F_Q1_Points_Diff, F_Q3_Points_Diff, F_STDEV_Points_Diff, 
                      F_Avg_Rebound_Diff, F_Q1_Rebound_Diff, F_Q3_Rebound_Diff, F_STDEV_Rebound_Diff, 
                      F_Avg_Assists_Diff, F_Q1_Assist_Diff, F_Q3_Assist_Diff, F_STDEV_Assist_Diff, 
                      F_Avg_FGA_Diff, F_Avg_FGM_Diff, F_Avg_FG_PCT_Diff ,F_Avg_FG3A_Diff, F_Avg_FG3M_Diff, F_Avg_FG3_PCT_Diff, 
                      C_Avg_Points_Diff, C_Q1_Points_Diff, C_Q3_Points_Diff, C_STDEV_Points_Diff, 
                      C_Avg_Rebound_Diff, C_Q1_Rebound_Diff, C_Q3_Rebound_Diff, C_STDEV_Rebound_Diff, 
                      C_Avg_Assists_Diff, C_Q1_Assist_Diff, C_Q3_Assist_Diff, C_STDEV_Assist_Diff, 
                      C_Avg_FGA_Diff, C_Avg_FGM_Diff, C_Avg_FG_PCT_Diff, C_Avg_FG3A_Diff, C_Avg_FG3M_Diff, C_Avg_FG3_PCT_Diff
                      ) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (
                          TeamID, season, seasonID, 
                          G_Avg_Points_Diff, G_Q1_Points_Diff, G_Q3_Points_Diff, G_STDEV_Points_Diff, 
                          G_Avg_Rebound_Diff, G_Q1_Rebound_Diff, G_Q3_Rebound_Diff, G_STDEV_Revound_Diff, 
                          G_Avg_Assists_Diff, G_Q1_Assist_Diff, G_Q3_Assist_Diff, G_STDEV_Assist_Diff, 
                          G_Avg_FGA_Diff, G_Avg_FGM_Diff, G_Avg_FG_PCT_Diff, G_Avg_FG3A_Diff, G_Avg_FG3M_Diff, G_Avg_FG3_PCT_Diff,
                          F_Avg_Points_Diff, F_Q1_Points_Diff, F_Q3_Points_Diff, F_STDEV_Points_Diff, 
                          F_Avg_Rebound_Diff, F_Q1_Rebound_Diff, F_Q3_Rebound_Diff, F_STDEV_Revound_Diff, 
                          F_Avg_Assists_Diff, F_Q1_Assist_Diff, F_Q3_Assist_Diff, F_STDEV_Assist_Diff, 
                          F_Avg_FGA_Diff, F_Avg_FGM_Diff, F_Avg_FG_PCT_Diff, F_Avg_FG3A_Diff, F_Avg_FG3M_Diff, F_Avg_FG3_PCT_Diff,
                          C_Avg_Points_Diff, C_Q1_Points_Diff, C_Q3_Points_Diff, C_STDEV_Points_Diff, 
                          C_Avg_Rebound_Diff, C_Q1_Rebound_Diff, C_Q3_Rebound_Diff, C_STDEV_Revound_Diff, 
                          C_Avg_Assists_Diff, C_Q1_Assist_Diff, C_Q3_Assist_Diff, C_STDEV_Assist_Diff, 
                          C_Avg_FGA_Diff, C_Avg_FGM_Diff, C_Avg_FG_PCT_Diff, C_Avg_FG3A_Diff, C_Avg_FG3M_Diff, C_Avg_FG3_PCT_Diff
                        )
                    )


    conn.commit()
    conn.close()
    return

def Create_Team_GameLogs():
    #get each gaemlog vs eash team
    file_path = os.path.join('database','main.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Team_Game_Logs")
    table = """ CREATE TABLE Team_Game_Logs (
                TeamID CHAR(25) NOT NULL,
                GameID VARCHAR(255) NOT NULL,
                GameDate DATE NOT NULL,
                Opp VARCHAR(3) NOT NULL,
                Points FLOAT(3, 1) NOT NULL,
                Rebounds FLOAT(3, 1) NOT NULL,
                Assists FLOAT(3, 1) NOT NULL,
                FGA FLOAT(3, 1) NOT NULL,
                FGM FLOAT(3, 1) NOT NULL,
                FG_PCT FLOAT(3, 1) NOT NULL,
                FG3A FLOAT(3, 1) NOT NULL,
                FG3M FLOAT(3, 1) NOT NULL,
                FG3_PCT FLOAT(3, 1) NOT NULL,
                FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
            ); """
    c.execute(table)

    teamList = c.execute("SELECT TeamID FROM Teams").fetchall()
    #teamList = teamList[:2]
    for team in teamList:
        teamID = team[0]
        gamelogs = teamgamelog.TeamGameLog(team_id=teamID)
        gamelogs = gamelogs.get_dict()
        print(gamelogs)
        gamelogs = gamelogs.get('resultSets')[0].get('rowSet')
        for game in gamelogs:
            game_ID = game[1]
            game_date = game[2]
            actual_date = convertDate(game_date)
            matchup = game[3]
            opp = matchup.split(" ")[2]
            fgm = game[9]
            fga = game[10]
            fg_pct = game[11]
            fg3m = game[12]
            fg3a = game[13]
            fg3_pct = game[14]
            reb = game[20]
            ast = game[21] 
            pts = game[26]

            c.execute(''' INSERT INTO Team_Game_Logs (TeamID, GameID, GameDate, Opp, Points, Rebounds, Assists ,FGA, FGM, FG_PCT, FG3A, FG3M, FG3_PCT)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (teamID, game_ID, actual_date, opp, pts, reb, ast, fga, fgm, fg_pct, fg3a, fg3m, fg3_pct))
    conn.commit()
    conn.close()
    