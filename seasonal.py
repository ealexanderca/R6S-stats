import tkinter as tk
from r6sUtil import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from termcolor import colored
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import pandas as pd
from matplotlib.lines import Line2D

class seasonalInterface():
    def __init__(self,frame):
        self.frame=frame
        self.web=web_access()
        self.options_frame = ttk.LabelFrame(self.frame, text="Options")
        self.options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        stats=['matchesPlayed', 'roundsPlayed', 'minutesPlayed', 'matchesWon', 'matchesLost', 'roundsWon', 'roundsLost', 'kills', 'assists', 'death', 'headshots', 'meleeKills', 'teamKills', 'openingKills', 'openingDeaths', 'trades', 'openingKillTrades', 'openingDeathTrades', 'revives', 'distanceTravelled', 'winLossRatio', 'killDeathRatio', 'headshotAccuracy', 'killsPerRound', 'roundsWithAKill', 'roundsWithMultiKill', 'roundsWithOpeningKill', 'roundsWithOpeningDeath', 'roundsWithKOST', 'roundsSurvived', 'roundsWithAnAce', 'roundsWithClutch', 'timeAlivePerMatch', 'timeDeadPerMatch', 'distancePerRound', 'aces', 'clutches', 'openingKillDeathRatio', 'RoundWinLossRatio']
        self.gameMode = exclusive_input(self,self.options_frame, ["all", "casual", "ranked", "unranked"],"Game Mode:",columns=2)
        self.stat = multiple_input(self,self.options_frame, stats,"Statistic:",initial=[False for _ in range(len(stats))],columns=2)
        self.trendLines = multiple_input(self,self.options_frame, ["Points","Line","Linear","Moving Average spline"],"Data Plot:",initial=[True,True,False,False],columns=2)
        
    def draw(self):
        try:
            cindex=-1
            fig, ax = plt.subplots(figsize=(6,6),nrows=1, ncols=1)
            ax.clear()
            colors=['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan','black']
            selectedGameMode = self.gameMode.var.get()
            selectedStats=[]
            for i,val in enumerate(self.stat.vars):
                if val.get():
                    selectedStats.append(self.stat.options[i])
            custom_lines =[]
            for selectedStat in selectedStats:
                cindex+=1
                datakeys=[]
                datavalues=[]
                for index in list(range(len(self.json[selectedGameMode]['seasons']))):
                    current=self.json[selectedGameMode]['seasons'][index]
                    if current['season_id']<14 and selectedStat in ['openingKills','openingDeaths','openingKillTrades','openingDeathTrades','roundsWithOpeningKill','roundsWithOpeningDeath','openingKillDeathRatio']:
                        datakeys.append(current['seasonYear']+current['seasonNumber'])
                        datavalues.append(np.NaN)
                    else:
                        datakeys.append(current['seasonYear']+current['seasonNumber'])
                        datavalues.append(current[selectedStat])
                # converting data to number lists
                dataints=list(range(len(datakeys)))
                #plotting the data
                idx = np.isfinite(datavalues)
                y=np.array(datavalues)[idx]
                x=np.array(dataints)[idx]
                if self.trendLines.vars[0].get():
                    ax.scatter(datakeys, datavalues, color=colors[cindex])
                # plotting the trend lines
                if self.trendLines.vars[1].get():
                    #r6s trend line
                    ax.plot(datakeys, datavalues, marker='', linestyle='-', color=colors[cindex])
                if self.trendLines.vars[2].get():
                    #linear trend line
                    coefficients = np.polyfit(x, y, 1)
                    m, b = coefficients
                    ax.plot(x, m * np.array(x) + b, color=colors[cindex])
                if self.trendLines.vars[3].get():
                    #custom trend line
                    window=min(5,len(y))
                    y_ma = pd.Series(y).rolling(window=window,min_periods=1,center=True).mean()
                    x_new2 = np.linspace(min(x), max(x), 800)  # Create 300 points for smoother curve
                    spl = make_interp_spline(x, y_ma, k=3)  # k=3 for cubic spline
                    values_smooth2 = spl(x_new2)
                    ax.plot(x_new2, values_smooth2, marker='', linestyle='-', color=colors[cindex])
                custom_lines.append(Line2D([0], [0], color=colors[cindex], lw=4))
            ax.legend(custom_lines, selectedStats)
            ax.set_xlabel('Game #')
            ax.set_ylabel('Value')
            ax.set_title("Seasonal Data Plot")
            ax.margins(x=0,y=0)
            ax.set_ylim(bottom=0)
            plt.margins(0)
            fig.subplots_adjust(left=0.12, right=.98, top=.95, bottom=0.1)
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

    def get(self,UID,platform,days=None):
        self.json=seasonalSummary(self.web.get_data('summary','seasonal',UID)['profileData'][UID]['platforms'][self.web.platformGroup[platform]])
        self.draw()

if __name__ == "__main__":
    app=base(seasonalInterface)
    app.mainloop()