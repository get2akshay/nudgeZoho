import requests
from datetime import datetime, timedelta
import time
from time import sleep
import json
import logging
params = dict()
result = dict()
import pdb

#Time span
def timespan_seconds(seconds_delta):
    # Calculate timestamps for 'from' and 'to' parameters
    now = datetime.utcnow()
    delta_in_seconds = now - timedelta(seconds=seconds_delta)
    from_timestamp = int(delta_in_seconds.timestamp() * 1000)  # Convert to milliseconds
    to_timestamp = int(now.timestamp() * 1000)  # Convert to milliseconds
    # logging.debug(from_timestamp, to_timestamp)
    return from_timestamp, to_timestamp

#ThingsBoard
base_url = "http://65.20.78.99:8080/api/"
get_url = f"{base_url}plugins/telemetry/DEVICE/1747e250-5a29-11ee-b96b-53725f09012e/values/timeseries"
headers = {
    "Content-Type": "application/json",
}
# Generate fresh JWT token
def jwttoken():
    """curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"username":"tenant@thingsboard.org", "password":"tenant"}' 'http://THINGSBOARD_URL/api/auth/login'"""
    params = {
        "username": "tenant@thingsboard.org",
        "password": "akshay911"
    }
    response = requests.post(f"{base_url}auth/login", headers=headers, json=params)
    if response.status_code == 200:
        # Parse the JSON response.
        token = response.json()
        return token["token"]
    else:
        print(f"Failed to fetch JWT Token! Status code: {response.status_code}")

#Get method
def rest_get():
    # print(params)
    response = requests.get(get_url, headers=headers, params=params)
    # Check if the request was successful (HTTP status code 200).
    if response.status_code == 200:
        # Parse the JSON response.
        telemetry_data = response.json()
        # Process the telemetry data as needed.
        return telemetry_data
    else:
        logging.debug(f"Failed to fetch telemetry data. Status code: {response.status_code}")

def visible_tag(seconds_delta):
    """http://65.20.78.99:8080/api/plugins/telemetry/DEVICE/1747e250-5a29-11ee-b96b-53725f09012e/values/timeseries"""
    global params
    startTs, endTs = timespan_seconds(seconds_delta)
    params = {
    "keys": "mac,uuid,major,minor,rssi,anchor",  # Replace with the telemetry keys you want to retrieve.
    "startTs": startTs,  # Replace with the start timestamp.
    "endTs": endTs,      # Replace with the end timestamp.
    }
    return rest_get()

def latest_tag_status():
    """http://65.20.78.99:8080/api/plugins/telemetry/DEVICE/1747e250-5a29-11ee-b96b-53725f09012e/values/timeseries"""
    global params
    params = {
    "keys": "mac,uuid,major,minor,rssi,anchor",  # Replace with the telemetry keys you want to retrieve.
    }
    return rest_get()

def last_captured(max_span): # max_span is in hours
    """http://65.20.78.99:8080/api/plugins/telemetry/DEVICE/1747e250-5a29-11ee-b96b-53725f09012e/values/timeseries"""
    min = last_available = 20 #Seconds
    span = 20
    dic = visible_tag(min)
    while True:
        if dic:
            global result
            result = dic
            logging.info(f"Tag was on floor {last_available} seconds before!")
            return last_available
        else:
            last_available = min + span
            dic = visible_tag(last_available)
            if last_available > (max_span * 60 * 60):
                logging.info(f"Tag is not on the floor for {max_span} hours!")
                return last_available

def uuidChanging():
    """{'rssi': [{'ts': 1695577502222, 'value': '-61'}], 'name': [{'ts': 1695577502222, 'value': 'Black Box'}], 'ID': [{'ts': 1695577502222, 'value': '76'}], 'major': [{'ts': 1695577502222, 'value': '10000'}], 'minor': [{'ts': 1695577502222, 'value': '0'}], 'power': [{'ts': 1695577502222, 'value': '-59'}], 'mac': [{'ts': 1695577502222, 'value': '00:8c:10:30:02:6f'}], 'uuid': [{'ts': 1695577502222, 'value': '00000000-0000-0000-0000-00000c406400'}], 'anchor': [{'ts': 1695495047871, 'value': ''}]}"""
    # Extract the initial uuid
    previous_uuid = ""
    initial_uuid = ""
    count = 0
    while True:
        result = latest_tag_status()
        if result:
            initial_uuid = result['uuid'][0]['value']
        # Check if the UUID has changed
        if previous_uuid != str(initial_uuid):
            print("UUID has changed:", result['uuid'][0]['value'])
        else:
            print("UUID has not changed:", result['uuid'][0]['value'])
        previous_uuid = initial_uuid
        # Simulate a delay (you can replace this with actual data updates)
        time.sleep(5)  # Check every 5 seconds

timespan_seconds(20)
JWT_token = jwttoken()
# Add the access token to the headers if it's required.
if JWT_token:
    headers["X-Authorization"] = f"Bearer {JWT_token}"
# visible_tag(5)
# print(last_captured(8))
# print(result)
# stationed_moving(20)
uuidChanging()