import requests
import os
import json
import time
from datetime import datetime

# DEPENDENCIES
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_TOKEN")
base_api_url = os.getenv("BASE_API_URL")
headers = {'Content-Type': 'application/json', 'Authorization': api_token}


def api_call_get(endpoint):
    # print("Calling GET\n")
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        # print("Returning GET\n")
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Too bad\n")
        return None

# POST API CALL HELPER FUNCTION


def api_call_post(endpoint, payload, now, cooldown):
    # print("Calling POST\n")
    # print(f">>>> payload {payload} <<<<")
    # time management
    then = now
    now = datetime.now()
    duration = now - then
    duration_in_s = duration.total_seconds()
    if duration_in_s <= cooldown:
        waiting_time = cooldown - duration_in_s
        print(
            f" >>>> Oh dear, we have to wait {waiting_time} seconds <<<<\n\n")
        time.sleep(waiting_time)
        print(f"<<<< Done with waiting. Let's move on.>>>> \n\n")
    print(f"## Calling >>>{endpoint}<<< endpoint ##\n\n")
    response = requests.post(
        f"{base_api_url}{endpoint}", headers=headers, json=payload)
    if response.status_code == 200:
        # print("Returning POST\n")
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Too bad\n")
        print(json.loads(response.content.decode('utf-8')))
        return None
