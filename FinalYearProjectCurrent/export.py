import sys
import requests
from bs4 import BeautifulSoup
import csv
import json

def exteams(league, seasons, team):

    with open('FinalYearProjectCurrent/store/leagueTally.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['Team', 'Played', 'Wins', 'Draws', 'Loses', 'GF', 'GA', 'GD', 'Points']
        writer.writerow(header)
        for i in range(len(seasons)):
            base_url = 'https://understat.com/league/'
            url = base_url +  league + '/' + seasons[i]

            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            scripts = soup.find_all('script')

            strings = scripts[1].string

            # print(strings)

            ind_start = strings.index("('") + 2
            ind_end = strings.index("')")
            json_data = strings[ind_start:ind_end]

            json_data = json_data.encode('utf8').decode('unicode_escape')

            data = json.loads(json_data)
            # print(data)

            played = 0
            point = 0
            gf = 0
            ga = 0
            gd = 0
            win = 0
            loss = 0
            draw = 0
            for index in range(len(data)):
                if data[index]['isResult'] is True:
                    h = int(data[index]['goals']['h'])
                    hteam = data[index]['h']['title']
                    ateam = data[index]['a']['title']
                    a = int(data[index]['goals']['a'])
                    if hteam == team:
                        played += 1
                        gf += h
                        ga += a
                        if h > a:
                            point += 3
                            win += 1
                        if h == a:
                            point += 1
                            draw += 1
                        if h < a:
                            point += 0
                            loss += 1
                    if ateam == team:
                        played += 1
                        gf += a
                        ga += h
                        if h < a:
                            point += 3
                            win += 1
                        if h == a:
                            point += 1
                            draw += 1
                        if h > a:
                            point += 0
                            loss += 1
            if point != 0:
                name = team + " " + seasons[i]
                gd = gf - ga  
                line = [name, played, win, draw, loss, gf, ga, gd, point]
                writer.writerow(line)

def exfixtures(league, season):
    dates = []
    home = []
    hgoals = []
    away = []
    agoals = []
    played = []
    result = []

    base_url = 'https://understat.com/league'
    url = base_url + '/' + league + '/' + season


    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    scripts = soup.find_all('script')

    strings = scripts[1].string

    # print(strings)

    ind_start = strings.index("('") + 2
    ind_end = strings.index("')")
    json_data = strings[ind_start:ind_end]

    json_data = json_data.encode('utf8').decode('unicode_escape')

    data = json.loads(json_data)

    #print(data)

    h = 0
    a = 0

    for index in range(len(data)):
        if data[index]['isResult'] is True:
            dates.append(data[index]['datetime'])
            home.append(data[index]['h']['title'])
            away.append(data[index]['a']['title'])
            h = int(data[index]['goals']['h'])
            a = int(data[index]['goals']['a'])
            hgoals.append(data[index]['goals']['h'])
            agoals.append(data[index]['goals']['a'])
            played.append("True")
            if h > a:
                result.append("H")
            if h == a:
                result.append("D")
            if h < a:
                result.append("A")
        
        if data[index]['isResult'] is False:
            dates.append(data[index]['datetime'])
            home.append(data[index]['h']['title'])
            away.append(data[index]['a']['title'])
            hgoals.append("-")
            agoals.append("-")
            played.append("False")
            result.append("TBP")
    return dates, home, hgoals, away, agoals, played, result
