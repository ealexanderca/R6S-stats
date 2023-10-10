from r6sUtil import *
web=web_access()
platform='uplay'
UID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
web.config
file= open(web.config, "r")
print(json.load(file))
