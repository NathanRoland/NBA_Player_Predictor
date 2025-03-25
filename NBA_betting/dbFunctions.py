import os
import sqlite3
from datetime import date
from datetime import datetime

def getTeams(team):
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    sql = """ SELECT * FROM Teams WHERE Abbreviation=? OR TeamID=? """
    team_info = c.execute(sql, (team, team)).fetchall()
    conn.close()
    return team_info

def getHomeTeam(gameID):
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    sql = """ SELECT homeTeamID FROM Fixtures WHERE gameID=? """
    team_info = c.execute(sql, (gameID,)).fetchall()
    conn.close()
    return team_info

def getAwayTeam(gameID):
    file_path = os.path.join('database','main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    sql = """ SELECT awayTeamID FROM Fixtures WHERE gameID=? """
    team_info = c.execute(sql, (gameID,)).fetchall()
    conn.close()
    return team_info


def getTeamPlayers(team):
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    sql = """ SELECT * FROM PlayerProfiles WHERE TeamID=?"""
    teamPlayers = c.execute(sql, (team,)).fetchall()
    conn.close()
    return teamPlayers

def getPlayerIDName(playerID):
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    sql = """ SELECT * FROM PlayerProfiles WHERE Player_ID=?"""
    player = c.execute(sql, (playerID,)).fetchall()
    conn.close()
    return player

def getPlayerDeets(playerID):
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    sql = """ SELECT * FROM PlayerProfiles WHERE Player_ID=?"""
    player = c.execute(sql, (playerID,)).fetchall()
    conn.close()
    return player

def getPlayerID(name):
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    sql = """ SELECT Player_ID FROM PlayerProfiles WHERE Player_Name=?"""
    player = c.execute(sql, (name,)).fetchall()
    conn.close()
    return player

def getGameID(homeTeam, AwayTeam):
    file_path = os.path.join('database', 'main2024.db')
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    homeTeamID = c.execute("SELECT TeamID FROM Teams WHERE Team_Name = ?", (homeTeam,)).fetchall()[0][0]
    awayTeamID = c.execute("SELECT TeamID FROM Teams WHERE Team_Name = ?", (AwayTeam,)).fetchall()[0][0]
    sql = """ SELECT gameDate FROM Fixtures WHERE homeTeamID=? AND awayTeamID = ?"""
    games = c.execute(sql, (homeTeamID, awayTeamID,)).fetchall()
    today = date.today()
    gamedates = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in games]
    res = min(gamedates, key=lambda sub: abs(sub - today))
    gameID = c.execute("SELECT gameID FROM Fixtures WHERE homeTeamID=? AND awayTeamID = ? AND gameDate=?", (homeTeamID, awayTeamID, res,)).fetchall()[0]
    conn.close()
    return gameID