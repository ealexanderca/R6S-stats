from termcolor import colored
import re
from r6sUtil import *

#inputs
names=['betterbotdogs','botdogs']
platform='uplay'
skip_print=['type','statsType','seasonYear','seasonNumber','roundsWithAnAce','roundsWithClutch','seasonNum','statsDetail']
calc=[['roundsWithAnAce','aces'],['roundsWithClutch','clutches']]
sumVals=["matchesPlayed","roundsPlayed","minutesPlayed","matchesWon","matchesLost","roundsWon","roundsLost","kills","assists","death","headshots","meleeKills","teamKills","openingKills","openingDeaths","trades","openingKillTrades","openingDeathTrades","revives","distanceTravelled","aces","clutches"]
platform2='PC'
gameMode='all'
teamRole='all'
sumAll={}
web=web_access()
for item in sumVals:
    sumAll[item]=0
for name in names:
    #UID collection
    if name !='':
        UID=web.get_UID(platform,name)
    # Step 1: Read the JSON file
    json_data=web.get_data('summary','seasonal',UID)
    seasons=json_data['profileData'][UID]['platforms'][platform2]['gameModes'][gameMode]['teamRoles'][teamRole]
    for season in seasons:
        season['seasonNum'] = int(re.findall(r'\d+',season['seasonYear'])[0])*4+int(re.findall(r'\d+',season['seasonNumber'])[0])-5
        for calcIn,calcOut in calc:
            if type(season[calcIn]) is dict:
                season[calcOut]=round(season['roundsPlayed']*season[calcIn]['value'])
            else:
                season[calcOut]=round(season['roundsPlayed']*season[calcIn])
        for item in sumVals:
            sumAll[item]=sumAll[item]+season[item]

    seasons = sorted(seasons, key=lambda x: x['seasonNum'], reverse=False)
    for season in seasons:
        print(colored(season['seasonYear']+season['seasonNumber'], 'red'))
        for key, value in season.items():
            if key not in skip_print:
                print(colored(key+':','green'),value)
    print(colored('sum of all seasons', 'red'))
    for key, value in sumAll.items():
        print(colored(key+':','green'),value)
    print(colored("K/D",'green'),sumAll["kills"]/sumAll["death"])
    print(colored("match W/L",'green'),sumAll["matchesWon"]/sumAll["matchesLost"])
    print(colored("round W/L",'green'),sumAll["roundsWon"]/sumAll["roundsLost"])