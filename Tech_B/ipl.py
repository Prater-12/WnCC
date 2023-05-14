# This started of as an attempt to scrape the IPL website to get a complete performance history of every team (since they only show the last 5),
# but in the process of trying to work around the dynamic nature of the page, I started accessing the API the site used, and in the end I'm
# not sure if this qualifies as a web scrapper anymore

import pandas as pd
import time
import datetime
import requests
import json
import re


def extract_JSON(res):
    b = str(res.content)
    b = re.sub(r'\\\\', r'\\', b)
    slc = slice(b.index('(')+1, b.rindex(')'))
    return json.loads(b[slc])


POINTS_TABLE_URL = 'https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/107-groupstandings.js'
MATCHES_URL = 'https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/107-matchschedule.js?MatchSchedule=_jqjsp&_1684078254800='

try:
    pointsRes = requests.get(POINTS_TABLE_URL)
except:
    print("Fetching data failed, try again.")
    exit(1)

points = extract_JSON(pointsRes)['points']

points.sort(key=lambda team: int(team['OrderNo']))

teams = {int(team['TeamID']): {
    'name': team['TeamName'],
    'code': team['TeamCode'],
    'logo': team['TeamLogo'],
    'matches': team['Matches'],
    'wins': team['Wins'],
    'loss': team['Loss'],
    'tied': team['Tied'],
    'no_result': team['NoResult'],
    'points': team['Points'],
    'nrr': team['NetRunRate'],
    'performance': [],
} for team in points}

try:
    matchRes = requests.get(MATCHES_URL)
except:
    print("Fetching data failed, try again.")
    exit(1)
matchSummaries = extract_JSON(matchRes)['Matchsummary']

matchSummaries.sort(key=lambda match: time.mktime(datetime.datetime.strptime(
    f"{match['GMTMatchDate']} {match['GMTMatchTime']}", '%Y-%m-%d %H:%M GMT').timetuple()), reverse=True)

for match in matchSummaries:
    if match['MatchStatus'] != 'Post':
        continue
    firstBat = match['FirstBattingTeamID']
    secondBat = match['SecondBattingTeamID']

    if (match['WinningTeamID'] == ''):
        if (match['Commentss'] == 'No Result'):
            teams[firstBat]['performance'].append('N')
            teams[secondBat]['performance'].append('N')
        else:
            teams[firstBat]['performance'].append('T')
            teams[secondBat]['performance'].append('T')
    else:
        winningTeamID = int(match['WinningTeamID'])
        LosingTeamID = secondBat if firstBat == winningTeamID else firstBat

        teams[winningTeamID]['performance'].append('W')
        teams[LosingTeamID]['performance'].append('L')

dfDict = {'id': []}

first = True

for teamID, team in teams.items():
    dfDict['id'].append(teamID)

    for key, value in team.items():
        if first:
            dfDict[key] = [value]
        else:
            dfDict[key].append(value)
    first = False

df = pd.DataFrame(dfDict)

df.to_csv(
    f"ipl_2023_point_table_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.csv", index=False)
