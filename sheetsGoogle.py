import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from lib import db
import numpy as np
import yaml
from time import sleep
from collections import defaultdict
#Sheet to update
spreadsheet_id = '1ipzQMruFXD0RMp2enGecLraYxDSIVxQXg1Pa4TPMxno'
NEW_SHEET_NAME = "tid"
# Load your service account credentials from the JSON file
credentials_file = 'service_account.json'
credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/spreadsheets'])
# Create a service object for Google Sheets API
service = build('sheets', 'v4', credentials=credentials)

def checkSheet(sheet_name):
    # Check if the sheet exists
    try:
        sheet_info = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_properties = sheet_info.get('sheets', [])
        sheet_names = [sheet['properties']['title'] for sheet in sheet_properties]
        if sheet_name in sheet_names:
            print(f"The sheet '{sheet_name}' already exists.")
            return True
            # You can return True here if needed
        else:
            # Create a new sheet with the specified name
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    'requests': [{
                        'addSheet': {
                            'properties': {'title': sheet_name}
                        }
                    }]
                }
            ).execute()
            print(f"Created a new sheet named '{sheet_name}'.")
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False


def addData(data):
    sheet_name = data[0]
    # Find the sheet ID
    sheet_info = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_properties = sheet_info.get('sheets', [])
    sheet_id = None
    for sheet in sheet_properties:
        if sheet['properties']['title'] == sheet_name:
            sheet_id = sheet['properties']['sheetId']
            break
    if not sheet_id:
        print(f"The sheet '{sheet_name}' does not exist. Will create!")
        checkSheet(sheet_name)
    
    # Get the last row number with data in the specified sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A:A',
        valueRenderOption='UNFORMATTED_VALUE'
    ).execute()
    values = result.get('values', [])
    next_row = len(values) + 1
    
    # Construct the request to update the sheet with the provided data
    body = {
        'values': [data],  # Assume data is a list of values to be added to each column
    }
    range_name = f'{sheet_name}!A{next_row}'
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print(f"Added data to '{sheet_name}' in row {next_row}.")


def dateFormat(timestamp):
    # Create a datetime object from the epoch time stamp
    date_time = datetime.datetime.fromtimestamp(timestamp)
    # Format the datetime object as a string
    return date_time.strftime("%d/%m/%Y %H:%M:%S")

def remove_duplicates_dict(input_list):
    my_dict = defaultdict(int)
    for num in input_list:
        if my_dict[num] == 0:
            my_dict[num] = 1
        else:
            input_list.remove(num)
    return input_list




def workHourRecord(name, mac, YYYY, MM, DD, HH, shift_hours):
    #Missing time 
    missingTime = 1800
    # Define the start date as a datetime object
    start_time = datetime.datetime(YYYY, MM, DD, HH, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    # Define the end date as a datetime object by adding 30 days to the start date
    if HH + shift_hours > 23:
        DD = DD + 1
    end_time = datetime.datetime(YYYY, MM, DD, 3, 30, 0).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Getting Old Movement data from {start_time} to {end_time} for {name} with Badge {mac} !")
    data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    if data is not None:
        # Use list comprehension to filter out the tuples that have at least two non zero values in the last three elements
        filtered_list = [t for t in data if np.count_nonzero(t[-3:]) >= 2]
        # Use another list comprehension to extract the timestamp values (index 0) from the filtered list
        timestamp_list = [t[0] for t in filtered_list]
        # Print the timestamp list
        try:
            unique = list(set(timestamp_list))
            # print("The list after removing duplicates:", unique)
            return unique
        except TypeError as t:
            print(f"Time stamp empty for {name} with {mac} in the period {start_time} to {end_time} !")


def prepRecords(name, mac, missingSeconds):
    record = sorted(workHourRecord(name, mac, 2023, 12, 1, 9, 15))
    c = 0
    m = 0
    records = {"FirstMoveOfTheDay": None, "LastMoveOfTheDay": record[-1]}  # Initialize the key
    while c < len(record) - 1:
        delta = record[c + 1] - record[c]
        if delta > missingSeconds:
            print("Not the first check-in!")
        elif delta < missingSeconds and records["FirstMoveOfTheDay"] is None:
            records["FirstMoveOfTheDay"] = record[c]
        else:
            records[f"Move{m}"] = record[c]
            m += 1
        c += 1
    return records


with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)

missingSeconds = 1800
for name, mac in employees.items():
    records = prepRecords(name, mac, missingSeconds)
    # Example usage
    checkin = records['FirstMoveOfTheDay']
    checkout = records["LastMoveOfTheDay"]
    hours = (checkout - checkin) / 3600
    data_to_add = [name, mac, dateFormat(checkin), dateFormat(checkout), hours]  # Provide the data to be added to each column
    addData(data_to_add)




