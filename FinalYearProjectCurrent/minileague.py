import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
from scipy.stats import poisson
from scipy.optimize import minimize


def mleagueResults(league, hside, aside):
    with open('FinalYearProjectCurrent/store/leagResults.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['homeTeam', 'awayTeam', 'homeGoals', 'awayGoals']
        writer.writerow(header)
        base_url = 'https://understat.com/league/'
        url = base_url + league + '/2021'


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

        for index in range(len(data)):
            hTeam = data[index]['h']['title']
            aTeam = data[index]['a']['title']
            for i in range(len(hside)):
                if hside[i] == hTeam:
                    for p in range(len(aside)):
                        if aside[p] == aTeam:
                            if data[index]['isResult'] is True:
                                hGoals = int(data[index]['goals']['h'])
                                aGoals = int(data[index]['goals']['a'])
                                line = [hTeam, aTeam, hGoals, aGoals]
                                writer.writerow(line)

def mleagueFixtures(hside, aside):
    with open('FinalYearProjectCurrent/store/leagFixtures.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['homeTeam', 'awayTeam']
        writer.writerow(header)
        for i in range(len(hside)):
            for p in range(len(aside)):
                if hside[i] != aside[p]:
                    line = [hside[i], aside[p]]
                    writer.writerow(line)


def mleaguePredictions(hside):
    df = pd.read_csv('FinalYearProjectCurrent/store/leagResults.csv')
    print("Head")
    print(df.head())
    print("Tail")
    print(df.tail())
    print("Shape")
    print(df.shape)
    print("Columns")
    print(df.columns)

    #print(df[["homeGoals", "awayGoals"]].mean())

    def logLikelyHood(
        homeGoalsObserved,
        awayGoalsObserved,
        homeAttack,
        homeDefence,
        awayAttack,
        awayDefence,
        homeAdvantage,
    ):
        homeGoalExpectation = np.exp(homeAttack + awayDefence + homeAdvantage)
        awayGoalExpectation = np.exp(awayAttack + homeDefence)

        if homeGoalExpectation < 0 or awayGoalExpectation < 0:
            return 10000    

        homeLLK = poisson.pmf(homeGoalsObserved, homeGoalExpectation)
        awayLLK = poisson.pmf(awayGoalsObserved, awayGoalExpectation)

        logLLK = np.log(homeLLK) + np.log(awayLLK)

        return -logLLK






    def fitPoissonModel():
        teams = np.sort(np.unique(np.concatenate([df["homeTeam"], df["awayTeam"]])))
        noTeams = len(teams)

        parameters = np.concatenate(
            (
                np.random.uniform(0.5, 1.5, (noTeams)),  # attack strength
                np.random.uniform(0, -1, (noTeams)),  # defence strength
                [0.25],  # home advantage
            )
        )

        def _fit(parameters, df, teams):
            attParameter = dict(zip(teams, parameters[:noTeams]))
            defParameter = dict(zip(teams, parameters[noTeams : (2 * noTeams)]))
            homeAdvantage = parameters[-1]

            llk = []

            for idx, row in df.iterrows():
                tmp = logLikelyHood(
                    row["homeGoals"],
                    row["awayGoals"],
                    attParameter[row["homeTeam"]],
                    defParameter[row["homeTeam"]],
                    attParameter[row["awayTeam"]],
                    defParameter[row["awayTeam"]],
                    homeAdvantage,
                )
                llk.append(tmp)

            return np.sum(llk)

        options = {
            "maxiter": 100,
            "disp": False,
        }

        constraints = [{"type": "eq", "fun": lambda x: sum(x[:noTeams]) - noTeams}]

        res = minimize(
            _fit,
            parameters,
            args=(df, teams),
            constraints=constraints,
            options=options,
        )

        modelParameters = dict(
            zip(
                ["attack_" + team for team in teams]
                + ["defence_" + team for team in teams]
                + ["homeAdv"],
                res["x"],
            )
        )

        return modelParameters

    modelParameters = fitPoissonModel()

    print(modelParameters)

    def predict(home_team, away_team, parameters, maxGoals):
        homeAttack = parameters["attack_"+home_team]
        homeDefence = parameters["defence_"+home_team]
        awayAttack = parameters["attack_"+away_team]
        awayDefence = parameters["defence_"+away_team]
        homeAdv = parameters["homeAdv"]

        homeGoalExp = np.exp(homeAttack + awayDefence + homeAdv)
        awayGoalExp = np.exp(awayAttack + homeDefence)

        homeProb = poisson.pmf(list(range(maxGoals + 1)), homeGoalExp)
        awayProb = poisson.pmf(range(maxGoals + 1), awayGoalExp)

        probabilityMatrix = np.outer(homeProb, awayProb)

        return(probabilityMatrix)

    df2 = pd.read_csv('FinalYearProjectCurrent/store/leagFixtures.csv')
    print("Head")
    print(df2.head())
    print("Tail")
    print(df2.tail())
    print("Shape")
    print(df2.shape)
    print("Columns")
    print(df2.columns)


    games = []
    wins = []
    draws = []
    loses = []
    gfor = []
    gagainst = []
    points = []
    for i in range(len(hside)):
        games.append(0)
        wins.append(0)
        draws.append(0)
        loses.append(0)
        gfor.append(0)
        gagainst.append(0)
        points.append(0)

    count = 0

    for idx, row in df2.iterrows():

        odds = predict(row["homeTeam"], row["awayTeam"], modelParameters, 4)
        
        #print(odds)

        draw = np.sum(np.diag(odds))
        #print("Likelyhood of draw")

        win = np.sum(np.tril(odds, 1))
        #print("Likelyhood of Home Win")

        loss = np.sum(np.triu(odds, -1))
        #print("Likelyhood of Away Win")

        h = 0
        a = 0
        pred = 0.0
        for i in range(len(odds)):
            for p in range(len(odds[i])):
                rnd = round(odds[i][p], 4)
                if rnd >= pred:
                    pred = rnd
                    h = i
                    a = p

        for i in range(len(hside)):
            if h > a:
                if row["homeTeam"] == hside[i]:
                    games[i] += 1
                    wins[i] += 1
                    gfor[i] += h
                    gagainst[i] += a
                    points[i] += 3
                if row["awayTeam"] == hside[i]:
                    games[i] += 1
                    loses[i] += 1
                    gfor[i] += a
                    gagainst[i] += h
                    points[i] += 0
                
            if h == a:
                if row["homeTeam"] == hside[i]:
                    games[i] += 1
                    draws[i] += 1
                    gfor[i] += h
                    gagainst[i] += a
                    points[i] += 1
                if row["awayTeam"] == hside[i]:
                    games[i] += 1
                    draws[i] += 1
                    gfor[i] += a
                    gagainst[i] += h
                    points[i] += 1

            if h < a:
                if row["homeTeam"] == hside[i]:
                    games[i] += 1
                    loses[i] += 1
                    gfor[i] += h
                    gagainst[i] += a
                    points[i] += 0
                if row["awayTeam"] == hside[i]:
                    games[i] += 1
                    wins[i] += 1
                    gfor[i] += a
                    gagainst[i] += h
                    points[i] += 3
        count += 1
    print(count)

    with open('FinalYearProjectCurrent/store/leagueTally.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['Team', 'Played', 'Wins', 'Draws', 'Loses', 'GF', 'GA', 'GD', 'Points']
        writer.writerow(header)

        for p in range(len(hside)):
            gd = (gfor[p] - gagainst[p])
            line = [hside[p], games[p], wins[p], draws[p], loses[p], gfor[p], gagainst[p], gd, points[p]]
            writer.writerow(line)


def mleagueDisplay():
    league = pd.read_csv("FinalYearProjectCurrent/store/leagueTally.csv")
    sorted_league = league.sort_values(by=["Points"], ascending=False)
    sorted_league.to_csv('FinalYearProjectCurrent/store/sortedleagueTally.csv', index=False)

    league = pd.read_csv("FinalYearProjectCurrent/store/sortedleagueTally.csv")
    
    clubs = []
    games = []
    wins = []
    draws = []
    loses = []
    gfor = []
    gagainst = []
    gdiff = []
    points = []
    for idx, row in league.iterrows():
        clubs.append(row["Team"])
        games.append(row["Played"])
        wins.append(row["Wins"])
        draws.append(row["Draws"])
        loses.append(row["Loses"])
        gfor.append(row["GF"])
        gagainst.append(row["GA"])
        gdiff.append(row["GD"])
        points.append(row["Points"])
    
    
    return clubs, games, wins, draws, loses, gfor, gagainst, gdiff, points





