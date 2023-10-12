import tkinter as tk
from r6sUtil import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from termcolor import colored
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import pandas as pd
from datetime import datetime, timedelta

class trendInterface():
    def __init__(self,frame):
        self.frame=frame
        self.web=web_access()
        self.options_frame = ttk.LabelFrame(self.frame, text="Options")
        self.options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        self.gameMode = exclusive_input(self,self.options_frame, ["all", "casual", "ranked", "unranked"],"Game Mode:",columns=2)
        self.teamRole = multiple_input(self,self.options_frame, ["all", "attacker", "defender"],"Team Role:",colors=['black','red','blue'])
        self.stat = exclusive_input(self,self.options_frame, ["winLossRatio", "killDeathRatio", "headshotAccuracy", "killsPerRound", "roundsWithAKill", "roundsWithMultiKill","roundsWithOpeningKill", "roundsWithOpeningDeath", "roundsWithKOST","roundsSurvived", "ratioTimeAlivePerMatch", "distancePerRound"],"Statistic:")
        self.trendLines = multiple_input(self,self.options_frame, ["points","Spline","Linear","moving average spline"],"Data Plot:",initial=[True,True,False,False])
        
    def draw(self):
        try:
            fig, ax = plt.subplots(figsize=(6,6),nrows=1, ncols=1)
            ax.clear()
            selectedStat = self.stat.var.get()
            selectedGameMode = self.gameMode.var.get()
            selectedTeamRoles=[]
            colors=self.teamRole.colors
            for index,val in enumerate(self.teamRole.vars):
                if val.get():
                    selectedTeamRoles.append(self.teamRole.options[index])
            for selectedTeamRole in selectedTeamRoles:
                index=self.teamRole.options.index(selectedTeamRole)
                data=self.json['gameModes'][selectedGameMode]['teamRoles'][selectedTeamRole][0][selectedStat]['actuals']
                trend=self.json['gameModes'][selectedGameMode]['teamRoles'][selectedTeamRole][0][selectedStat]['trend']
                # converting data to number lists
                datakeys = [eval(i) for i in list(data.keys())]
                datavalues = list(data.values())
                trendkeys = [eval(i) for i in list(trend.keys())]
                trendvalues = list(trend.values())
                #plotting the data
                if self.trendLines.vars[0].get():
                    ax.scatter(datakeys, datavalues, color=colors[index])
                # plotting the trend lines
                if self.trendLines.vars[1].get():
                    #r6s trend line
                    x_new = np.linspace(min(map(int,datakeys)), max(map(int,datakeys)), 800)
                    try:
                        spline = make_interp_spline(np.array(trendkeys)/max(trendkeys)*max(datakeys), trendvalues, k=3)
                        values_smooth = spline(x_new)
                    except:
                        values_smooth=trendvalues
                        x_new = trendkeys
                    ax.plot(x_new, values_smooth, marker='', linestyle='-', color=colors[index])
                if self.trendLines.vars[2].get():
                    #linear trend line
                    coefficients = np.polyfit(datakeys, datavalues, 1)
                    m, b = coefficients
                    ax.plot(datakeys, m * np.array(datakeys) + b, color=colors[index])
                if self.trendLines.vars[3].get():
                    #custom trend line
                    window=min(5,len(datavalues))
                    y_ma = pd.Series(datavalues).rolling(window=window,min_periods=1,center=True).mean()
                    x_new2 = np.linspace(min(datakeys), max(datakeys), 800)  # Create 300 points for smoother curve
                    spl = make_interp_spline(datakeys, y_ma, k=3)  # k=3 for cubic spline
                    values_smooth2 = spl(x_new2)
                    ax.plot(x_new2, values_smooth2, marker='', linestyle='-', color=colors[index])
            ax.set_xlabel('Game #')
            ax.set_ylabel('Value')
            ax.set_title(selectedStat+' Data Plot')
            ax.margins(x=0,y=0)
            fig.subplots_adjust(left=0.08, right=.98, top=.95, bottom=0.1)
            plt.margins(0)
        except:
            print(colored('Could Not Load Data or No Data','red'))
            ax.set_title('Could Not Load Data or No Data', color='red')
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            plt.close()
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def get(self,UID,platform,days):
        endDate = datetime.now()
        startDate = endDate - timedelta(days=days)
        endDate = endDate.strftime("%Y%m%d")
        startDate = startDate.strftime("%Y%m%d")
        self.json=self.web.get_data('movingpoint','current',UID,platform,startDate=startDate,endDate=endDate)['profileData'][UID]['platforms'][self.web.platformGroup[platform]]
        self.draw()

if __name__ == "__main__":
    app=base(trendInterface)
    app.mainloop()