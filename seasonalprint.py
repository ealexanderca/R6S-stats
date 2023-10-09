from termcolor import colored
from r6sUtil import *
platform='uplay'
names=['make_uh_wish']
web=web_access()
skip_print=['type','statsType','seasonYear','seasonNumber','roundsWithAnAce','roundsWithClutch','seasonNum','statsDetail']
sumVals=["matchesPlayed","roundsPlayed","minutesPlayed","matchesWon","matchesLost","roundsWon","roundsLost","kills","assists","death","headshots","meleeKills","teamKills","openingKills","openingDeaths","trades","openingKillTrades","openingDeathTrades","revives","distanceTravelled","aces","clutches"]
colors=['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
sumAll={}
for item in sumVals:
    sumAll[item]=0
for name in names:
    UID=web.get_UID(platform,name)
    json_data=web.get_data('summary','seasonal',UID,platform)
    data=json_data['profileData'][UID]['platforms'][web.platformGroup[platform]]
    data=seasonalSummary(data)
    seasons=data['all']['seasons']
    for season in seasons:
        for item in sumVals:
            sumAll[item]=sumAll[item]+season[item]
        print(colored(season['seasonYear']+season['seasonNumber'], 'red'))
        for key, value in season.items():
            if key not in skip_print:
                print(colored(key+':','green'),value)
    print(colored('sum of all seasons and names', 'red'))
    for key, value in sumAll.items():
        print(colored(key+':','green'),value)
    print(colored("killDeathRatio",'green'),sumAll["kills"]/sumAll["death"])
    print(colored("winLossRatio",'green'),sumAll["matchesWon"]/sumAll["matchesLost"])
    print(colored("roundWinLossRatio",'green'),sumAll["roundsWon"]/sumAll["roundsLost"])
    print(colored("headshotAccuracy",'green'),sumAll["headshots"]/sumAll["kills"])