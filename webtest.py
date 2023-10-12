from r6sUtil import *
web=web_access()
platform='uplay'
UID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
data=web.get_data(url='https://public-ubiservices.ubi.com/v1/spaces/')
print(data)

