import os
import http.client
import json
from datetime import datetime, timedelta
import requests

current_time = datetime.utcnow()
future_time = current_time + timedelta(minutes=10)
formatted_future_time = future_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
spaceIds = {
    "uplay": "5172a557-50b5-4665-b7db-e3f2e8c5041d",
    "psn": "05bfb3f7-6c21-4c42-be1f-97a33fb5cf66",
    "xbl": "98a601e5-ca91-4440-b1c5-753f601a2c90",
    "null": "null"
}
appid = "39baebad-39e5-4552-8c25-2c9b919064e2"

def get_auth_ticket(platform):
    if not os.path.exists("token.txt"):
        with open("tokenGenerator.py") as f:
            exec(f.read())
    with open("token.txt", "r") as file:
        token = file.read().strip()
    

    # Get auth token
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
        'Ubi-AppId': appid,
    }

    conn = http.client.HTTPSConnection('public-ubiservices.ubi.com', port=443)
    path = '/v3/profiles/sessions'
    data = {
        'appId': appid,
        'spaceId': spaceIds[platform],
    }
    json_data = json.dumps(data)

    try:
        conn.request('POST', path, body=json_data, headers=headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        session_data = json.loads(data)
        authTicket = 'Ubi_v1 t=' + session_data['ticket']
        return authTicket
    except Exception as e:
        print(str(e))

def get_UID(platform,name,authTicket):
    headers = {
        "Authorization": authTicket,
        "Expiration": formatted_future_time,
        "Ubi-Appid": appid,
        "Ubi-Sessionid": "57130b9b-0cb7-49c7-8fda-ba0be96f4dd3",
    }
    url = "https://public-ubiservices.ubi.com/v3/profiles?nameOnPlatform="+name+"&platformType="+platform
    response = requests.get(url, headers=headers)
    print("UID response code: "+str(response.status_code))
    userData=json.loads(response.text)
    return userData['profiles'][0]['idOnPlatform']

def get_name(platform,UID,authTicket):
    headers = {
        "Authorization": authTicket,
        "Expiration": formatted_future_time,
        "Ubi-Appid": appid,
        "Ubi-Sessionid": "57130b9b-0cb7-49c7-8fda-ba0be96f4dd3",
    }
    url = "https://public-ubiservices.ubi.com/v3/profiles?idOnPlatform="+UID+"&platformType="+platform
    response = requests.get(url, headers=headers)
    print("UID response code: "+str(response.status_code))
    userData=json.loads(response.text)
    print(userData)
    return userData['profiles'][0]['nameOnPlatform']

def get_json(file_path,url,authTicket):
    headers = {
        "Authorization": authTicket,
        "Expiration": formatted_future_time,
        "Ubi-Appid": appid,
        "Ubi-Sessionid": "57130b9b-0cb7-49c7-8fda-ba0be96f4dd3",
    }
    response = requests.get(url, headers=headers)
    print("Data response code: "+ str(response.status_code))
    with open(file_path, 'w') as f:
        f.write(response.text)