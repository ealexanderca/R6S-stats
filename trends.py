import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
from termcolor import colored
import json
import re
from web_utils import get_auth_ticket
from web_utils import get_UID
from web_utils import get_json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

class UserInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.UID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
        self.title("User Statistics Interface")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.options_frame = ttk.LabelFrame(self, text="Options")
        self.options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        # Username input
        self.username_label = tk.Label(self.options_frame, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.options_frame)
        self.username_entry.pack()

        self.name_submit_button = tk.Button(self.options_frame, text="Submit", command=self.submit_username)
        self.name_submit_button.pack()

        self.UID_label = tk.Label(self.options_frame, text="UID:")
        self.UID_label.pack()

        self.UID_entry = tk.Entry(self.options_frame)
        self.UID_entry.pack()

        self.UID_submit_button = tk.Button(self.options_frame, text="Submit", command=self.submit_UID)
        self.UID_submit_button.pack()
        
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
        name = self.username_entry.get()
        authTicket = get_auth_ticket('uplay')
        self.UID=get_UID('uplay',name,authTicket)
        self.UID_entry.insert(0,self.UID)
        self.get_data()
        self.submit_stats

    def submit_UID(self):
        self.UID = self.UID_entry.get()
        authTicket = get_auth_ticket('uplay')
        name = get_UID('uplay',self.UID,authTicket)
        self.username_entry.insert(0,name)
        self.get_data()
        self.submit_stats
    
    def get_data(self):
        authTicket = get_auth_ticket('uplay')
        endDate = datetime.now()
        startDate = endDate - timedelta(days=120)
        endDate = endDate.strftime("%Y%m%d")
        startDate = startDate.strftime("%Y%m%d")
        file_path = self.UID+'trendtemp.json'  # Replace with your file's path
        get_json(file_path,"https://prod.datadev.ubisoft.com/v1/users/"+self.UID+"/playerstats?spaceId=5172a557-50b5-4665-b7db-e3f2e8c5041d&view=current&aggregation=movingpoint&gameMode=all,ranked,casual,unranked&platformGroup=PC&teamRole=all,attacker,defender&startDate="+startDate+"&endDate="+endDate+"&trendType=days",authTicket)
    
    def submit_stats(self):
        fig, ax = plt.subplots(figsize=(6,6),nrows=1, ncols=1)
        ax.clear()
        file_path = self.UID + 'trendtemp.json'
        selectedStat = self.selectedStat_var.get()
        gameMode = self.gameMode_var.get()
        teamRole = self.teamRole_var.get()
        # Call a function to process the selected stat, game mode, and player role
        with open(file_path, 'r') as json_file:
            json_data = json_file.read()
        parsed_data = json.loads(json_data)  # Convert JSON string to Python data structure
        try:
            data=parsed_data['profileData'][self.UID]['platforms']['PC']['gameModes'][gameMode]['teamRoles'][teamRole][0][selectedStat]['actuals']
            trend=parsed_data['profileData'][self.UID]['platforms']['PC']['gameModes'][gameMode]['teamRoles'][teamRole][0][selectedStat]['trend']
            datakeys = list(data.keys())
            datavalues = list(data.values())
            trendkeys = list(trend.keys())
            trendvalues = list(trend.values())
            x_new = np.linspace(min(map(int,trendkeys)), max(map(int,trendkeys)), 300)  # Increase the number of points
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
            if hasattr(self, "canvas"):
                self.canvas.get_tk_widget().destroy()
                self.toolbar.destroy()

            self.canvas = FigureCanvasTkAgg(fig, master=self)
            self.canvas.draw()

            # Pack the canvas into your Tkinter interface
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Add a Matplotlib navigation toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas, self)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        except:
            print("could not load")

    def on_closing(self):
        self.quit()
        

if __name__ == "__main__":
    app = UserInterface()
    app.mainloop()
