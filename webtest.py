from r6sUtil import *
name='botdogs'
UID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
platform='uplay'
web=web_access()
if name !='':
    UID=web.get_UID(platform,name)
data=web.get_data(url='https://prod.datadev.ubisoft.com/v1/users/833708a6-9155-435c-bfdc-6d9a96d6fcd0/playerstats?spaceId=5172a557-50b5-4665-b7db-e3f2e8c5041d&view=seasonal&aggregation=summary&gameMode=all,ranked,unranked,casual&platform=PC&teamRole=all,Attacker,Defender')