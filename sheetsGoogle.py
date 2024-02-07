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
import pdb

#Sheet to update
spreadsheet_id = '1ipzQMruFXD0RMp2enGecLraYxDSIVxQXg1Pa4TPMxno'
NEW_SHEET_NAME = "tid"
# Load your service account credentials from the JSON file
credentials_file = 'service_account.json'
credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/spreadsheets'])
# Create a service object for Google Sheets API
service = build('sheets', 'v4', credentials=credentials)

def monthReturn(number):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return months[number - 1]

def get_last_row_date_day(name):
    try:
        # Specify the range to read (column D)
        range_name = f"{name}!D:D"
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return None

        # Get the last row entry (assuming the data is sorted by date)
        last_row_entry = values[-1][0]

        # Parse the date string
        date_str = last_row_entry.split()[0]  # Assuming the format is "12/05/2023 0:21:28"
        date_obj = datetime.datetime.strptime(date_str, '%m/%d/%Y')

        # Get the day number
        day_number = date_obj.day
        return day_number

    except Exception as e:
        print(f"Error reading data: {e}")
        return None

def datetime_to_epoch(datetime_str):
    try:
        dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        epoch_time = int(dt.timestamp())
        return epoch_time
    except ValueError:
        return None

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
    if timestamp is None:
        return None
    # Create a datetime object from the epoch time stamp
    date_time = datetime.datetime.fromtimestamp(timestamp)
    # Format the datetime object as a string
    return date_time.strftime("%m/%d/%Y %H:%M:%S")

def remove_duplicates_dict(input_list):
    my_dict = defaultdict(int)
    for num in input_list:
        if my_dict[num] == 0:
            my_dict[num] = 1
        else:
            input_list.remove(num)
    return input_list




def workHourRecord(name, mac, YYYY, MM, DD, HH, shift_hours):
    unique = []
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
            return unique


def prepRecords(name, mac, YYYY, MM, DD, HH, shift_hours, missingSeconds):
    records = {}
    records.update({"FirstMoveOfTheDay": None, "LastMoveOfTheDay": None})
    record = sorted(workHourRecord(name, mac, YYYY, MM, DD, HH, shift_hours))
    if len(record) == 0:
        datetime_str = datetime.datetime(YYYY, MM, DD, HH, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        records.update({"FirstMoveOfTheDay": datetime_to_epoch(datetime_str)})
        datetime_str = datetime.datetime(YYYY, MM, DD+1, 3, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        records.update({"LastMoveOfTheDay": datetime_to_epoch(datetime_str)})
        return records
    else:
        c = 0
        k = 0
        while c < len(record) - 1:
            delta = record[c + 1] - record[c]
            if delta > missingSeconds:
                records.update({"From": record[c], "To": record[c + 1]}) 
            elif delta < missingSeconds and records.get("FirstMoveOfTheDay") is None:
                records.update({"FirstMoveOfTheDay": record[c]})
            else:
                records[f"Move{k}"] = record[c]
                k += 1
            c += 1
            if c == (len(record) - 1):
                records = {"LastMoveOfTheDay": record[c]}  # Initialize the key
        if records.get("FirstMoveOfTheDay") is None:
            records.update({"FirstMoveOfTheDay": record[0]})
        else:
            return records


with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)


def processData(YYYY=2023, MM=12, DD=1, HH=9, shift_hours=12, missingSeconds=1800, days_in_month=30):
    while start_day <= days_in_month:
        for name, mac in employees.items():
            day_move = {}
            day_move.update({"FirstMoveOfTheDay": None, "LastMoveOfTheDay": None})  # Initialize the key
            # Get Data filled date
            last_day_number = get_last_row_date_day(name)
            if last_day_number:
                print(f"Last row date day number: {last_day_number}")
            else:
                print("Error retrieving data.")
            day_move.update(prepRecords(name, mac, YYYY, MM, DD, HH, shift_hours, missingSeconds))
            # name, mac, missingSeconds, YYYY, MM, DD, HH, MS
            # Month
            month = monthReturn(MM)
            # Example usage
            checkin = day_move.get("FirstMoveOfTheDay")
            checkout = day_move.get("LastMoveOfTheDay")
            hours = 0
            if checkin is None or checkout is None:
                hours = 0
            else:
                hours = (checkout - checkin) / 3600
            status = "OFF"
            if hours == 0:
                status = "OFF"
            elif 0 < hours < 3:
                status = "UH"
            elif 3 < hours < 6:
                status = "HD"
            elif 6 < hours < 9:
                status = "FD"
            elif 9 < hours < 12:
                status = "OT"
            data_to_add = [name, mac, month, dateFormat(checkin), dateFormat(checkout), hours, status]  # Provide the data to be added to each column
            addData(data_to_add)
        start_day += 1 #Increment for each day work calc



processData(YYYY=2023, MM=12, DD=1, HH=8, shift_hours=12, missingSeconds=1800, days_in_month=31)






