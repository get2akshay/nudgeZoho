from datetime import datetime
import requests
from time import sleep
from lib import db
import yaml
access_token = ""
refresh_token = ""
expires_in = 0
clientId = "1000.PPKI153U5EWZGDF9Z3LAQXKI3OA8GH"
clientSecret = "1a77f2b194027d1b35f0f73494c90b8965138d0307"
# 1000.39c2ea305b1b4f4fc8169850bdcd3b8c.cd63686c26bca7701cc6d9faa6ccce29
code = "1000.e2c8a274464cfa4467e76a6a98c26084.d70a7113a622272fa30b0e53b93f514f"
# set the request URL and parameters for token
token_url = "https://accounts.zoho.in/oauth/v2/token"

def generateToken():
    global access_token
    global refresh_token
    token_params = {
    "code": code,
    "client_id": "1000.JNR6PEB28PKC57GQ0VLB7WS9I5NURA",
    "client_secret": "7ca3162c9acf96a9a3259254854b18d3dce65c50da",
    "redirect_uri": "https://www.example.com/",
    "grant_type": "authorization_code"
    }
    # send a POST request and get the access token
    token_response = requests.post(token_url, params=token_params)
    try:
        access_token = token_response.json()["access_token"]
        refresh_token = token_response.json()["refresh_token"]
        expires_in = token_response.json()["expires_in"]
    except KeyError as k:
        if "invalid_code" in token_response.json()["error"]:
            print("Generate Code again!")
            tokenRenew()
            exit
# Attendence

def tokenRenew():
    global access_token
    global expires_in
    # global refresh_token
    #{Accounts_URL}/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token
    # token_url = "https://accounts.zoho.in/oauth/v2/token"
    if not refresh_token:
        print("manually add code")
    token_params = {
        "refresh_token": refresh_token,
        "client_id": "1000.JNR6PEB28PKC57GQ0VLB7WS9I5NURA",
        "client_secret": "7ca3162c9acf96a9a3259254854b18d3dce65c50da",
        "redirect_uri": "https://www.example.com/",
        "grant_type": "refresh_token"
    }
    # send a POST request and get the access token
    token_response = requests.post(token_url, params=token_params)
    try:
        access_token = token_response.json()["access_token"]
        expires_in = token_response.json()["expires_in"]
    except KeyError as k:
        print(f"Token renew failed with error {k}")


def timedelta(last_motion, seconds_delta):
    # get the current time as a datetime object
    now = datetime.now()
    # convert the epoch timestamp to a datetime object
    epoch_datetime = datetime.fromtimestamp(last_motion)
    # calculate the difference between the current time and the epoch time as a timedelta object
    delta = now - epoch_datetime
    # check if the delta is greater than 10 minutes
    if delta.total_seconds() > seconds_delta:
        # print the delta as a string
        return True
    else:
        return False

def checkinout(status, employee, timestamp):
    # generate token
    generateToken()
    print(f"Token is valid for {expires_in}")
    url = "https://people.zoho.in/people/api/attendance"
    # get the current date and time
    now = datetime.now()
    # format the date and time as dd/MM/yyyy HH:mm:ss
    date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
    params = {
    "dateFormat": "dd/MM/yyyy HH:mm:ss",
    status : date_time_str,
    "empId": employee
    }
    print(params)
    # set the authorization header with your Zoho OAuth token
    headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    # send a POST request and get the response
    response = requests.post(url, params=params, headers=headers)
    # print the response status code and content
    print(response.status_code)
    print(response.content)


employees = {"Rajesh Sharma": "00:8c:10:30:02:6f"}


with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)

#employees = {"Rajesh Sharma": "S2"}
# motionDetect = db.getxyz('00:8c:10:30:02:6f')
# from pdb import set_trace
# set_trace()
while True:
    for name, mac in employees.items():
        print(f"Checking motion status for {name} assigned badge {mac}")
        try:
            motionDetect = db.getxyz(mac)
            #motionDetect = db.getxyz('00:8c:10:30:02:6f')
            #motionDetect = (1, -80)
            print(motionDetect)
            if motionDetect[1] is not None: 
                if timedelta(motionDetect[0],43200):
                    checkinout("checkOut",mac,motionDetect[0])
                else:
                    checkinout("checkIn",mac, motionDetect[0])
        except TypeError as t:
            print(f"Badge {mac} not found in DB for {name}, check again !")
            continue
    sleep(10)
