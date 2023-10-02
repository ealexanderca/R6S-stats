import json
from termcolor import colored
import json
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
    json_data=web.get_data('seasonal',UID,'uplay')
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

#other urls to test
# url = "https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=summary&gameMode=all,ranked,unranked,casual&platformGroup="+platform2+"&teamRole=all,attacker,defender&seasons="+seasonCode
# url ="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=movingpoint&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=all,attacker,defender&startDate="+startDate+"&endDate="+endDate+"&trendType=days"
# url="https://public-ubiservices.ubi.com/v1/spaces/"+spaceIds[platform]+"/sandboxes/OSBOR_PC_LNCH_A/r6karma/player_skill_records?board_ids=pvp_ranked&season_ids=-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,-26,-27,-28,-29,-30,-31&region_ids=ncsa&profile_ids="+UID
# url="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=weapons&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=attacker,defender,all"
# url="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=operators&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=attacker,defender&seasons="+seasonCode
# url="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=maps&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=all,attacker,defender&seasons="+seasonCode