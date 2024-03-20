

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
test = True
if not test:
    from lib import db
import numpy as np
import yaml
from time import sleep
from collections import defaultdict
import pdb
import logging
offset = 0
tollarance = 1800

tdd = [1706779963, 1706780640, 1706790586, 1706792442, 1706792448, 1706792770, 1706793326, 1706795112, 1706795114, 1706799685, 1706801012, 1706802195, 1706802210, 1706802296, 1706802471, 1706802472, 1706803193, 1706803820, 1706804712, 1706806236, 1706806238, 1706806552, 1706806572, 1706806574, 1706806689, 1706806691, 1706806693, 1706806699, 1706806700, 1706807178, 1706807180, 1706807968, 1706807972, 1706808217, 1706808251, 1706808269, 1706808291, 1706808318, 1706808320, 1706809142, 1706809653, 1706809655, 1706812381, 1706812384, 1706812386, 1706812910]    


#Sheet to update
#https://docs.google.com/spreadsheets/d/1Upm2saIcs3A6Cij5YdHA1KgIwj6yEfHW90lfA8aavnQ/edit#gid=903908714
spreadsheet_id = '1Upm2saIcs3A6Cij5YdHA1KgIwj6yEfHW90lfA8aavnQ'
NEW_SHEET_NAME = "Automatic"
# Load your service account credentials from the JSON file
credentials_file = 'service_account.json'
credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/spreadsheets'])
# Create a service object for Google Sheets API
service = build('sheets', 'v4', credentials=credentials)

def format_end_dates(manual_date_str=None):
    # Get the current date and time
    current_date = datetime.datetime.now()

    if manual_date_str:
        # Parse the manually passed date
        return datetime.datetime.strptime(manual_date_str, "%Y-%m-%d %H:%M:%S")
    else:
        # Use the current date if no manual date is provided
        return current_date

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
    return date_time.strftime("%d/%m/%Y %H:%M:%S")

def remove_duplicates_dict(input_list):
    my_dict = defaultdict(int)
    for num in input_list:
        if my_dict[num] == 0:
            my_dict[num] = 1
        else:
            input_list.remove(num)
    return input_list

def workHourRecordold(name, mac, YYYY, MM, DD, HH, shift_hours):
    unique = []
    # Define the start date as a datetime object
    start_time = datetime.datetime(YYYY, MM, DD, HH, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    # Define the end date as a datetime object by adding 30 days to the start date
    DD = DD + 1
    try:
        end_time = datetime.datetime(YYYY, MM, DD, 3, 30, 0).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Getting Old Movement data from {start_time} to {end_time} for {name} with Badge {mac} !")
        data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    except ValueError as v:
        print(f"All Month days done, caught error {v}")
        return unique
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


def extract_datetime_components(date_obj, offset_minutes=offset):
    try:
        # Parse the input date string
        # dt_nooffset = datetime.datetime.strptime(date_obj, "%Y-%m-%d %H:%M:%S")

        # Add the offset to the datetime
        dt = date_obj + datetime.timedelta(minutes=offset_minutes)

        # Extract individual components
        YYYY = dt.year
        MM = dt.month
        DD = dt.day
        HH = dt.hour
        mm = dt.minute
        ss = dt.second

        return YYYY, MM, DD, HH, mm, ss
    except ValueError:
        # Handle invalid date string format
        return None


def workHourRecord(mac, ist_start_date, test=False):
    YYYY, MM, DD, HH, mm, ss = extract_datetime_components(ist_start_date)
    if test:
        from lib import helper
        return helper.generate_timestamps(YYYY, MM, DD, HH)
    unique = []
    # Define the start date as a datetime object
    start_time = datetime.datetime(YYYY, MM, DD, HH, mm, ss).strftime("%Y-%m-%d %H:%M:%S")
    # Define the end date as a datetime object by adding 30 days to the start date
    DD = DD + 1
    try:
        end_time = datetime.datetime(YYYY, MM, DD, 2, mm, ss).strftime("%Y-%m-%d %H:%M:%S")
        # print(f"Getting Old Movement data from {start_time} to {end_time} Badge {mac} !")
        data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    except ValueError as v:
        # print(f"All Month days done, caught error {v}")
        return unique
    if data is not None:
        # Use list comprehension to filter out the tuples that have at least two non zero values in the last three elements
        filtered_list = [t for t in data if np.count_nonzero(t[-3:]) >= 1]
        # Use another list comprehension to extract the timestamp values (index 0) from the filtered list
        timestamp_list = [t[0] for t in filtered_list]
        # Print the timestamp list
        try:
            unique = list(set(timestamp_list))
            # print("The list after removing duplicates:", unique)
            return unique
        except TypeError as t:
            # print(f"Time stamp empty for {mac} in the period {start_time} to {end_time} !")
            return unique


def prepRecords(name, mac, ist_start_date, shift_hours, missingSeconds):
    YYYY, MM, DD, HH, mm, ss = extract_datetime_components(ist_start_date)
    records = {}
    records.update({"FirstMoveOfTheDay": None, "LastMoveOfTheDay": None})
    timestamp_list = sorted(workHourRecord(name, mac, YYYY, MM, DD, HH, shift_hours))
    offfloor = 0
    if timestamp_list is not None and len(timestamp_list) > 0:
        if len(timestamp_list) < 2:
            logging.info(f"Very less movement for {mac} on {ist_start_date}")
            return True
        elif len(timestamp_list) == 2:
            logging.debug(f"Two movement data for {mac} on {ist_start_date}")
            return True
        for idx, timestamp in enumerate(sorted(timestamp_list)):
            if idx == 0:
                # First timestamp, mark as check-in
                records.update({"FirstMoveOfTheDay": timestamp_list[0]})
                continue
            elif idx == len(timestamp_list) - 1:
                # Last timestamp, mark as check-out
                records.update({"LastMoveOfTheDay": timestamp_list[-1]})
                break
            else:
                time_diff = timestamp - timestamp_list[idx - 1]
                if time_diff > tollarance:
                    offfloor += time_diff
                    records.update({"OffFloor": offfloor })
    return records

with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)

def processData(ist_start_date, shift_hours=12, missingSeconds=1800):
    YYYY, MM, DD, HH, mm, ss = extract_datetime_components(ist_start_date)
    for name, mac in employees.items():
        day_move = {}
        day_move.update({"FirstMoveOfTheDay": None, "LastMoveOfTheDay": None})  # Initialize the key
        # Get Data filled date
        day_move.update(prepRecords(name, mac, ist_start_date, shift_hours, missingSeconds))
        # name, mac, missingSeconds, YYYY, MM, DD, HH, MS
        # Month
        month = monthReturn(MM)
        # Example usage
        checkin = day_move.get("FirstMoveOfTheDay")
        date_time_obj = datetime.strptime(dateFormat(checkin), "%m/%d/%Y %H:%M:%S")
        # Extract date and time components
        in_date = date_time_obj.date()
        in_time = date_time_obj.time()
        checkout = day_move.get("LastMoveOfTheDay")
        date_time_obj = datetime.strptime(dateFormat(checkout), "%m/%d/%Y %H:%M:%S")
        # Extract date and time components
        out_date = date_time_obj.date()
        out_time = date_time_obj.time()
        offfloor = day_move.get("OffFloor")
        if checkin is None or checkout is None:
            total_hours = 0
        else:
            total_hours = (checkout - checkin) / 3600
        activehours = total_hours - offfloor
        data_to_add = [name, mac, month, in_date, in_time, out_date, out_time, total_hours, activehours]  # Provide the data to be added to each column
        addData(data_to_add)

# processData(YYYY=2024, MM=3, DD=1, HH=8, shift_hours=12, missingSeconds=1800, days_in_month=31)
        
# Given IST start date string
ist_start_date_str = "2024-02-1 07:00:00"
ist_start_date = datetime.datetime.strptime(ist_start_date_str, "%Y-%m-%d %H:%M:%S")
# Get the current date
# Example usage:
end_date_str = "2024-03-21 02:00:00"
ist_end_date = format_end_dates(end_date_str)
# Increment the date until the current day
logging.info("Starting DB Parsing")
while ist_start_date.date() <= ist_end_date.date():
    for mac in employees.values():
        logging.info(f"Getting Data for {mac} from {ist_start_date.date()} To {ist_end_date.date()} !")
        processData(ist_start_date, shift_hours=12, missingSeconds=tollarance)
    ist_start_date += datetime.timedelta(days=1)
