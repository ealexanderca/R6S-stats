
import tkinter as tk                     
from tkinter import ttk 
from r6sUtil import *
from seasonal import *
from trend import *

class statsWindow(tk.Tk):
    def __init__(self):
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
        tabControl = ttk.Notebook(self) 
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        self.seasonal=seasonalInterface(tab1)
        self.trend=trendInterface(tab2)
        self.header= tk.Frame(self)
        self.username = text_input(self.header,self.defaultname,'Username:',row=0, column=0)
        self.UID = text_input(self.header,self.defaultUID,'UID:',row=0, column=1)
        self.platform = drop_down(self.header,['uplay','psn','xbl'],'Platform:',row=0, column=2)
        self.days = text_input(self.header,'120','Days:',row=0, column=3)
        self.submit_button = tk.Button(self.header, text="Submit", command=self.submit)
        self.submit_button.grid(row=0, column=4)
        self.header.pack()
        tabControl.add(tab1, text ='Seasonal')
        tabControl.add(tab2, text ='Trends')
        tabControl.pack(expand = 1, fill ="both") 
        self.seasonal.get(self.UID.get(),self.platform.get())
        self.trend.get(self.UID.get(),self.platform.get(),self.days.val())


    def submit(self):
        if self.username.changed():
            self.UID.update(self.web.get_UID('uplay',self.username.get()))
        elif self.UID.changed():
            self.username.update(self.web.get_name('uplay',self.UID.get()))
        self.seasonal.get(self.UID.get(),self.platform.get())
    
    def on_closing(self):
        self.quit()


if __name__ == "__main__":
    app = statsWindow()
    app.mainloop()