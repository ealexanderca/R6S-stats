import json
from termcolor import colored
import json
import re
from web_utils import get_auth_ticket
from web_utils import get_UID
from web_utils import get_json
from datetime import datetime, timedelta
#inputs
names=['botdogs']
platform='uplay'
UID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
platform2='PC'
gameMode='all'
teamRole='all'
authTicket = get_auth_ticket(platform)
spaceIds = {
    "uplay": "5172a557-50b5-4665-b7db-e3f2e8c5041d",
    "psn": "05bfb3f7-6c21-4c42-be1f-97a33fb5cf66",
    "xbl": "98a601e5-ca91-4440-b1c5-753f601a2c90",
    "null": "null"
}
#date range
endDate = datetime.now()

# Calculate the start date by subtracting 120 days
startDate = endDate - timedelta(days=120)

# Format the dates as YYYYMMDD strings
endDate = endDate.strftime("%Y%m%d")
startDate = startDate.strftime("%Y%m%d")
for name in names:
    if name !='':
        UID=get_UID(platform,name,authTicket)
    # Step 1: Read the JSON file
    file_path = UID+'trendtemp.json'  # Replace with your file's path
    get_json(file_path,"https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=movingpoint&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=all,attacker,defender&startDate="+startDate+"&endDate="+endDate+"&trendType=days",authTicket)
    with open(file_path, 'r') as json_file:
        json_data = json_file.read()
    parsed_data = json.loads(json_data)  # Convert JSON string to Python data structure
    seasons=parsed_data['profileData'][UID]['platforms'][platform2]['gameModes'][gameMode]['teamRoles'][teamRole]
    

#other urls to test
# url ="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=summary&gameMode=all,ranked,unranked,casual&platformGroup="+platform2+"&teamRole=all,attacker,defender&seasons="+seasonCode
# url ="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=movingpoint&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=all,attacker,defender&startDate="+startDate+"&endDate="+endDate+"&trendType=days"
# url="https://public-ubiservices.ubi.com/v1/spaces/"+spaceIds[platform]+"/sandboxes/OSBOR_PC_LNCH_A/r6karma/player_skill_records?board_ids=pvp_ranked&season_ids=-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,-26,-27,-28,-29,-30,-31&region_ids=ncsa&profile_ids="+UID
# url="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=weapons&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=attacker,defender,all"
# url="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=operators&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=attacker,defender&seasons="+seasonCode
# url="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+spaceIds[platform]+"&view=current&aggregation=maps&gameMode=all,ranked,casual,unranked&platformGroup="+platform2+"&teamRole=all,attacker,defender&seasons="+seasonCode