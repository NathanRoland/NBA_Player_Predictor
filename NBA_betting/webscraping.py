import requests
import urllib3
#import schedule
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from urllib.request import Request, urlopen

markets = ['Player Points Markets', 'Player Rebounds Markets', 'Player Assists Markets', 'Player Three Point Markets', 'Player Points, Rebounds and Assists Markets', 'Player Points and Rebounds Markets', 'Player Points and Assists Markets', 'Player Rebounds and Assists Markets']
ladbrokes_markets = ['Player Performance Markets', 'Player Points Markets', 'Player Rebounds Markets', 'Player Assists Markets', 'Player Threes Markets']
pointsbet_markets = ['Points', 'Assists', 'Threes', 'Rebounds', 'Points + Rebounds + Assists', 'Points + Assists', 'Points + Rebounds', 'Assists + Rebounds']
def webscrape_test():
    r = requests.get('https://www.geeksforgeeks.org/python-programming-language/')
    print(r)

    soup = BeautifulSoup(r.content, 'html.parser')
    print(soup.prettify())

    s = soup.find('div', class_='entry-content')
    content = soup.find_all('p')
    print(content)


#sportsbet'
def get_games():
    r = requests.get("https://www.sportsbet.com.au/betting/basketball-us/nba")
    soup = BeautifulSoup(r.content, 'html.parser')
    content_div = soup.find("div", class_='content_fso6rhz')
    matches_container = content_div.find(attrs={'class':"", 'data-automation-id':'competition-matches-container'})
    matches = matches_container.find_all('div')[0]
    print((matches.find('time', class_='timeText_f1bxfcjc')).text.strip())
    list = matches.find('ul')
    games = list.find_all('li')
    all_links = []
    all_games = []
    games_num = 0
    for game in games:
        game_list = []
        link_container = game.find('a', class_='linkMultiMarket_fcmecz0')
        all_links.append(link_container.get('href'))
        teams = game.find('div', class_='participantContainer_fkhz08q')
        two_teams = teams.find_all('div', class_='participantRow_fklqmim')
        fixture_string = (str(games_num)+'. ')
        for team in two_teams:
            game_list.append(team.find('div', class_="size14_f7opyze Endeavour_fhudrb0 medium_f1wf24vo participantText_fivg86r").text.strip())
            fixture_string += team.find('div', class_="size14_f7opyze Endeavour_fhudrb0 medium_f1wf24vo participantText_fivg86r").text.strip() + " vs "
        games_num += 1
        print(fixture_string[:-4])
        all_games.append(game_list[::-1])
    return all_links, all_games

def sportsbet_webscrape(link):
    all_markets = {}
    driver = webdriver.Chrome()
    driver.get('https://www.sportsbet.com.au' + str(link))
    elements = driver.find_elements(By.XPATH, "//div[@class='marketGroupings_fc8wfj0']")
    for element in elements:
        try:
            driver.implicitly_wait(0.8)
            market_name = element.find_element(By.XPATH, ".//span[@class='SF_PRO_BLD_14_16_fpqs91j TextNormal_f1vshw8n oneLine_f15ay66x']")
            if market_name.get_attribute('innerHTML') in markets:
                official_market_name = market_name.get_attribute('innerHTML')
                #all_markets[market_name.get_attribute('innerHTML')] = {}
                element.click()
                all_individual_markets = element.find_elements(By.XPATH, ".//div[@class='content_f1sk4ot6 divider_ffir01h']")
                for player_market in all_individual_markets:
                    try:
                        player_market_name = player_market.find_element(By.XPATH, ".//span[@class='SF_PRO_BLD_12_16_f19gvpxj TextNormal_f1vshw8n oneLine_f15ay66x']")
                        player_market.click()
                        line = player_market.find_element(By.XPATH, ".//span[@class='SF_PRO_REG_12_16_ftl08fn TextNormal_f1vshw8n']")
                        if line.get_attribute('innerHTML') != "Pick" and "1st Qtr Points" not in player_market_name.get_attribute('innerHTML') and "Top Points Scorer" not in player_market_name.get_attribute('innerHTML'):
                            #print(player_market_name.get_attribute('innerHTML'))
                            #print(line.get_attribute('innerHTML'))
                            player_name = player_market_name.get_attribute('innerHTML').split(' -')[0]
                            player_line = (line.get_attribute('innerHTML')).split('+')[1].replace(")","")
                            odds = player_market.find_elements(By.XPATH, ".//span[@class='size14_f7opyze bold_f1au7gae priceTextSize_frw9zm9']")
                            above = odds[0].get_attribute('innerHTML')
                            below = odds[1].get_attribute('innerHTML')
                            if player_name not in all_markets:
                                all_markets[player_name] = {}
                            all_markets[player_name][official_market_name] = {'player_line': player_line, 'above': above, 'below': below} 
                            #print(official_market_name + " : " + player_name + " - " + player_line, above, below)
                    except:
                        next     
                
                last_markets = element.find_elements(By.XPATH, ".//div[@class='contentWithRoundedBottomBorders_fm4pkx']")
                for last_market in last_markets:
                    try:
                        
                        player_market_name = last_market.find_element(By.XPATH, ".//span[@class='SF_PRO_BLD_12_16_f19gvpxj TextNormal_f1vshw8n oneLine_f15ay66x']")
                        last_market.click()
                        line = last_market.find_element(By.XPATH, ".//span[@class='SF_PRO_REG_12_16_ftl08fn TextNormal_f1vshw8n']")
                        if line.get_attribute('innerHTML') != "Pick" and "1st Qtr Points" not in player_market_name.get_attribute('innerHTML') and "Top Points Scorer" not in player_market_name.get_attribute('innerHTML'):
                            #print(player_market_name.get_attribute('innerHTML'))
                            #print(line.get_attribute('innerHTML'))
                            player_name = player_market_name.get_attribute('innerHTML').split(' -')[0]
                            player_line = (line.get_attribute('innerHTML')).split('+')[1].replace(")","")
                            odds = player_market.find_elements(By.XPATH, ".//span[@class='size14_f7opyze bold_f1au7gae priceTextSize_frw9zm9']")
                            above = odds[0].get_attribute('innerHTML')
                            below = odds[1].get_attribute('innerHTML')
                            if player_name not in all_markets:
                                all_markets[player_name] = {}
                            all_markets[player_name][official_market_name] = {'player_line': player_line, 'above': above, 'below': below} 
                            #print(official_market_name + " : " + player_name + " - " + player_line, above, below)
                    except:
                        next   
        except:
            print('sorry')
    #wait = WebDriverWait(driver, 10)
    #element = wait.until(EC.visibility_of_element_located((By.ID, "element_id")))
    driver.quit()
    return all_markets

#ladbrokes

def ladbrokes_webscrape():
    driver = webdriver.Chrome()
    driver.get("https://www.ladbrokes.com.au/sports/basketball/usa/nba/new-york-knicks-vs-san-antonio-spurs/0a05b36f-5691-4de5-b014-a0446fd428d0")
    driver.implicitly_wait(0.5)
    main_page = driver.find_element(By.XPATH, "//div[@class='event-card']")
    elements = main_page.find_elements(By.XPATH, ".//div[@class='market-group']")

    three_point_market = {}
    #print(elements.get_attribute('innerHTML'))
    for element in elements:
        try:
            driver.implicitly_wait(0.5)
            market_name = (element.find_element(By.XPATH, ".//div/h3/span")).get_attribute('innerHTML').split(' (')[0]
            if market_name in ladbrokes_markets:
                element.click()
                player_markets = element.find_elements(By.XPATH, ".//div[@class='market-two-col terminal:mb-3 terminal:last:mb-0']")
                for player_market in player_markets:
                    player_name = player_market.find_element(By.XPATH, ".//span[@class='capitalize']")
                    if '+' in player_name.get_attribute('innerHTML') and 'Three' not in player_name.get_attribute('innerHTML'):
                        next
                    elif '+' in player_name.get_attribute('innerHTML') and 'Three' in player_name.get_attribute('innerHTML'):
                        
                        amount = float(player_name.get_attribute('innerHTML').split('+')[0].split(" ")[-1])
                        player_market.click()
                        Three_point_player_market = player_market.find_elements(By.XPATH, ".//div[@class='market-two-col__entrant']")
                        for player in Three_point_player_market:
                            actual_player_name_unedit = player.find_element(By.XPATH, ".//span[@class='market-two-col__entrant-name tabnz-sst:!text-lg tabnz-sst:!font-normal']")
                            actual_player_name = (actual_player_name_unedit.get_attribute('innerHTML')).split(' (')[0]
                            line = float(player.find_element(By.XPATH, ".//div[@class='price-button-odds-price']/span").get_attribute('innerHTML'))
                            if actual_player_name in three_point_market:
                                new_diff = abs(line - 2)
                                cur_diff = abs(three_point_market.get(actual_player_name)[1] - 2)
                                if new_diff < cur_diff:
                                    three_point_market[actual_player_name] = [amount, line]
                            else:
                                three_point_market[actual_player_name] = [amount, line]
                    else:
                        print(player_name.get_attribute('innerHTML'))
                        actual_player_name = (player_name.get_attribute('innerHTML')).split('- ')[1].split(' (')[0]
                        points_line = (player_name.get_attribute('innerHTML')).split('(')[1].replace(")", "")
                        odds = player_market.find_elements(By.XPATH, ".//div[@class='price-button-odds-price']/span")
                        over = odds[0].get_attribute('innerHTML')
                        under = odds[1].get_attribute('innerHTML')
                        player_market.click()
                        #print(actual_player_name + ': ' + points_line + ' over: ' + over, 'under: ' + under)
        except:
            print('failed scraping')
    print(three_point_market)
    print('finished')
    driver.quit()

#tab

def pointsbet_webscrape():
    driver = webdriver.Chrome()
    driver.get("https://pointsbet.com.au/sports/basketball/NBA/2054501")
    #driver.implicitly_wait(0.5)
    #players = driver.find_elements(By.XPATH, "//div[@class='fa2dl2e']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='fgl61z2']")))
    players = driver.find_elements(By.XPATH, "//div[@class='fa2dl2e']")

    for player in players:
        driver.implicitly_wait(0.5)
        player_name = player.find_element(By.XPATH, ".//p[@class='fclohlv f909g20']").get_attribute('innerHTML')
        if player_name == 'Points':
            break
        print(player_name)
        button = player.find_element(By.XPATH, ".//button[@class='fi57b6']")
        button.click()
        print('test done')

    driver.quit()

#scrape from nba injury report

#scrape from espn
def espn_injury_scrape():
    url="https://stackoverflow.com/search?q=html+error+403"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    web_byte = urlopen(req).read()

    webpage = web_byte.decode('utf-8')
    print(webpage)
    r = requests.get('https://www.espn.com.au/nba/injuries')
    soup = BeautifulSoup(r.content, 'html.parser')
    injuries = {}
    print(r)
    s = soup.find_all('div', class_="ResponsiveTable Table__league-injuries")
    for team in s:
        print(team)




#scrape minutes predictions
def mins_projector():
    #daily link = https://www.fanduel.com/research/nba/fantasy/dfs-projections
    r = requests.get("https://www.fanduel.com/research/nba/fantasy/dfs-projections")
    soup = BeautifulSoup(r.content, 'html.parser')
    overall_mins = {}
    div_set = soup.find('div', class_="projectionsContainer_tableContainer__d8Mba")
    print(div_set)
    table = div_set.find('table', class_="tableStyles_vtable__iACEt")
    body = table.find('tbody', class_="tableStyles_vtbody__Tj_Pq")
    rows = body.find_all('tr')
    for row in rows:
        name = row.find('a', class_="full").text.strip()
        min = row.find('td', class_="min").text.strip()
        overall_mins[name] = min
    return overall_mins

def mins_projector_3():
    driver = webdriver.Chrome()
    driver.get("https://www.fanduel.com/research/nba/fantasy/dfs-projections")
    #driver.implicitly_wait(0.5)
    #players = driver.find_elements(By.XPATH, "//div[@class='fa2dl2e']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//table[@class='tableStyles_vtable__iACEt']")))
    overall_mins = {}
    table = driver.find_element(By.XPATH, "//table[@class='tableStyles_vtable__iACEt']")
    body = table.find_element(By.XPATH, "//tbody[@class='tableStyles_vtbody__Tj_Pq']") 
    rows = body.find_elements(By.XPATH, "//tr")
    for row in rows:
        name = row.find_element(By.XPATH,"//div[@class='PlayerCell_nameLinkText__P3INe']").get_attribute('innerHTML')
        print(name)
        min = row.find_elements(By.XPATH, "//td[@class='tableStyles_vtd__HAZr4']")[3].get_attribute('innerHTML')
        print(min)
        overall_mins[name] = min
    return overall_mins


def mins_projector_2():
    r = requests.get("https://www.sportsline.com/nba/expert-projections/simulation/")
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('table', class_="sc-36594fa2-7 ZvKHg")
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    overall_mins = {}
    for row in rows:
        name = row.find('td', class_="sc-36594fa2-6 dVyafO first-column").text.strip()
        mins = row.find_all('td', class_="sc-36594fa2-6 dVyafO column")[8].text.strip()
        overall_mins[name] = mins
    return overall_mins

def get_projected_lineups():
    #link https://basketballmonster.com/nbalineups.aspx
    r = requests.get("https://basketballmonster.com/nbalineups.aspx")
    soup = BeautifulSoup(r.content, 'html.parser')
    games = soup.find_all('div', class_="container-fluid p-2 m-2 float-left")
    for game in games:
        head = game.find('thead')

        team_headings = head.find_all('tr')[1]
        teams = team_headings.find_all('th')
        home_team = teams[2].text.strip().replace("@ ", "")
        away_team = teams[1].text.strip()

        rows = game.find_all('tr')[2::]
        print(home_team, away_team)
        for row in rows:
            elements = row.find_all('td')
            position = elements[0].text.strip()
            home_player = elements[2]
            home_inj = None
            away_inj = None
            if home_player.find('span', class_="status-square"):
                home_inj = home_player.find('span', class_="status-square").text.strip()
                home_player_text = elements[2].find('a').text.strip()
            else:
                home_player_text = elements[2].text.strip()
            away_player = elements[1]
            if away_player.find('span', class_="status-square"):
                away_inj = away_player.find('span', class_="status-square").text.strip()
                away_player_text = elements[1].find('a').text.strip()
            else:
                away_player_text = elements[1].text.strip()
            print(position, home_player_text, home_inj, away_player_text, away_inj)
        



#old

def old_webscrape():

    markets_all = {}
    r = requests.get('https://www.sportsbet.com.au/betting/basketball-us/nba/detroit-pistons-at-boston-celtics-8770759')
    soup = BeautifulSoup(r.content, 'html.parser')
    t = soup.find('div', class_="roundBottomBorder_f87wm2u")
    print(t.text)
    s = soup.find_all('div', class_="accordion_fub39zu")
    for group in s:
        break
        name = group.find('span', class_='SF_PRO_BLD_14_16_fpqs91j TextNormal_f1vshw8n oneLine_f15ay66x')
        if name.text in markets:
            testing_text = group.find('div', class_='roundBottomBorder_f87wm2u')
            print(group)
            markets_all[name.text] = get_sb_Markets(group)
    print(len(t))
    print(len(s))
    
    #bets_list = s.find('div', class_="roundBottomBorder_f87wm2u")
    #dame_list = bets_list.find('div', class_="content_f1sk4ot6 divider_ffir01h")
    #print(dame_list.prettify())
    #3 is points, 4 is rebounds, 5 is assists, 6 is 3point, 7 is pra, 8 is pr, 9 is pa, 10 is ra
    points = s[3]
    rebounds = s[4]
    assists = s[5]
    three_points = s[6]
    pra = s[7]
    pr = s[8]
    pa = s[9]
    ra = s[10]
 #content_f1sk4ot6 divider_ffir01h
    # accordion_fub39zu - 

def get_sb_Markets(bet_market):
    #print(bet_market)
    dictionary = {}
    #dict example = {player_name: {line: 30.5, odds:[over, under]}, }
    specific_markets = bet_market.find_all('div', class_='content_f1sk4ot6 divider_ffir01h')
    for player_market in specific_markets:
        player_name = player_market.find('span', class_='SF_PRO_BLD_12_16_f19gvpxj TextNormal_f1vshw8n oneLine_f15ay66x')
        #print(player_name)

def test_func():
    print("this is a test")

def continuousLoop():
    schedule.every(1).minutes.do(test_func)
    while True:
        schedule.run_pending()
        time.sleep(1)
    