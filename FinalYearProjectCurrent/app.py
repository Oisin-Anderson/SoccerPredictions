from unittest import result
from flask import Flask, render_template, request
from export import exteams, exfixtures
from h2h import h2hscraping, h2hpredictions, h2hdata
from h2hleague import hlscraping, hlpredictions, hldata
from minileague import mleagueFixtures, mleaguePredictions, mleagueResults, mleagueDisplay
from fullleague import fleagueFixtures, fleaguePredictions, fleagueResults, fleagueDisplay, fleagueTeams
from testing import testMatches, testTail, testPredictions, testDirPredictions, testDirect, saveTest
import csv
import pandas as pd
import datetime

app = Flask(__name__)

#Home Page Loads
@app.route('/')
def home():
    return render_template('home.html')

#About Page Loads
@app.route('/about')
def about():
    return render_template('about.html')

#League Menu Page Loads
@app.route('/leaguepage', methods=['POST'])
def lpage():
    league = request.form['league']
    
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        date = row["Date"]
        sleague = row["StorLeague"]

    with open('FinalYearProjectCurrent/store/leagueName.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['CurLeague', 'StorLeague', 'Date']
        writer.writerow(header)
        line = [league, sleague, date]
        writer.writerow(line)

    seasons = ["2021"]

    clubs = fleagueTeams(league, seasons)
    length = len(clubs)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == ' ':
                text = text + '_'
            else:
                text = text + temp[i]
        clubs[j] = text
    
    clubs.sort()
    print(clubs)

    return render_template('leaguepage.html', cleague=league, clubs=clubs, length=length, date=date, sleague=sleague)

#Back To League Menu Page Loads
@app.route('/backleaguepage', methods=['POST'])
def blpage():    
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]
        sleague = row["StorLeague"]
        date = row["Date"]

    seasons = ["2021"]

    clubs = fleagueTeams(league, seasons)
    length = len(clubs)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == ' ':
                text = text + '_'
            else:
                text = text + temp[i]
        clubs[j] = text
    
    clubs.sort()
    print(clubs)

    return render_template('leaguepage.html', cleague=league, clubs=clubs, length=length, date=date, sleague=sleague)

#H2H Menu Page Loads
@app.route('/headpage', methods=['POST'])
def hpage():
    league = request.form['league']
    
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        date = row["Date"]
        sleague = row["StorLeague"]

    with open('FinalYearProjectCurrent/store/leagueName.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['CurLeague', 'StorLeague', 'Date']
        writer.writerow(header)
        line = [league, sleague, date]
        writer.writerow(line)
    
    seasons = ["2021"]
    clubs = fleagueTeams(league, seasons)
    length = len(clubs)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == ' ':
                text = text + '_'
            else:
                text = text + temp[i]
        clubs[j] = text
    
    clubs.sort()
    print(clubs)
    return render_template('headpage.html', league=league, clubs=clubs, length=length)


#Testing Direct H2H
@app.route('/testing', methods=['POST'])
def testing():
    option = request.form['option']
    league = request.form['league']


    testMatches(league)
    hteams, ateams, tail = testTail()
    predict = []
    head = ""
    if option == "Direct":
        head = league + " Direct Last 20 Fixture Comparison"
        for i in range(len(hteams)):
            hteam = hteams[i]
            ateam = ateams[i]
            home, away, hgoals, agoals = testDirect(hteam, ateam, league)
            with open('FinalYearProjectCurrent/store/testFixtures.csv', 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                header = ['homeTeam', 'awayTeam', 'homeGoals', 'awayGoals']
                writer.writerow(header)
                for j in range(len(home)):
                    line = [home[j], away[j], hgoals[j], agoals[j]]
                    writer.writerow(line)
            temp = testDirPredictions(hteam, ateam)
            predict.append(temp)  
    elif option == "League":
        head = league + " League Last 20 Fixture Comparison"
        predict = testPredictions(hteams, ateams)
    elif option == "preDirect":
        head = league + " Direct Last 20 Fixture Comparison"
        df = pd.read_csv("FinalYearProjectCurrent/store/testDirect.csv")
        for idx, row in df.iterrows():
            predict.append(row["Predict"])
    elif option == "preLeague":
        head = league + " League Last 20 Fixture Comparison"
        df = pd.read_csv("FinalYearProjectCurrent/store/testLeague.csv")
        for idx, row in df.iterrows():
            predict.append(row["Predict"])

    saveTest(option, predict)

    result = []
    for idx, row in tail.iterrows():
        result.append(row["Result"])
    length = len(hteams)

    correct = []
    count = 0
    for i in range(len(hteams)):
        if result[i] == predict[i]:
            count += 1
            correct.append(count)
        else:
            correct.append(count)

    return render_template('testing.html', header=head, hteams=hteams, ateams=ateams, result=result, predict=predict, length=length, correct=correct)

#Back To H2H Menu Page
@app.route('/backheadpage', methods=['POST'])
def bhpage():
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]
    
    seasons = ["2021"]
    clubs = fleagueTeams(league, seasons)
    length = len(clubs)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == ' ':
                text = text + '_'
            else:
                text = text + temp[i]
        clubs[j] = text
    
    clubs.sort()
    print(clubs)
    return render_template('headpage.html', league=league, clubs=clubs, length=length)


#H2H Menu Page Loads
@app.route('/exportpage', methods=['POST'])
def epage():
    league = request.form['league']
    
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        date = row["Date"]
        sleague = row["StorLeague"]

    with open('FinalYearProjectCurrent/store/leagueName.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['CurLeague', 'StorLeague', 'Date']
        writer.writerow(header)
        line = [league, sleague, date]
        writer.writerow(line)

    seasons = ['2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
    clubs = fleagueTeams(league, seasons)
    clength = len(clubs)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == ' ':
                text = text + '_'
            else:
                text = text + temp[i]
        clubs[j] = text
        
    clubs.sort()

    slength = len(seasons)
    return render_template('export.html', league=league, seasons=seasons, slength=slength, clubs=clubs, clength=clength)

#Back To H2H Menu Page
@app.route('/backexportpage', methods=['POST'])
def bepage():
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]

    seasons = ['2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
    clubs = fleagueTeams(league, seasons)
    clength = len(clubs)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == ' ':
                text = text + '_'
            else:
                text = text + temp[i]
        clubs[j] = text
        
    clubs.sort()

    slength = len(seasons)
    return render_template('export.html', league=league, seasons=seasons, slength=slength, clubs=clubs, clength=clength)


#Exports Fixture Data to CSV
@app.route('/fixtures', methods=['POST'])
def fixtures():
    league = ""
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]

    season = request.form['season']
    
    dates, home, hgoals, away, agoals, played, result = exfixtures(league, season)
    length = len(dates)

    header = "All " + season + " " + league + " season fixtures"
        
    return render_template('fixtures.html', length=length, header=header, dates=dates, home=home, hgoals=hgoals, away=away, agoals=agoals, played=played, result=result)

#Exports Teams Data to CSV
@app.route('/teams', methods=['POST'])
def teams():
    league = ""
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]

    team = request.form['team']

    temp = team
    text = ""
    for i in range(len(temp)):
        if temp[i] == '_':
            text = text + ' '
        else:
            text = text + temp[i]
    team = text

    seasons = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"]
    
    exteams(league, seasons, team)
    clubs, games, wins, draws, loses, gfor, gagainst, gdiff, points = mleagueDisplay()
    pos = []
    for i in range(len(clubs)):
        pos.append(i + 1)

    league = team + " Table All Seasons"
    length = len(clubs)

    return render_template('league.html', league=league, length=length, pos=pos, clubs=clubs, games=games, wins=wins, draws=draws, loses=loses, gfor=gfor, gagainst=gagainst, gdiff=gdiff, points=points)

#Head To Head match predcitions
@app.route('/headPred', methods=['POST'])
def headPred():

    team1 = request.form['team1']
    team2 = request.form['team2']

    if team1 == team2:
        message = "Same team selected for both"
        return render_template('error.html', message=message)
    league = ""
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]

    clubs = []
    clubs.append(team1)
    clubs.append(team2)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == '_':
                text = text + ' '
            else:
                text = text + temp[i]
        clubs[j] = text

    team1 = clubs[0]
    team2 = clubs[1]

    h2hscraping(team1, team2, league)

    odds = h2hpredictions(team1, team2)

    draw, win, loss, predict, h, a, scores = h2hdata(odds)
    print("Home Team is Vertical")
    print(team1)
    print("Away Team is Horizontal")
    print(team2)
    print(odds)

    return render_template('h2h.html', win=win, draw=draw, loss=loss, predict=predict, hteam=team1, ateam=team2, h=h, a=a, odds=scores)


#Head To Head match predcitions
@app.route('/headleagPred', methods=['POST'])
def headleagPred():

    team1 = request.form['team1']
    team2 = request.form['team2']

    if team1 == team2:
        return render_template('error.html')
    league = ""
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]

    clubs = []
    clubs.append(team1)
    clubs.append(team2)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == '_':
                text = text + ' '
            else:
                text = text + temp[i]
        clubs[j] = text

    team1 = clubs[0]
    team2 = clubs[1]

    hlscraping(team1, team2, league)

    odds = hlpredictions(team1, team2)

    draw, win, loss, predict, h, a, scores = hldata(odds)
    print("Home Team is Vertical")
    print(team1)
    print("Away Team is Horizontal")
    print(team2)
    print(odds)

    return render_template('h2h.html', win=win, draw=draw, loss=loss, predict=predict, hteam=team1, ateam=team2, h=h, a=a, odds=scores)

#MiniLeaguePrediction
@app.route('/miniLeague', methods=['POST', 'GET'])
def miniLeague():
    league = ""
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        league = row["CurLeague"]
    
    clubs = request.form.getlist('mini')

    if len(clubs) < 6:
        message = "Please select atleast 6 teams for an accurate prediction"
        return render_template('error.html', message=message)

    for j in range(len(clubs)):
        temp = clubs[j]
        text = ""
        for i in range(len(temp)):
            if temp[i] == '_':
                text = text + ' '
            else:
                text = text + temp[i]
        clubs[j] = text
    
    hside = clubs
    aside = clubs
    mleagueResults(league, hside, aside)
    mleagueFixtures(hside, aside)
    mleaguePredictions(hside)
    clubs, games, wins, draws, loses, gfor, gagainst, gdiff, points = mleagueDisplay()
    pos = []
    for i in range(len(clubs)):
        pos.append(i + 1)

    league = league + " Mini League Prediction"

    length = len(clubs)

    return render_template('league.html', league=league, length=length, pos=pos, clubs=clubs, games=games, wins=wins, draws=draws, loses=loses, gfor=gfor, gagainst=gagainst, gdiff=gdiff, points=points)

#FullLeaguePrediction
@app.route('/fullLeague', methods=['POST'])
def fullLeague():
    cleague = ""
    df = pd.read_csv("FinalYearProjectCurrent/store/leagueName.csv")
    for idx, row in df.iterrows():
        cleague = row["CurLeague"]
        sleague = row["StorLeague"]
        date = row["Date"]
    options = request.form['floptions']


    if options == "whole":
        options = request.form['floptions']
        clubs, games, wins, draws, loses, gfor, gagainst, points = fleagueResults(cleague)
        fleagueFixtures(cleague)
        fleaguePredictions(clubs, games, wins, draws, loses, gfor, gagainst, points)
        date = datetime.datetime.now()
        for idx, row in df.iterrows():
            sleague = row["CurLeague"]

    clubs, games, wins, draws, loses, gfor, gagainst, gdiff, points = fleagueDisplay()
    pos = []
    for i in range(len(clubs)):
        pos.append(i + 1)

    head = "Final " + sleague + " Table Prediction"

    length = len(clubs)

    with open('FinalYearProjectCurrent/store/leagueName.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['CurLeague', 'StorLeague', 'Date']
        writer.writerow(header)
        line = [cleague, sleague, date]
        writer.writerow(line)


    return render_template('league.html', league=head, length=length, pos=pos, clubs=clubs, games=games, wins=wins, draws=draws, loses=loses, gfor=gfor, gagainst=gagainst, gdiff=gdiff, points=points)


if __name__ == '__main__':
    app.run()
