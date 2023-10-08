from r6sUtil import *
web=web_access()
platform='uplay'
UID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
json_data=web.get_data('summary','seasonal',UID,platform)
data=json_data['profileData'][UID]['platforms'][web.platformGroup[platform]]
data=seasonalSummary(data)