import requests

API_KEY = 'da4a3b7c861165fee16c30e3720aaf38'
EventID = 12

def getPlayerOdds():

    #sports_response = requests.get(
     #   'https://api.the-odds-api.com/v4/sports', 
      #  params={
       #     'api_key': API_KEY
        #}
    #)

    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/
    {EventID}/odds?apiKey={API_KEY}&regions=au&markets=player_points&oddsFormat=decimal')
