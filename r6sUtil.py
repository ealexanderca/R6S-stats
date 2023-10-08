import tkinter as tk
import os
import json
from datetime import datetime, timedelta
import requests
import http.client
import base64
import getpass
import re

def filePath():
    return os.path.dirname(os.path.abspath(__file__))+"\\"  


class exclusive_input():
    def __init__(self, root, options,title):
        self.var = tk.StringVar(value=options[0])
        self.label = tk.Label(root.options_frame, text=title, fg="red")  # Set text color to red
        self.label.pack()

        for option in options:
            rb = tk.Radiobutton(root.options_frame, text=option, variable=self.var, value=option, command=root.draw)
            rb.pack()


class multiple_input():
    def __init__(self, root, options, title,colors=None,initial=None):
        if colors==None:
            colors=[]
            for i in range(len(options)):
                colors.append('black')
        if initial==None:
            initial=[]
            for i in range(len(options)):
                initial.append(True)
        self.colors=colors
        self.options=options
        self.vars = [tk.BooleanVar(value=val) for val in initial]
        self.label = tk.Label(root.options_frame, text=title, fg="red")
        self.label.pack()
        for i, option in enumerate(options):
            cb = tk.Checkbutton(root.options_frame, fg=colors[i], text=option, variable=self.vars[i], onvalue=True, offvalue=False, command=root.draw)
            cb.pack()
    

class text_input():
    def __init__(self, root, entry, title):
        self.label = tk.Label(root.options_frame, text=title)
        self.label.pack()
        self.entry = tk.Entry(root.options_frame)
        self.entry.pack()
        self.entry.insert(0,entry)
        self.old=entry

    def update(self,entry):
        if entry != None:
            self.entry.delete(0,'end')
            self.entry.insert(0,entry)
        else:
            self.entry.delete(0,'end')
            self.entry.insert(0,'^Error^')
        self.old=self.get()
        
    def changed(self):
        temp= self.old!=self.get()
        self.old=self.get()
        return temp
    
    def get(self):
        return self.entry.get()
    
    def val(self):
        return int(self.entry.get())


class web_access:
    def __init__(self):
        self.config=filePath()+"webConfig.json"
        self.appid = ''
        # settings
        self.authTicket=''
        self.sessionID=''
        self.get_appID()
        self.read_config()
        self.spaceIds = {
            "uplay": "5172a557-50b5-4665-b7db-e3f2e8c5041d",
            "psn": "05bfb3f7-6c21-4c42-be1f-97a33fb5cf66",
            "xbl": "98a601e5-ca91-4440-b1c5-753f601a2c90",
            "null": "null"
        }
        self.platformGroup ={
            "uplay": "PC",
            "psn": "console",
            "xbl": "console",
            "null": "null"
        }
    
    def write_config(self):
        data={
            'token': self.token,
            'authTicket': self.authTicket,
            'sessionID': self.sessionID
        }
        with open(self.config, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def read_config(self):
        if not os.path.exists(self.config):
            self.generate_token()
            self.get_auth_ticket()
            self.write_config()
        else:
            with open(self.config, "r") as file:
                data = json.load(file)
                self.token=data['token']
                self.authTicket=data['authTicket']
                self.sessionID=data['sessionID']

    def generate_token(self):
        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")
        self.token = 'basic ' + base64.b64encode((email + ":" + password).encode("utf-8")).decode("utf-8")
        print("Generated Token")

    def get_auth_ticket(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.token,
            'Ubi-AppId': self.appid,
        }
        conn = http.client.HTTPSConnection('public-ubiservices.ubi.com', port=443)
        path = '/v3/profiles/sessions'
        try:
            conn.request('POST', path, headers=headers)
            response = conn.getresponse()
            data = response.read()
            if response.getcode() != 200:
                print('could not get auth code, try deleting token.txt to regenerate it')
            else:
                auth = json.loads(data)
                self.authTicket = 'Ubi_v1 t=' + auth['ticket']
                self.sessionID = auth['sessionId']
            conn.close()
            self.write_config()
        except Exception as e:
            print(str(e))
        
    def get_appID(self):
        url="https://www.ubisoft.com/en-ca/game/rainbow-six/siege/stats/summary/833708a6-9155-435c-bfdc-6d9a96d6fcd0"
        response = self.send_request(url)
        match = re.search('"appId":"([^"]+)"', response.text)
        self.appid=match.group(1)

    def get_UID(self,platform,username):
        url = "https://public-ubiservices.ubi.com/v3/profiles?nameOnPlatform="+username+"&platformType="+platform
        response = self.send_request(url)
        print("UID response code: "+str(response.status_code))
        userData=json.loads(response.text)['profiles']
        for data in userData:
            if data['platformType'] == platform:
                return data['userId']

    def get_name(self,platform,UID):
        url = "https://public-ubiservices.ubi.com/v3/profiles?idOnPlatform="+UID+"&platformType="+platform
        response = self.send_request(url)
        print("name response code: "+str(response.status_code))
        userData=json.loads(response.text)
        return userData['profiles'][0]['nameOnPlatform']

    def get_data(self,aggregation=['summary','movingpoint','weapons','operators','maps'][0],view=['seasonal','current'][0],UID='',platform='uplay',startDate = (datetime.now() - timedelta(days=120)).strftime("%Y%m%d"),endDate = datetime.now().strftime("%Y%m%d"),seasonCode=None,region=None,gameMode='all,ranked,casual,unranked',teamRole='attacker,defender,all',url=None,debug=False):
        # possible aggregations 
        if seasonCode is list:
            seasonCode = ','.join(seasonCode)
        if gameMode is list:
            gameMode = ','.join(gameMode)
        if teamRole is list:
            teamRole = ','.join(teamRole)
        if region is list:
            region = ','.join(region)
        #selects the correct url to collect the data
        if url == None:
            if view == 'sandbox':
                seasonIds=','.join(map(str, list(range(0,-31,-1))))
                url="https://public-ubiservices.ubi.com/v1/spaces/"+self.spaceIds[platform]+"/sandboxes/OSBOR_PC_LNCH_A/r6karma/player_skill_records?board_ids=pvp_ranked&season_ids="+seasonIds+"&region_ids="+region+"&profile_ids="+UID
            else:
                url="https://prod.datadev.ubisoft.com/v1/users/"+UID+"/playerstats?spaceId="+self.spaceIds[platform]+"&view="+view+"&aggregation="+aggregation+"&gameMode="+gameMode+"&teamRole="+teamRole
                if aggregation == 'movingpoint':
                    url+="&trendType=days"
                if platform != '':
                    url+="&platformGroup="+self.platformGroup[platform]+"&platform="+self.platformGroup[platform]
                if view=="current":
                    url+="&startDate="+startDate+"&endDate="+endDate
                if seasonCode != None:
                    url+="&seasons="+seasonCode
                if region != None:
                    url+="&region_ids="+region
        response = self.send_request(url)
        if debug==True:
            print(url)
            print(response.text)
        print("Data response code: "+ str(response.status_code))
        if response.text:
            return json.loads(response.text)
    
    def send_request(self,url):
        headers = {
            "Authorization": self.authTicket,
            "Expiration": (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Ubi-Appid": self.appid,
            "Ubi-Sessionid": self.sessionID,
            'User-Agent': 'UbiServices_SDK_2020.Release.58_PC64_ansi_static',
            'Connection': 'keep-alive'
            }
        response = requests.get(url, headers=headers)
        if response.status_code !=200:
            self.get_auth_ticket()
            headers = {
            "Authorization": self.authTicket,
            "Expiration": (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Ubi-Appid": self.appid,
            "Ubi-Sessionid": self.sessionID,
            'User-Agent': 'UbiServices_SDK_2020.Release.58_PC64_ansi_static',
            'Connection': 'keep-alive'
            }
            response = requests.get(url, headers=headers)
        return response
def datamap(data):
    tree=[]
    tree.append(list(data))
    index=1
    while True:
        data=data[tree[index-1][0]]
        if type(data) is list:
            print(len(data))
            tree.append([len(data)-1])
        elif type(data) is dict:
            tree.append(list(data))
        else:
            break
        index+=1
    return tree

def removechoice(data):
    if type(data) is list:
        tree=list(range(len(data)))
    elif type(data) is dict:
        tree=list(data)
    else:
        return data
    
    if len(tree)<=1:
        return removechoice(data[tree[0]])
    elif type(data) is list:
        temp=[]
        for i in tree:
            temp.append(removechoice(data[i]))
    else:
        if 'value' in tree:
            return data['value']
        else:
            temp={}
            for key in tree:
                temp[key]=removechoice(data[key])
    return temp

def div(i,j):
    if j==0:
        return 0
    else:
        return i/j
    
def seasonalSummary(data):
    data=removechoice(data)
    calc=[["round(season['roundsWithAnAce']*season['roundsPlayed'])",'aces'],["round(season['roundsWithClutch']*season['roundsPlayed'])",'clutches'],["div(season['openingKills'],season['openingDeaths'])",'openingKillDeathRatio'],["div(season['roundsWon'],season['roundsLost'])",'RoundWinLossRatio']]
    sumVals=["matchesPlayed","roundsPlayed","minutesPlayed","matchesWon","matchesLost","roundsWon","roundsLost","kills","assists","death","headshots","meleeKills","teamKills","openingKills","openingDeaths","trades","openingKillTrades","openingDeathTrades","revives","distanceTravelled","aces","clutches"]
    for key,seasons in data.items():
        sumAll={}
        for item in sumVals:
            sumAll[item]=0
        for season in seasons:
            season['seasonNum'] = int(re.findall(r'\d+',season['seasonYear'])[0])*4+int(re.findall(r'\d+',season['seasonNumber'])[0])-5
            for calcIn,calcOut in calc:
                season[calcOut]=eval(calcIn)
            for item in sumVals:
                sumAll[item]+=season[item]
        seasons = sorted(seasons, key=lambda x: x['seasonNum'], reverse=False)
        sumAll["openingKillDeathRatio"]=sumAll["openingKills"]/sumAll["openingDeaths"]
        sumAll["killDeathRatio"]=sumAll["kills"]/sumAll["death"]
        sumAll["winLossRatio"]=sumAll["matchesWon"]/sumAll["matchesLost"]
        sumAll["RoundWinLossRatio"]=sumAll["roundsWon"]/sumAll["roundsLost"]
        sumAll["headshotAccuracy"]=sumAll["headshots"]/sumAll["kills"]
        data[key]={'seasons': seasons,"Summary": sumAll}
    return data