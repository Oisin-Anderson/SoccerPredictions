import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
from scipy.stats import poisson
from scipy.optimize import minimize


def psplayer(playerID):
    base_url = 'https://understat.com/player'
    url = base_url + '/' + playerID

    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    scripts = soup.find_all('script')

    strings = scripts[1].string

    # print(strings)

    ind_start = strings.index("('") + 2
    ind_end = strings.index("')")
    json_data = strings[ind_start:ind_end]

    json_data = json_data.encode('utf8').decode('unicode_escape')

    playdata = json.loads(json_data)
    data = playdata['season']

    #print(data)

    for index in range(len(data)):
        team = data[index]['team']
        played = data[index]['games']
        break
    print(team)



    strings = scripts[3].string
    #print(strings)

    ind_start = strings.index("('") + 2
    ind_end = strings.index("')")
    json_data = strings[ind_start:ind_end]

    json_data = json_data.encode('utf8').decode('unicode_escape')

    data2 = json.loads(json_data)

    #print(data2)

    for index in range(len(data2)):
        player = data2[index]['player']
        break
    print(player)
    return team, player


def psteamgames(team):
    fixtures = []
    base_url = 'https://understat.com/league'
    url = base_url + '/EPL/2021'

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
    print(team)
    for index in range(len(data)):
        if data[index]['isResult'] is True:
            hname = data[index]['h']['title']
            aname = data[index]['a']['title']
            id = data[index]['id']
            if team == hname or team == aname:
                fixtures.append(id)
    print(fixtures)
    return fixtures


def psfixtures(fixtures, player, oppCon, oppStop, opponent):
    with open('FinalYearProjectCurrent/store/psFixtures.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        header = ["Player", "Against", "Goals", "OppCon", "Missed", "OppSaved"]
        writer.writerow(header)
        print(fixtures)
        goals = []
        missed = []
        for j in range(len(fixtures)):
            base_url = 'https://understat.com/match'
            url = base_url + '/' + fixtures[j]
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

            data_home = data['h']
            data_away = data['a']

            goal = 0
            miss = 0
            played = 0

            for index in range(len(data_home)):
                temp = data_home[index]['player']
                result = data_home[index]['result']
                if player == temp:
                    played += 1
                    if result == "Goal":
                        goal += 1
                    else:
                        miss += 1
                    
            for index in range(len(data_away)):
                temp = data_away[index]['player']
                result = data_away[index]['result']
                if player == temp:
                    played += 1
                    if result == "Goal":
                        goal += 1
                    else:
                        miss += 1
            if bool(played):
                goals.append(goal)
                missed.append(miss)

        print(goals)
        for p in range(len(goals)):
            line = ["Ronaldo", opponent, goals[p], oppCon[p], missed[p], oppStop[p]]
            writer.writerow(line)


def pspredictions(player, opponent):
    df = pd.read_csv('FinalYearProjectCurrent/store/psFixtures.csv')
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
        play_goals_observed,
        opp_def_observed,
        play_scored,
        play_missed,
        opp_conceded,
        opp_stopped,
    ):
        play_goal_expectation = np.exp(play_scored + opp_conceded)
        opp_stop_expectation = np.exp(opp_stopped + play_missed)

        if play_goal_expectation < 0 or opp_stop_expectation < 0:
            return 10000    

        play_llk = poisson.pmf(play_goals_observed, play_goal_expectation)
        opp_llk = poisson.pmf(opp_def_observed, opp_stop_expectation)

        logLLK = np.log(play_llk) + np.log(opp_llk)

        return -logLLK


    def fitPoissonModel():
        teams = np.sort(np.unique(np.concatenate([df["Player"], df["Against"]])))
        noTeams = len(teams)

        parameters = np.concatenate(
            (
                np.random.uniform(0.5, 1.5, (noTeams)),  # attack strength
                np.random.uniform(0, -1, (noTeams)),  # defence strength
            )
        )

        def _fit(parameters, df, teams):
            attParameter = dict(zip(teams, parameters[:noTeams]))
            defParameter = dict(zip(teams, parameters[noTeams : (2 * noTeams)]))
            llk = []

            for idx, row in df.iterrows():
                tmp = logLikelyHood(
                    row["Goals"],
                    row["OppCon"],
                    attParameter[row["Player"]],
                    defParameter[row["Player"]],
                    attParameter[row["Against"]],
                    defParameter[row["Against"]],
                )
                llk.append(tmp)

            return np.sum(llk)

        options = {
            "maxiter": 100,
            "disp": False,
        }

        constraints = [{"type": "eq", "fun": lambda x: sum(x[:noTeams]) - noTeams}]

        print(len(teams))
        print(len(df))
        res = minimize(
            _fit,
            parameters,
            args=(df, teams),
            constraints=constraints,
            options=options
        )

        modelParameters = dict(
            zip(
                ["scored_" + team for team in teams]
                + ["missed_" + team for team in teams],
                res["x"],
            )
        )

        return modelParameters

    modelParameters = fitPoissonModel()

    print(modelParameters)

    def predict(player, against, parameters, maxGoals):
        play_scored = parameters["scored_"+player]
        play_missed = parameters["missed_"+player]
        opp_conceded = parameters["scored_"+against]
        opp_stopped = parameters["missed_"+against]

        play_goal_exp = np.exp(play_scored + opp_conceded)
        opp_stop_exp = np.exp(opp_stopped + play_missed)

        play_probs = poisson.pmf(list(range(maxGoals + 1)), play_goal_exp)
        opp_probs = poisson.pmf(range(maxGoals + 1), opp_stop_exp)

        probabilityMatrix = np.outer(play_probs, opp_probs)

        return(probabilityMatrix)

    odds = predict(player, opponent, modelParameters, 4)

    return odds


def psopponent(opponent, fixtures):
    against = []
    base_url = 'https://understat.com/league'
    url = base_url + '/EPL/2021'

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
    print(opponent)
    for index in range(len(data)):
        if data[index]['isResult'] is True:
            hname = data[index]['h']['title']
            aname = data[index]['a']['title']
            id = data[index]['id']
            if opponent == hname or opponent == aname:
                against.append(id)
    print(against)

    oppCon = []
    oppStop = []
    for j in range(len(against)):
        base_url = 'https://understat.com/match'
        url = base_url + '/' + against[j]
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

        data_home = data['h']
        data_away = data['a']

        concede = 0
        shot = 0
        played = 0

        for index in range(len(data_home)):
            played += 1
            temp = data_home[index]['h_team']
            result = data_home[index]['result']
            if opponent == temp:
                if result == "Goal":
                    concede += 1
                else:
                    shot += 1
                
        for index in range(len(data_away)):
            played += 1
            temp = data_away[index]['a_team']
            result = data_away[index]['result']
            if opponent == temp:
                if result == "Goal":
                    concede += 1
                else:
                    shot += 1

        if bool(played):
            oppCon.append(concede)
            oppStop.append(shot)
    
    for i in range(len(oppCon)):
        if len(oppCon) == 24:
            break
        oppCon.pop(0)

        print(len(oppCon))

    for i in range(len(oppStop)):
        if len(oppStop) == 24:
            break
        oppStop.pop(0)

    print(len(oppCon))
    print(len(oppStop))
    return oppCon, oppStop
