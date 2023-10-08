import tkinter as tk
from r6sUtil import *
import os
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from termcolor import colored
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import pandas as pd

class Interface(tk.Tk):
    def __init__(self):
        self.web=web_access()
        super().__init__()
        self.platform='uplay'
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
        self.submit_button = tk.Button(self.options_frame, text="Submit", command=self.submit)
        self.submit_button.pack()
        stats=['matchesPlayed', 'roundsPlayed', 'minutesPlayed', 'matchesWon', 'matchesLost', 'roundsWon', 'roundsLost', 'kills', 'assists', 'death', 'headshots', 'meleeKills', 'teamKills', 'openingKills', 'openingDeaths', 'trades', 'openingKillTrades', 'openingDeathTrades', 'revives', 'distanceTravelled', 'winLossRatio', 'killDeathRatio', 'headshotAccuracy', 'killsPerRound', 'roundsWithAKill', 'roundsWithMultiKill', 'roundsWithOpeningKill', 'roundsWithOpeningDeath', 'roundsWithKOST', 'roundsSurvived', 'roundsWithAnAce', 'roundsWithClutch', 'timeAlivePerMatch', 'timeDeadPerMatch', 'distancePerRound', 'aces', 'clutches', 'openingKillDeathRatio', 'RoundWinLossRatio']
        self.gameMode = exclusive_input(self, ["all", "casual", "ranked", "unranked"],"Game Mode:")
        self.stat = multiple_input(self, stats,"Statistic:",initial=[False for _ in range(len(stats))])
        self.trendLines = multiple_input(self, ["points","Spline","Linear","moving average spline"],"Data Plot:",initial=[True,True,False,False])
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
        self.json=seasonalSummary(self.web.get_data('summary','seasonal',self.UID.get())['profileData'][self.UID.get()]['platforms'][self.web.platformGroup[self.platform]])
        
    def draw(self):
        # try:
        cindex=-1
        fig, ax = plt.subplots(figsize=(6,6),nrows=1, ncols=1)
        ax.clear()
        colors=['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
        selectedGameMode = self.gameMode.var.get()
        selectedStats=[]
        for i,val in enumerate(self.stat.vars):
            if val.get():
                selectedStats.append(self.stat.options[i])
        for selectedStat in selectedStats:
            cindex+=1
            tree=datamap(self.json)
            datakeys=[]
            datavalues=[]
            for index in list(range(len(self.json[selectedGameMode]['seasons']))):
                current=self.json[selectedGameMode]['seasons'][index]
                datakeys.append(current['seasonYear']+current['seasonNumber'])
                datavalues.append(current[selectedStat])
            # converting data to number lists
                
            
            #plotting the data
            if self.trendLines.vars[0].get():
                ax.scatter(datakeys, datavalues, color=colors[cindex])
            # plotting the trend lines
            if self.trendLines.vars[1].get():
                #r6s trend line
                ax.plot(datakeys, datavalues, marker='', linestyle='-', color=colors[cindex])
            if self.trendLines.vars[2].get():
                #linear trend line
                coefficients = np.polyfit(datakeys, datavalues, 1)
                m, b = coefficients
                ax.plot(datakeys, m * np.array(datakeys) + b, color=colors[cindex])
            if self.trendLines.vars[3].get():
                #custom trend line
                window=min(5,len(datavalues))
                y_ma = pd.Series(datavalues).rolling(window=window,min_periods=1,center=True).mean()
                x_new2 = np.linspace(min(datakeys), max(datakeys), 800)  # Create 300 points for smoother curve
                spl = make_interp_spline(datakeys, y_ma, k=3)  # k=3 for cubic spline
                values_smooth2 = spl(x_new2)
                ax.plot(x_new2, values_smooth2, marker='', linestyle='-', color=colors[cindex])
        ax.set_xlabel('Game #')
        ax.set_ylabel('Value')
        ax.set_title('Seasonal Data Plot')
        ax.margins(x=0,y=0)
        # except:
        #     print(colored('Could Not Load Data or No Data','red'))
        #     ax.set_title('Could Not Load Data or No Data', color='red')
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
    app = Interface()
    app.mainloop()
