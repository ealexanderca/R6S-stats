
import tkinter as tk                     
from tkinter import ttk 
from r6sUtil import *

def on_closing(self):
    self.quit()

def submit():
    print('submit')

class statsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tab Widget") 
        tabControl = ttk.Notebook(self) 
        self.title("User Statistics Interface")
        self.defaultUID='833708a6-9155-435c-bfdc-6d9a96d6fcd0'
        self.defaultname='botdogs'
        self.protocol("WM_DELETE_WINDOW",on_closing(self))
        self.header= tk.Frame(self)
        self.username = text_input(self.header,self.defaultname,'Username:',row=0, column=0)
        self.UID = text_input(self.header,self.defaultUID,'UID:',row=0, column=1)
        self.days = text_input(self.header,'120','Days:',row=0, column=2)
        self.submit_button = tk.Button(self.header, text="Submit", command=submit)
        self.submit_button.grid(row=0, column=3)
        self.header.pack()
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)



        tabControl.add(tab1, text ='Seasonal')
        tabControl.add(tab2, text ='Trends')
        tabControl.pack(expand = 1, fill ="both") 

        ttk.Label(tab1,text ="Welcome to GeeksForGeeks").grid(column = 0,row = 0,padx = 30,pady = 30)   
        ttk.Label(tab2,text ="Lets dive into the world of computers").grid(column = 0,row = 0,padx = 30,pady = 30) 

if __name__ == "__main__":
    app = statsWindow()
    app.mainloop()