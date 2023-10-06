import tkinter as tk
from r6sUtil import *
import os
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
from termcolor import colored
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline


class TrendInterface(tk.Tk):
    def __init__(self):
        self.web=web_access()
        super().__init__()
        self.defaultUID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
        self.defaultname='botdogs'
        self.filePath= os.path.abspath(__file__)
        if os.path.exists(filePath()+"defaultUID.txt"):
            with open(filePath()+"defaultUID.txt", "r") as file:
                self.defaultUID = file.read().strip()
        else:
            file = open(filePath()+"defaultUID.txt", "w") 
            file.write(self.UID.get())
            file.close()
        
        self.title("User Statistics Interface")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.options_frame = ttk.LabelFrame(self, text="Options")
        self.options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        
        self.username = text_input(self,self.defaultname,'Username:')
        self.UID = text_input(self,self.defaultUID,'UID:')
        self.days = text_input(self,'120','Days:')
        self.submit_button = tk.Button(self.options_frame, text="Submit", command=self.submit)
        self.submit_button.pack()
    
        self.gameMode = exclusive_input(self, ["all", "casual", "ranked", "unranked"],"Game Mode:")
        self.teamRole = exclusive_input(self, ["all", "attacker", "defender"],"Team Role:")
        self.stat = exclusive_input(self, ["winLossRatio", "killDeathRatio", "headshotAccuracy", "killsPerRound", "roundsWithAKill", "roundsWithMultiKill","roundsWithOpeningKill", "roundsWithOpeningDeath", "roundsWithKOST","roundsSurvived", "ratioTimeAlivePerMatch", "distancePerRound"],"Statistic:")
        self.get()
        self.draw()

    def submit(self):
        if self.username.changed():
            self.UID.update(self.web.get_UID('uplay',self.username.get()))
        elif self.UID.changed():
            self.username.update(self.web.get_name('uplay',self.UID.get()))
        if self.days.changed():
            if self.days.get()=='':
                self.days.update("120")
            if self.days.val()>120:
                self.days.update("120")
            elif self.days.val()<1:
                self.days.update('1')
        self.get()
        self.draw()

    def get(self):
        endDate = datetime.now()
        startDate = endDate - timedelta(days=self.days.val())
        endDate = endDate.strftime("%Y%m%d")
        startDate = startDate.strftime("%Y%m%d")
        self.json=self.web.get_data('movingpoint','current',self.UID.get(),startDate=startDate,endDate=endDate)
        
    def draw(self):
        try:
            fig, ax = plt.subplots(figsize=(6,6),nrows=1, ncols=1)
            ax.clear()
            selectedStat = self.stat.var.get()
            selectedGameMode = self.gameMode.var.get()
            selectedTeamRole = self.teamRole.var.get()
            
            data=self.json['profileData'][self.UID.get()]['platforms']['PC']['gameModes'][selectedGameMode]['teamRoles'][selectedTeamRole][0][selectedStat]['actuals']
            trend=self.json['profileData'][self.UID.get()]['platforms']['PC']['gameModes'][selectedGameMode]['teamRoles'][selectedTeamRole][0][selectedStat]['trend']
            datakeys = list(data.keys())
            datavalues = list(data.values())
            trendkeys = list(trend.keys())
            trendvalues = list(trend.values())
            x_new = np.linspace(min(map(int,trendkeys)), max(map(int,trendkeys)), 800)
            try:
                spline = make_interp_spline(trendkeys, trendvalues, k=3)
                values_smooth = spline(x_new)
            except:
                values_smooth=trendvalues
                x_new = trendkeys
            
            ax.scatter(datakeys, datavalues)
            ax.plot(x_new, values_smooth, marker='', linestyle='-', color='b')
            ax.set_xlabel('Game #')
            ax.set_ylabel('Value')
            ax.set_title(selectedStat+' Data Plot')
            if max([np.max(values_smooth),max(map(int,datavalues))])!=0:
                ax.set_ylim(0, max([np.max(values_smooth),max(map(int,datavalues))]))
            else:
                ax.set_ylim(0,1)
            xticks = ax.get_xticks()
            ax.set_xticks(xticks[::len(xticks) // 9])
            ax.tick_params(axis='x', rotation=30)
            ax.margins(x=0)  
        except:
            print(colored('Could Not Load Data or No Data','red'))
            ax.set_title('Could Not Load Data or No Data', color='red')
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            plt.close()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def on_closing(self):
        self.quit()

if __name__ == "__main__":
    app = TrendInterface()
    app.mainloop()
