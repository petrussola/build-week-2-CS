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
base_api_url_bc = os.getenv("BASE_API_URL_BC")
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


def api_call_post(endpoint, now, cooldown, payload=None):
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
    if payload is not None:
        response = requests.post(
            f"{base_api_url}{endpoint}", headers=headers, json=payload)
    else:
        response = requests.post(
            f"{base_api_url}{endpoint}", headers=headers)
    res = json.loads(response.content.decode('utf-8'))
    cooldown = res["cooldown"]
    now = datetime.now()
    print(f"Response status is: {response.status_code} <<")
    if response.status_code == 200:
        print("Returning POST\n")
        return [res, now, cooldown]
    else:
        print("Too bad\n")
        print(json.loads(response.content.decode('utf-8')))
        return [None, now, cooldown]


def api_call_get_timer(endpoint, now, cooldown):
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
    # print("Calling GET\n")
    response = requests.get(f"{base_api_url}{endpoint}", headers=headers)
    res = json.loads(response.content.decode('utf-8'))
    print(f"Response from get timer api call is:\n {res}")
    now = datetime.now()
    cooldown = res["cooldown"]
    if response.status_code == 200:
        # print("Returning GET\n")
        return [res, now, cooldown]
    else:
        print("Too bad\n")
        return [None, now, cooldown]

def api_call_get_timer_bc(endpoint, now, cooldown):
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
    # print("Calling GET\n")
    response = requests.get(f"{base_api_url_bc}{endpoint}", headers=headers)
    res = json.loads(response.content.decode('utf-8'))
    print(f"Response from get timer api call is:\n {res}")
    now = datetime.now()
    cooldown = res["cooldown"]
    if response.status_code == 200:
        # print("Returning GET\n")
        return [res, now, cooldown]
    else:
        print("Too bad\n")
        return [None, now, cooldown]

def api_call_post_bc(endpoint, now, cooldown, payload=None):
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
    if payload is not None:
        response = requests.post(
            f"{base_api_url_bc}{endpoint}", headers=headers, json=payload)
        print(f"Response from mine endpoint:\n {response.json()} \n")
    else:
        response = requests.post(
            f"{base_api_url_bc}{endpoint}", headers=headers)
    res = json.loads(response.content.decode('utf-8'))
    cooldown = res["cooldown"]
    now = datetime.now()
    print(f"Response status is: {response.status_code} <<")
    if response.status_code == 200:
        print("Returning POST\n")
        return [res, now, cooldown]
    else:
        print("Too bad\n")
        print(json.loads(response.content.decode('utf-8')))
        return [None, now, cooldown]