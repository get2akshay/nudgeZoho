import datetime
import requests
from time import sleep
from lib import db
import yaml
import numpy as np
access_token = ""
refresh_token = ""
expires_in = 0
clientId = "1000.PPKI153U5EWZGDF9Z3LAQXKI3OA8GH"
clientSecret = "1a77f2b194027d1b35f0f73494c90b8965138d0307"
# 1000.39c2ea305b1b4f4fc8169850bdcd3b8c.cd63686c26bca7701cc6d9faa6ccce29
code = "1000.bc9f76e0a5bfa8ea0e9b6536ab331c41.78d45c018546b5076ce29a8614e76b01"
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

def dateFormat(timestamp):
    # Create a datetime object from the epoch time stamp
    date_time = datetime.datetime.fromtimestamp(timestamp)
    # Format the datetime object as a string
    return date_time.strftime("%d/%m/%Y %H:%M:%S")


def parseExistingCheckin(data):
    # Load the JSON data from the string
    # Access the checkin time stamp from the JSON data
    checkin_time = data["response"]["result"][0]["entries"][0]["2020-06-06"]["singleRegEntries"]["checkInTime"]
    # Parse the checkin time stamp to a datetime object
    checkin_datetime = datetime.datetime.strptime(checkin_time, '%d-%b-%Y %H:%M:%S')
    # Convert the datetime object to epoch time
    checkin_epoch = checkin_datetime.timestamp()
    # Print the epoch time as an integer
    print(int(checkin_epoch))


def timedelta(last_motion, seconds_delta):
    # get the current time as a datetime object
    now = datetime.datetime.now()
    # convert the epoch timestamp to a datetime object
    epoch_datetime = datetime.datetime.fromtimestamp(last_motion)
    # calculate the difference between the current time and the epoch time as a timedelta object
    delta = now - epoch_datetime
    # check if the delta is greater than 10 minutes
    if delta.total_seconds() > seconds_delta:
        # print the delta as a string
        return True
    else:
        return False

def getStatusLogin(duration):
    """https://people.zoho.com/api/attendance/fetchLatestAttEntries?duration=5&dateTimeFormat=dd-MM-yyyy HH:mm:ss"""
    # Define the Zoho API endpoint
    generateToken()
    print(f"Token is valid for {expires_in}")
    url = "https://people.zoho.in/api/attendance/fetchLatestAttEntries"
    # Define the query parameters
    params = {
        "duration": duration,
        "dateTimeFormat": "dd-MM-yyyy HH:mm:ss"
    }
    # Define the authorization header
    headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    # Send a GET request and get the response
    response = requests.get(url, params=params, headers=headers)

    # Check the status code and the content
    if response.status_code == 200:
            return response.json()
            # Do something with the data
    else:
        # Print the error message
        print(f"Error: {response.status_code} - {response.reason}")

    


def checkinout(status, employee, timestamp):
    # generate token
    generateToken()
    print(f"Token is valid for {expires_in}")
    url = "https://people.zoho.in/people/api/attendance"
    params = {
    "dateFormat": "dd/MM/yyyy HH:mm:ss",
    status : dateFormat(timestamp),
    "empId": employee
    }
    print(params)
    # set the authorization header with your Zoho OAuth token
    headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    # send a POST request and get the response
    response = requests.post(url, params=params, headers=headers)
    # Check the status code and the content
    if response.status_code == 200:
            return response.json()
            # Do something with the data
    else:
        # Print the error message
        print(f"Error: {response.status_code} - {response.reason}")


with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)

#employees = {"Rajesh Sharma": "S2"}
# motionDetect = db.getxyz('00:8c:10:30:02:6f')
# from pdb import set_trace
# set_trace()


for name, mac in employees.items():
    # Use the date() method to get the date part of the datetime object
    # Use the datetime.datetime class to call the today() method
    start_date = datetime.datetime.today()
    # Use the date() method to get the date part of the datetime object
    start_date = start_date.date()
    # Combine the date with the minimum time
    start_date = datetime.datetime.combine(start_date, datetime.time.min).strftime("%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Getting Movement data from {start_date} to {end_date} for {name} with Badge {mac} !")
    data = db.motionInSpecifiedTimePeriod(mac, start_date, end_date)
    # Import the decimal module
    from decimal import Decimal
    # Define the list of tuples
    filter_value = Decimal('0E-9')
    # Use list comprehension to filter out the tuples that have at least two non zero values in the last three elements
    filtered_list = [t for t in data if np.count_nonzero(t[-3:]) >= 2]
    # Use another list comprehension to extract the timestamp values (index 0) from the filtered list
    timestamp_list = [t[0] for t in filtered_list]
    # Print the timestamp list
    print(timestamp_list)
    try:
        chekinTime = timestamp_list[0].strftime("%Y-%m-%d %H:%M:%S")
        print(f"Earliest Motion found for {name} with {mac} was {chekinTime} !")
        loginStatus = checkinout("checkIn", mac, timestamp_list[0])
        print(loginStatus)
    except IndexError as i:
        print(f"No movement detected for {name} and badge {mac}")

    



""" 
for name, mac in employees.items():
    print(f"Checking motion status for {name} assigned badge {mac}")
    motionDetect = sorted(db.getxyzSpecifictime(mac))
    print(motionDetect)
    timestamps = sorted(motionDetect)
    logindata = getStatusLogin(5)
    print(logindata)
    # Parse the JSON string and create a Python object
    # Access the result key from the Python object
    try:
        result = logindata["response"]["result"]
        # Do something with result
         # Get the length of the result list
        length = len(result)
        # Check if the length is zero or not
        if length == 0 and len(logindata) != 0:
            # Print a message that the result key is empty
            print("No checkin data found, continue to checkin!")
            loginStatus = checkinout("checkIn", mac, timestamps[0])
        else:
            # Print a message that the result key has content
            print(f"The result key has {length} items.")
    except TypeError as e:
        print(f"The logindata is None: {e}")
        continue
    except IndexError as i:
        print(f"No timestamp data for badge, so the error: {i}")
        continue

 """


""" while True:
    for name, mac in employees.items():
        print(f"Checking motion status for {name} assigned badge {mac}")
        try:
            #motionDetect = db.getxyz(mac)
            motionDetect = sorted(db.getxyzSpecifictime(mac))
            if "checkOut" in loggedInStatus[mac]:
                checkinout("checkIn",mac,motionDetect[0])
                loggedInStatus[mac] = "checkIn"
            if timedelta(motionDetect[-1],600) and "checkIn" in loggedInStatus[mac]:
                now = datetime.now()
                checkinout("checkOut",mac,now)
            
        except TypeError as t:
            print(f"Badge {mac} not found in DB for {name}, check again !")
            continue
        except IndexError as i:
            print(f"No motion points for {mac}")
            continue
    sleep(10) """
