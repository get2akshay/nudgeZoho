import datetime
import requests
from time import sleep
from lib import db
import yaml
import numpy as np
# Import the decimal module
from decimal import Decimal
access_token = ""
refresh_token = ""
expires_in = 0
clientId = "1000.PPKI153U5EWZGDF9Z3LAQXKI3OA8GH"
clientSecret = "1a77f2b194027d1b35f0f73494c90b8965138d0307"
# 1000.39c2ea305b1b4f4fc8169850bdcd3b8c.cd63686c26bca7701cc6d9faa6ccce29
code = "1000.d0abd38a5d44c525b5ccd70b9d6062bb.cd9b4eeb0a4c46aa3c7adb8e52be8868"
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
    # print(f"Token is valid for {expires_in}")
    url = "https://people.zoho.in/people/api/attendance"
    params = {
    "dateFormat": "dd/MM/yyyy HH:mm:ss",
    status : dateFormat(timestamp),
    "empId": employee
    }
    # print(params)
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

def firstEntyCheckiIn(name, mac, start_date=None, end_date=None):
    # Use the date() method to get the date part of the datetime object
    # Use the datetime.datetime class to call the today() method
    start_time = datetime.datetime.today()
    # Use the date() method to get the date part of the datetime object
    start_time = start_time.date()
    # Combine the date with the minimum time
    if start_date is not None:
        start_time = start_date
    start_time = datetime.datetime.combine(start_time, datetime.time.min).strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if end_date is not None:
        end_time = end_date.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Getting Movement data from {start_time} to {end_time} for {name} with Badge {mac} !")
    data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    if data is not None:
        # Use list comprehension to filter out the tuples that have at least two non zero values in the last three elements
        filtered_list = [t for t in data if np.count_nonzero(t[-3:]) >= 2]
        # Use another list comprehension to extract the timestamp values (index 0) from the filtered list
        timestamp_list = [t[0] for t in filtered_list]
        # Print the timestamp list
        print(timestamp_list)
        try:
            # Create a datetime object from the epoch time
            dt = datetime.datetime.fromtimestamp(timestamp_list[0])
            # Format the datetime object using strftime
            chekinTime = dt.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Earliest Motion found for {name} with {mac} was {chekinTime} !")
            loginStatus = checkinout("checkIn", mac, timestamp_list[0])
            print(loginStatus)
        except IndexError as i:
            print(f"No movement detected for {name} and badge {mac}")
    

def lastMotionCheck(name, mac, start_date=None, end_date=None):
    # Use the date() method to get the date part of the datetime object
    # Get the current datetime object
    current_time = datetime.datetime.now()
    # Subtract one day from the current date
    previous_date = current_time.date() - datetime.timedelta(days=1)
    # Combine the previous date with the minimum time (00:00:00)
    if start_date is not None:
        previous_date = start_date
    start_time = datetime.datetime.combine(previous_date, datetime.time.min)
    # Format the start time using strftime
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    # Print the start time
    print(start_time)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if end_date is not None:
        end_time = end_date.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Getting Movement data from {start_time} to {end_time} for {name} with Badge {mac} !")
    data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    # Define the list of tuples
    # filter_value = Decimal('0E-9')
    if data is not None:
        # Use list comprehension to filter out the tuples that have at least two non zero values in the last three elements
        filtered_list = [t for t in data if np.count_nonzero(t[-3:]) >= 2]
        # Use another list comprehension to extract the timestamp values (index 0) from the filtered list
        timestamp_list = [t[0] for t in filtered_list]
        # Print the timestamp list
        print(timestamp_list)
        try:
            # Create a datetime object from the epoch time
            dt = datetime.datetime.fromtimestamp(timestamp_list[-1])
            # Format the datetime object using strftime
            chekioutTime = dt.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Last Motion found for {name} with {mac} was {chekioutTime} !")
            loginStatus = checkinout("checkOut", mac, timestamp_list[-1])
            print(loginStatus)
        except IndexError as i:
            print(f"No movement detected for {name} and badge {mac}")
        

def old_data(name, mac):
    #Missing time 
    missingTime = 1800
    # Define the start date as a datetime object
    start_time = datetime.datetime(2023, 12, 1, 9, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    # Define the end date as a datetime object by adding 30 days to the start date
    end_time = datetime.datetime(2023, 12, 31, 2, 5, 0).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Getting Old Movement data from {start_time} to {end_time} for {name} with Badge {mac} !")
    data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    if data is not None:
        # Use list comprehension to filter out the tuples that have at least two non zero values in the last three elements
        filtered_list = [t for t in data if np.count_nonzero(t[-3:]) >= 2]
        # Use another list comprehension to extract the timestamp values (index 0) from the filtered list
        timestamp_list = [t[0] for t in filtered_list]
        # Print the timestamp list
        try:
            list(set(timestamp_list.sort()))
        except TypeError as t:
            print(f"Time stamp empty for {name} with {mac} in the period {start_time} to {end_time} !")
        print(timestamp_list)
        # Loop through the list of timestamps
        for index, ts in enumerate(timestamp_list):
            # Convert the current and next timestamps to datetime objects
            # Call the function with the appropriate arguments
            if index == 0:
                # First checkin with the earliest timestamp
                loginStatus = checkinout("checkIn", mac, timestamp_list[index])
            else:
                # Checkout and checkin with the subsequent timestamps
                try:
                    # Calculate the time difference in seconds
                    time_diff = (timestamp_list[index + 1] - timestamp_list[index])
                    # Print the time difference
                    print(f"The time difference between {timestamp_list[index + 1]} and {timestamp_list[index]} is {time_diff} seconds.")
                    # Check if the time difference is more than 1800 seconds
                    if time_diff > missingTime:
                        # Call the checkout function
                        loginStatus = checkinout("checkOut", mac, timestamp_list[index] + missingTime)
                        print(f"Making checkOut for OLd time stamp {loginStatus}")
                    # Call the checkinout function with the appropriate arguments
                    loginStatus = checkinout("checkIn", mac, ts)
                    print(f"Making checkIn for OLd time stamps {loginStatus}")
                    if index == len(timestamp_list) - 1:
                        # this is the last index loop
                        loginStatus = checkinout("checkOut", mac, timestamp_list[index] + missingTime)
                except IndexError as i:
                    print(f"No movement detected for {name} and badge {mac}")
                    # Loop through the list of datetime objects
            

# Define the time range
checkout_check_start_time = datetime.time(5, 0, 0) # 0500 hours
checkout_check_end_time = datetime.time(5, 30, 0) # 0530 hours
# Start the loop
count = 0
while True:
    # Get the current time
    current_time = datetime.datetime.now().time()
    for name, mac in employees.items():
         # Check if the current time is within the time range
        if checkout_check_start_time <= current_time <= checkout_check_end_time:
        # Run the first function
            # lastMotionCheck(name, mac)
            pass
        else:
        # Run the second function
            # firstEntyCheckiIn(name, mac)
            pass
        #Settle old data
        if count < 3:
            old_data(name, mac)
            count+=1
        # Pause the loop for 10 seconds
        sleep(10)