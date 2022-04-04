import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
from scipy.stats import poisson
from scipy.optimize import minimize

def h2hscraping(team1, team2, league):
    seasons = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"]

    #Exports data from league and season chosen
    with open('FinalYearProjectCurrent/store/h2h.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['DateTime', 'homeTeam', 'awayTeam', 'homeId', 'awayId', 'homeGoals', 'awayGoals']
        writer.writerow(header)
        for i in range(len(seasons)):
            base_url = 'https://understat.com/league/'
            url = base_url + league + '/' + seasons[i]


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
                if data[index]['isResult'] is True:
                    hGoals = int(data[index]['goals']['h'])
                    hid = int(data[index]['h']['id'])
                    hTeam = data[index]['h']['title']
                    aGoals = int(data[index]['goals']['a'])
                    aid = int(data[index]['a']['id'])
                    aTeam = data[index]['a']['title']
                    temp = data[index]['datetime']
                    date = datetime.fromisoformat(temp)
                    # print(type(date))
                    if hTeam == team1 and aTeam == team2:
                        
                        line = [date, hTeam, aTeam, hid, aid, hGoals, aGoals]
                        writer.writerow(line)
                    if aTeam == team1 and hTeam == team2:
                        
                        line = [date, hTeam, aTeam, hid, aid, hGoals, aGoals]
                        writer.writerow(line)
                    

def h2hpredictions(team1, team2):
    df = pd.read_csv('FinalYearProjectCurrent/store/h2h.csv')
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

    odds = predict(team1, team2, modelParameters, 4)

    return odds

def h2hdata(odds):
    draw = np.sum(np.diag(odds))
    #print(draw)

    win = np.sum(np.tril(odds, 1))
    #print(win)

    loss = np.sum(np.triu(odds, -1))
    #print(loss)

    predict = 0.0
    h = 0
    a = 0
    scores = []

    win = round((win * 100), 3)
    draw = round((draw * 100), 3)
    loss = round((loss * 100), 3)

    for i in range(len(odds)):
        for p in range(len(odds[i])):
            rnd = round((odds[i][p] * 100), 3)
            if rnd >= predict:
                predict = rnd
                h = i
                a = p

            scores.append(rnd)
    return draw, win, loss, predict, h, a, scores