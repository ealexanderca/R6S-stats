import tkinter as tk
import os
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
from termcolor import colored
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import requests
import http.client
import base64
import getpass

class UserInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.UID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
        self.name='botdogs'
        self.days=120
        self.filePath=script_filepath = os.path.abspath(__file__)
        if os.path.exists(filePath()+"defaultUID.txt"):
            with open(filePath()+"defaultUID.txt", "r") as file:
                self.UID = file.read().strip()
        else:
            file = open(filePath()+"defaultUID.txt", "w") 
            file.write(self.UID)
            file.close()
        self.authTicket=''
        self.sessionID=''
        self.title("User Statistics Interface")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.options_frame = ttk.LabelFrame(self, text="Options")
        self.options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        self.appid = "39baebad-39e5-4552-8c25-2c9b919064e2"
        # settings

        self.spaceIds = {
            "uplay": "5172a557-50b5-4665-b7db-e3f2e8c5041d",
            "psn": "05bfb3f7-6c21-4c42-be1f-97a33fb5cf66",
            "xbl": "98a601e5-ca91-4440-b1c5-753f601a2c90",
            "null": "null"
        }

        self.username_label = tk.Label(self.options_frame, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.options_frame)
        self.username_entry.pack()
        self.username_entry.insert(0,self.name)

        self.name_submit_button = tk.Button(self.options_frame, text="Submit", command=self.submit_username)
        self.name_submit_button.pack()

        self.UID_label = tk.Label(self.options_frame, text="UID:")
        self.UID_label.pack()

        self.UID_entry = tk.Entry(self.options_frame)
        self.UID_entry.pack()
        self.UID_entry.insert(0,self.UID)

        self.UID_submit_button = tk.Button(self.options_frame, text="Submit", command=self.submit_UID)
        self.UID_submit_button.pack()

        self.days_label = tk.Label(self.options_frame, text="Number of days:")
        self.days_label.pack()

        self.days_entry = tk.Entry(self.options_frame)
        self.days_entry.pack()
        self.days_entry.insert(0,'120')

        self.days_submit_button = tk.Button(self.options_frame, text="Submit", command=self.submit_days)
        self.days_submit_button.pack()

        
        
        # Exclusive button groups
        self.gameMode_var = tk.StringVar(value="all")
        self.gameMode_label = tk.Label(self.options_frame, text="Game Mode:", fg="red")  # Set text color to red
        self.gameMode_label.pack()

        gameModes = ["all", "casual", "ranked", "unranked"]
        for mode in gameModes:
            rb = tk.Radiobutton(self.options_frame, text=mode, variable=self.gameMode_var, value=mode, command=self.submit_stats)
            rb.pack()

        self.teamRole_var = tk.StringVar(value="all")
        self.teamRole_label = tk.Label(self.options_frame, text="Player Role:", fg="red")  # Set text color to red
        self.teamRole_label.pack()

        teamRoles = ["all", "attacker", "defender"]
        for role in teamRoles:
            rb = tk.Radiobutton(self.options_frame, text=role, variable=self.teamRole_var, value=role, command=self.submit_stats)
            rb.pack()

        self.selectedStat_var = tk.StringVar(value="winLossRatio")
        self.stats_label = tk.Label(self.options_frame, text="Select Stats:", fg="red")  # Set text color to red
        self.stats_label.pack()

        stats = ["winLossRatio", "killDeathRatio", "headshotAccuracy", "killsPerRound", "roundsWithAKill", "roundsWithMultiKill","roundsWithOpeningKill", "roundsWithOpeningDeath", "roundsWithKOST","roundsSurvived", "ratioTimeAlivePerMatch", "distancePerRound"]
        for stat in stats:
            rb = tk.Radiobutton(self.options_frame, text=stat, variable=self.selectedStat_var, value=stat, command=self.submit_stats)
            rb.pack()
        self.get_data()
        self.submit_stats()

    def submit_username(self):
        self.name = self.username_entry.get()
        self.get_UID('uplay')
        self.UID_entry.delete(0,'end')
        self.UID_entry.insert(0,self.UID)
        self.get_data()
        self.submit_stats()

    def submit_UID(self):
        self.UID = self.UID_entry.get()
        self.get_name('uplay')
        self.username_entry.delete(0,'end')
        self.username_entry.insert(0,self.name)
        self.get_data()
        self.submit_stats()
    
    def submit_days(self):
        if self.days_entry.get()=='':
             self.days=120
        else:
            self.days = int(self.days_entry.get())
        if self.days>120 or self.days<1:
            if self.days>60:
                self.days=120
            else:
                self.days=1
        self.days_entry.delete(0,'end')
        self.days_entry.insert(0,self.days)
        self.get_data()
        self.submit_stats()
    
    def get_data(self):
        endDate = datetime.now()
        startDate = endDate - timedelta(days=self.days)
        endDate = endDate.strftime("%Y%m%d")
        startDate = startDate.strftime("%Y%m%d")
        file_path = filePath()+self.UID+'trendtemp.json'  # Replace with your file's path
        url="https://prod.datadev.ubisoft.com/v1/users/"+self.UID+"/playerstats?spaceId=5172a557-50b5-4665-b7db-e3f2e8c5041d&view=current&aggregation=movingpoint&gameMode=all,ranked,casual,unranked&platformGroup=PC&teamRole=all,attacker,defender&startDate="+startDate+"&endDate="+endDate+"&trendType=days"
        response = self.send_request(url)
        print("Data response code: "+ str(response.status_code))
        with open(file_path, 'w') as f:
            f.write(response.text)
        
    def submit_stats(self):
        fig, ax = plt.subplots(figsize=(6,6),nrows=1, ncols=1)
        ax.clear()
        file_path = filePath() + self.UID + 'trendtemp.json'
        selectedStat = self.selectedStat_var.get()
        gameMode = self.gameMode_var.get()
        teamRole = self.teamRole_var.get()
        # Call a function to process the selected stat, game mode, and player role
        try:
            with open(file_path, 'r') as json_file:
                json_data = json_file.read()
            parsed_data = json.loads(json_data)  # Convert JSON string to Python data structure
            data=parsed_data['profileData'][self.UID]['platforms']['PC']['gameModes'][gameMode]['teamRoles'][teamRole][0][selectedStat]['actuals']
            trend=parsed_data['profileData'][self.UID]['platforms']['PC']['gameModes'][gameMode]['teamRoles'][teamRole][0][selectedStat]['trend']
            datakeys = list(data.keys())
            datavalues = list(data.values())
            trendkeys = list(trend.keys())
            trendvalues = list(trend.values())
            x_new = np.linspace(min(map(int,trendkeys)), max(map(int,trendkeys)), 800)  # Increase the number of points
            spline = make_interp_spline(trendkeys, trendvalues, k=3)
            values_smooth = spline(x_new)
            max_ticks = 20
            x_tick_indices = np.linspace(0, len(datakeys) - 1, max_ticks, dtype=int)
            x_ticks = [datakeys[i] for i in x_tick_indices]
            ax.scatter(datakeys, datavalues)
            ax.plot(x_new, values_smooth, marker='', linestyle='-', color='b')
            ax.set_xlabel('Game #')
            ax.set_ylabel('Value')
            ax.set_title(selectedStat+' Data Plot')
            ax.set_xticks(x_ticks)
            ax.set_xlim(min(map(int,datakeys)), max(map(int,datakeys)))
            ax.set_ylim(0, max([np.max(values_smooth),max(map(int,datavalues))]))
            
        except:
            print(colored('Could Not Load Data or No Data','red'))
            ax.set_title('Could Not Load Data or No Data', color='red')
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            plt.close()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()

        # Pack the canvas into your Tkinter interface
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add a Matplotlib navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def on_closing(self):
        self.quit()


    def get_auth_ticket(self):
        with open(filePath()+"token.txt", "r") as file:
            token = file.read().strip()
        
        # Get auth token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token,
            'Ubi-AppId': self.appid,
        }

        conn = http.client.HTTPSConnection('public-ubiservices.ubi.com', port=443)
        path = '/v3/profiles/sessions'
        data = {
            'appId': self.appid,
            'spaceId': self.spaceIds['uplay'],
        }
        json_data = json.dumps(data)

        try:
            conn.request('POST', path, body=json_data, headers=headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
            session_data = json.loads(data)
            self.authTicket = 'Ubi_v1 t=' + session_data['ticket']
            self.sessionID = session_data['sessionId']
        except Exception as e:
            print(str(e))

    def get_UID(self,platform):
        url = "https://public-ubiservices.ubi.com/v3/profiles?nameOnPlatform="+self.name+"&platformType="+platform
        response = self.send_request(url)
        print("UID response code: "+str(response.status_code))
        userData=json.loads(response.text)
        self.UID = userData['profiles'][0]['idOnPlatform']

    def get_name(self,platform):
        url = "https://public-ubiservices.ubi.com/v3/profiles?idOnPlatform="+self.UID+"&platformType="+platform
        response = self.send_request(url)
        print("name response code: "+str(response.status_code))
        userData=json.loads(response.text)
        self.name = userData['profiles'][0]['nameOnPlatform']

    def send_request(self,url):
        headers = {
            "Authorization": self.authTicket,
            "Expiration": (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Ubi-Appid": self.appid,
            "Ubi-Sessionid": self.sessionID,
        }
        response = requests.get(url, headers=headers)
        if response.status_code !=200:
            self.get_auth_ticket()
            headers = {
            "Authorization": self.authTicket,
            "Expiration": (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Ubi-Appid": self.appid,
            "Ubi-Sessionid": self.sessionID,
            }
            response = requests.get(url, headers=headers)
        return response


            
def filePath():
    return os.path.dirname(os.path.abspath(__file__))+"\\"

def token_encode(email, password):
    token = 'basic ' + base64.b64encode((email + ":" + password).encode("utf-8")).decode("utf-8")
    return token

def generate_token():
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")
    token = token_encode(email, password)
    file = open(filePath()+"token.txt", "w") 
    file.write(token)
    file.close()
    print("Generated Token saved to token.txt")

def check_token():
    if not os.path.exists(filePath()+"token.txt"):
        generate_token()       

if __name__ == "__main__":
    check_token()
    app = UserInterface()
    app.mainloop()
