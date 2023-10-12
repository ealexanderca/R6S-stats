import tkinter as tk
import os
import json
from datetime import datetime, timedelta
import requests
import http.client
import base64
import getpass
import re
from tkinter import ttk

def filePath():
    return os.path.dirname(os.path.abspath(__file__))+"\\"  


class exclusive_input():
    def __init__(self, root,frame, options,title,columns=1,column=None,row=None):
        self.var = tk.StringVar(value=options[0])
        self.frame= ttk.LabelFrame(frame, text=title)

        for i, option in enumerate(options):
            row_index = i // columns + 1 
            col_index = i % columns
            rb = tk.Radiobutton(self.frame, text=option, variable=self.var, value=option, command=root.draw)
            rb.grid(row=row_index, column=col_index)
        if row is None or column is None:
            self.frame.pack()
        else:
            self.frame.grid(row=row, column=column)


class multiple_input():
    def __init__(self, root,frame, options, title,colors=None,initial=None,columns=1,column=None,row=None):
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
        self.frame= ttk.LabelFrame(frame, text=title)
        self.vars = [tk.BooleanVar(value=val) for val in initial]
        for i, option in enumerate(options):
            row_index = i // columns + 1
            col_index = i % columns
            cb = tk.Checkbutton(self.frame, fg=colors[i], text=option, variable=self.vars[i], onvalue=True, offvalue=False, command=root.draw)
            cb.grid(row=row_index, column=col_index)
        if row is None or column is None:
            self.frame.pack()
        else:
            self.frame.grid(row=row, column=column)
    
class drop_down():
    def __init__(self,frame, options, title, row=None,column=None):
        self.frame= ttk.LabelFrame(frame, text=title)
        self.selection=tk.StringVar()
        self.entry = tk.OptionMenu(self.frame,self.selection,*options)
        self.selection.set(options[0])
        self.old=options[0]
        self.entry.pack()
        
        if row is None or column is None:
            self.frame.pack()
        else:
            self.frame.grid(row=row, column=column)

    def changed(self):
        temp= self.old!=self.get()
        self.old=self.get()
        return temp

    def get(self):
        return str(self.selection.get())

    def val(self):
        return int(self.selection.get())

class text_input():
    def __init__(self,frame, entry, title, row=None,column=None):
        self.frame= ttk.LabelFrame(frame, text=title)
        self.entry = tk.Entry(self.frame)
        self.entry.pack()
        self.entry.insert(0,entry)
        self.old=entry
        if row is None or column is None:
            self.frame.pack()
        else:
            self.frame.grid(row=row, column=column)

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
        self.appid=''
        # settings
        self.authTicket=''
        self.sessionId=''
        self.get_appID()
        try:
            self.token=self.read_config('token')
        except:
            self.generate_token()
        try:
            [self.sessionId,self.authTicket]=self.read_config(['sessionId','authTicket'])
        except:
            self.get_authTicket()
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
    
    def write_config(self,input):
        try:
            file = open(self.config, 'r')
            data=json.load(file)
        except:
            file = open(self.config, 'w')
            json.dump(input, file, indent=4)
            return False
        file.close
        file = open(self.config, 'w')
        data.update(input)
        json.dump(data, file, indent=4)
        return True

    def read_config(self,val):
        file= open(self.config, "r")
        data = json.load(file)
        file.close()
        if type(val) is list:
            out={}
            for item in val:
                out[item]=data[item]
        else:
            out=data[val]
        return out

    def generate_token(self):
        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")
        self.token = 'basic ' + base64.b64encode((email + ":" + password).encode("utf-8")).decode("utf-8")
        print("Generated Token")
        self.write_config({'token': self.token})

    def get_authTicket(self):
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
                self.sessionId = auth['sessionId']
            conn.close()
        except Exception as e:
            print(str(e))
        self.write_config({'sessionId': self.sessionId,'authTicket': self.authTicket})

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

    def get_data(self,aggregation=['summary','movingpoint','weapons','operators','maps'][0],view=['seasonal','current','rank'][0],UID='',platform='uplay',startDate = (datetime.now() - timedelta(days=120)).strftime("%Y%m%d"),endDate = datetime.now().strftime("%Y%m%d"),seasonCode=None,region='ncsa',gameMode='all,ranked,casual,unranked',teamRole='attacker,defender,all',url=None,debug=False):
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
            if view == 'rank':
                seasonIds=','.join(map(str, list(range(0,-27,-1))))
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
            "Ubi-Sessionid": self.sessionId,
            'User-Agent': 'UbiServices_SDK_2020.Release.58_PC64_ansi_static',
            'Connection': 'keep-alive'
            }
        response = requests.get(url, headers=headers)
        if response.status_code !=200:
            self.get_authTicket()
            headers = {
            "Authorization": self.authTicket,
            "Expiration": (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Ubi-Appid": self.appid,
            "Ubi-Sessionid": self.sessionId,
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
            season['season_id'] = int(re.findall(r'\d+',season['seasonYear'])[0])*4+int(re.findall(r'\d+',season['seasonNumber'])[0])-4
            for calcIn,calcOut in calc:
                season[calcOut]=eval(calcIn)
            for item in sumVals:
                sumAll[item]+=season[item]
        seasons = sorted(seasons, key=lambda x: x['season_id'], reverse=False)
        sumAll["openingKillDeathRatio"]=sumAll["openingKills"]/sumAll["openingDeaths"]
        sumAll["killDeathRatio"]=sumAll["kills"]/sumAll["death"]
        sumAll["winLossRatio"]=sumAll["matchesWon"]/sumAll["matchesLost"]
        sumAll["RoundWinLossRatio"]=sumAll["roundsWon"]/sumAll["roundsLost"]
        sumAll["headshotAccuracy"]=sumAll["headshots"]/sumAll["kills"]
        data[key]={'seasons': seasons,"Summary": sumAll}
    return data

class base(tk.Tk):
    def __init__(self,plotterClass):
        super().__init__()
        self.web=web_access()
        self.platform='uplay'
        self.defaultUID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
        self.defaultname='botdogs'
        try:
            self.defaultUID=self.web.read_config('defaultUID')
        except:
            self.web.write_config({'defaultUID':self.defaultUID})
        self.title("User Statistics Interface")
        self.protocol("WM_DELETE_WINDOW",self.on_closing)
        self.plotter=plotterClass(self)
        self.header= tk.Frame(self)
        self.username = text_input(self.header,self.defaultname,'Username:',row=0, column=0)
        self.UID = text_input(self.header,self.defaultUID,'UID:',row=0, column=1)
        self.platform = drop_down(self.header,['uplay','psn','xbl'],'Platform:',row=0, column=2)
        self.days = text_input(self.header,'120','Days:',row=0, column=3)
        self.submit_button = tk.Button(self.header, text="Submit", command=self.submit)
        self.submit_button.grid(row=0, column=4)
        self.header.pack()
        self.plotter.get(self.UID.get(),self.platform.get(),days=self.days.val())


    def submit(self):
        if self.username.changed():
            self.UID.update(self.web.get_UID('uplay',self.username.get()))
        elif self.UID.changed():
            self.username.update(self.web.get_name('uplay',self.UID.get()))
        self.plotter.get(self.UID.get(),self.platform.get(),days=self.days.val())
    
    def on_closing(self):
        self.quit()