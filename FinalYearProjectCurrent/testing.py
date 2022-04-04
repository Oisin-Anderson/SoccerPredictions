import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import csv
import json
from scipy.stats import poisson
from scipy.optimize import minimize


def testMatches(league):
    base_url = 'https://understat.com/league/'
    url = base_url +  league + '/2021'

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
    
    hteam = ""
    hgoals = 0
    ateam = ""
    agoals = 0
    result = ""
    with open('FinalYearProjectCurrent/store/testFixtures.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ['homeTeam', 'homeGoals', 'awayTeam', 'awayGoals', 'Result']
        writer.writerow(header)
        for index in range(len(data)):
            if data[index]['isResult'] is True:
                hgoals = int(data[index]['goals']['h'])
                hteam = data[index]['h']['title']
                ateam = data[index]['a']['title']
                agoals = int(data[index]['goals']['a'])
                if hgoals > agoals:
                    result = "H"
                if hgoals == agoals:
                    result = "D"
                if hgoals < agoals:
                    result = "A"
            
                line = [hteam, hgoals, ateam, agoals, result]
                writer.writerow(line)

def testTail():
    df = pd.read_csv('FinalYearProjectCurrent/store/testFixtures.csv')
    #print(df.tail())

    tail = df.tail(20)

    hteams = []
    ateams = []
    #print(tail)
    for idx, row in tail.iterrows():
        hteams.append(row["homeTeam"])
        ateams.append(row["awayTeam"])

    return hteams, ateams, tail


def testDirect(team1, team2, league):
    seasons = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"]

    
    home = []
    away = []
    hgo = []
    ago = []
    for i in range(len(seasons)):
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
            if data[index]['isResult'] is True:
                hGoals = int(data[index]['goals']['h'])
                hTeam = data[index]['h']['title']
                aGoals = int(data[index]['goals']['a'])
                aTeam = data[index]['a']['title']
                if hTeam == team1 and aTeam == team2:
                    home.append(hTeam)
                    away.append(aTeam)
                    hgo.append(hGoals)
                    ago.append(aGoals)
                if aTeam == team1 and hTeam == team2:
                    home.append(hTeam)
                    away.append(aTeam)
                    hgo.append(hGoals)
                    ago.append(aGoals)
                    
    return home, away, hgo, ago




def testPredictions(hteams, ateams):
    df = pd.read_csv('FinalYearProjectCurrent/store/testFixtures.csv')
    df = df.iloc[:-20 , :]

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
    

    result = []
    for i in range(len(hteams)):
        odds = predict(hteams[i], ateams[i], modelParameters, 4)
        print("here")
        
        draw = np.sum(np.diag(odds))
        #print("Likelyhood of draw")

        win = np.sum(np.tril(odds, 1))
        #print("Likelyhood of Home Win")

        loss = np.sum(np.triu(odds, -1))
        #print("Likelyhood of Away Win")

        if win > loss and win > draw:
            result.append("H")
        elif draw > loss and draw > win:
            result.append("D")
        elif loss > win and loss > draw:
            result.append("A")

    return result




def testDirPredictions(hteam, ateam):
    df = pd.read_csv('FinalYearProjectCurrent/store/testFixtures.csv')
    df = df.iloc[:-1 , :]

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
    

    result = ""
    odds = predict(hteam, ateam, modelParameters, 4)
    print("here")
    
    draw = np.sum(np.diag(odds))
    #print("Likelyhood of draw")

    win = np.sum(np.tril(odds, 1))
    #print("Likelyhood of Home Win")

    loss = np.sum(np.triu(odds, -1))
    #print("Likelyhood of Away Win")

    if win > loss and win > draw:
        result = "H"
    elif draw > loss and draw > win:
        result = "D"
    elif loss > win and loss > draw:
        result = "A"

    return result

def saveTest(option, predict):
    
    if option == "Direct":
        with open('FinalYearProjectCurrent/store/testDirect.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            header = ['Predict']
            writer.writerow(header)
            for i in range(len(predict)):
                line = [predict[i]]
                writer.writerow(line)

    if option == "League":
        with open('FinalYearProjectCurrent/store/testLeague.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            header = ['Predict']
            writer.writerow(header)
            for i in range(len(predict)):
                line = [predict[i]]
                writer.writerow(line)
