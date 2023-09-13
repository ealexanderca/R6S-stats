import tkinter as tk
import os
import json
from datetime import datetime, timedelta
import requests
import http.client
import base64
import getpass

def filePath():
    return os.path.dirname(os.path.abspath(__file__))+"\\"
class web_token():
    def __init__(self):
        self.check()
    def encode(self,email, password):
        self.token = 'basic ' + base64.b64encode((email + ":" + password).encode("utf-8")).decode("utf-8")

    def generate(self):
        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")
        self.encode(email, password)
        file = open(filePath()+"token.txt", "w") 
        file.write(self.token)
        file.close()
        print("Generated Token saved to token.txt")

    def check(self):
        if not os.path.exists(filePath()+"token.txt"):
            self.generate()
        else:
            with open(filePath()+"token.txt", "r") as file:
                self.token = file.read().strip()

class exclusive_input():
    def __init__(self, root, options,title):
        self.var = tk.StringVar(value=options[0])
        self.label = tk.Label(root.options_frame, text=title, fg="red")  # Set text color to red
        self.label.pack()

        for option in options:
            rb = tk.Radiobutton(root.options_frame, text=option, variable=self.var, value=option, command=root.draw)
            rb.pack()
    

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
        self.webToken=web_token()
        self.appid = "39baebad-39e5-4552-8c25-2c9b919064e2"
        # settings
        self.authTicket=''
        self.sessionID=''
        self.spaceIds = {
            "uplay": "5172a557-50b5-4665-b7db-e3f2e8c5041d",
            "psn": "05bfb3f7-6c21-4c42-be1f-97a33fb5cf66",
            "xbl": "98a601e5-ca91-4440-b1c5-753f601a2c90",
            "null": "null"
        }
    
    def get_auth_ticket(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.webToken.token,
            'Ubi-AppId': self.appid,
        }

        conn = http.client.HTTPSConnection('public-ubiservices.ubi.com', port=443)
        path = '/v3/profiles/sessions'
        data = {
            'appId': self.appid,
            'spaceId': self.spaceIds['uplay'],
        }
        json_trends = json.dumps(data)

        try:
            conn.request('POST', path, body=json_trends, headers=headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
            session_trends = json.loads(data)
            self.authTicket = 'Ubi_v1 t=' + session_trends['ticket']
            self.sessionID = session_trends['sessionId']
        except Exception as e:
            print(str(e))

    def get_UID(self,platform,username):
        url = "https://public-ubiservices.ubi.com/v3/profiles?nameOnPlatform="+username+"&platformType="+platform
        response = self.send_request(url)
        print("UID response code: "+str(response.status_code))
        userData=json.loads(response.text)
        return userData['profiles'][0]['idOnPlatform']

    def get_name(self,platform,UID):
        url = "https://public-ubiservices.ubi.com/v3/profiles?idOnPlatform="+UID+"&platformType="+platform
        response = self.send_request(url)
        print("name response code: "+str(response.status_code))
        userData=json.loads(response.text)
        return userData['profiles'][0]['nameOnPlatform']

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
