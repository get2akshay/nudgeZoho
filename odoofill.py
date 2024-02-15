
import datetime
from lib import db
import numpy as np
from lib import odoo
from pdb import set_trace
import time

def dateFormatOdoo(timestamp):
    # Create a datetime object from the epoch time stamp
    date_time = datetime.datetime.fromtimestamp(timestamp)
    # Format the datetime object as a string
    return date_time.strftime("%Y-%m-%d %H:%M:%S")

# Define the method that takes an epoch time stamp as an argument
def epoch_to_datetime(epoch):
  # Convert the epoch time stamp to a datetime object
  dt = datetime.datetime.fromtimestamp(epoch)
  # Format the datetime object as a string
  dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
  # Return the formatted string
  return dt_str

def workHourRecord(mac, YYYY, MM, DD, HH):
    unique = []
    # Define the start date as a datetime object
    start_time = datetime.datetime(YYYY, MM, DD, HH, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    # Define the end date as a datetime object by adding 30 days to the start date
    DD = DD + 1
    try:
        end_time = datetime.datetime(YYYY, MM, DD, 3, 30, 0).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Getting Old Movement data from {start_time} to {end_time} Badge {mac} !")
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
            print(f"Time stamp empty for {mac} in the period {start_time} to {end_time} !")
            return unique

mac = '00:8c:10:30:02:6f'
timestamp_list = []
timestamp_list = workHourRecord(mac, YYYY=2024, MM=2, DD=1, HH=8)
kvs = odoo.verify_existing_checkin(mac)
for atdid, checkin in kvs.items():
    timestamp_obj = datetime.datetime.strptime(checkin, '%Y-%m-%d %H:%M:%S')
    timestamp_epoch = int(time.mktime(timestamp_obj.timetuple()))
    print(f"Current checked In Time {checkin} and its Epoch {timestamp_epoch}")



"""

def checkOutExistingCheckin(mac):
    checkins = odoo.get_checkin(mac)
    if len(checkins) > 0:
        timestamp_obj = datetime.datetime.strptime(checkins[0], '%Y-%m-%d %H:%M:%S')
        timestamp_epoch = int(time.mktime(timestamp_obj.timetuple()))
        epoch_time = timestamp_epoch + (4 * 60 * 60)
        # loginStatus = odoo.mark_attendance('check_out', mac, epoch_to_datetime(epoch_time))
        odoo.auto_checkout('00:8c:10:30:02:6f', epoch_time)
        return True
    return False


mac = '00:8c:10:30:02:6f'
# checkOutExistingCheckin(mac)
timestamp_list = []
timestamp_list = workHourRecord(mac, YYYY=2024, MM=2, DD=1, HH=8)
timestamp_list.sort()
tolrance = 30
# odoo.mark_attendance('check_in', mac, epoch_to_datetime(min(timestamp_list)))
# Loop through the list and compare each timestamp with the previous one
for i in range(len(timestamp_list)):
    # Convert the timestamp to a datetime object
    dt = datetime.datetime.fromtimestamp(timestamp_list[i])
    # If it is the first timestamp, print the start time
    if i == 0:
        print(f"Start time: {dt}")
        odoo.mark_attendance('check_in', mac, epoch_to_datetime(timestamp_list[i]))
    # Otherwise, calculate the time difference with the previous timestamp
    else:
        # Convert the previous timestamp to a datetime object
        prev_dt = datetime.datetime.fromtimestamp(timestamp_list[i-1])
        # Calculate the time delta in minutes
        delta = (dt - prev_dt) / datetime.timedelta(minutes=1)
        # Print the time delta
        print(f"Time delta: {delta} minutes")
        if delta > tolrance:
            odoo.mark_attendance('check_out', mac, epoch_to_datetime(timestamp_list[i]))
    # If it is the last timestamp, print the final checkout time
    if i == len(timestamp_list) - 1:
        print(f"Final checkout time: {dt}")
        odoo.mark_attendance('check_out', mac, epoch_to_datetime(timestamp_list[i]))



"""


"""

timestamp_list = []
timestamp_list = workHourRecord(mac, YYYY=2024, MM=2, DD=1, HH=8)  
missingTime = 30
set_trace()
checkins = odoo.get_checkin(mac)
if len(checkins) > 0:
    timestamp_obj = datetime.datetime.strptime(checkins[0], '%Y-%m-%d %H:%M:%S')
    timestamp_epoch = int(time.mktime(timestamp_obj.timetuple()))
    epoch_time = datetime.datetime.now().timestamp()
    if (epoch_time - timestamp_epoch) > missingTime:
        odoo.auto_checkout('00:8c:10:30:02:6f', missingTime)
else:
    for index, ts in enumerate(timestamp_list):
        # Convert the current and next timestamps to datetime objects
        # Call the function with the appropriate arguments
        if index == 0:
            # First checkin with the earliest timestamp
            # loginStatus = checkinout("checkIn", mac, timestamp_list[index])
            loginStatus = odoo.mark_attendance('check_in', mac, epoch_to_datetime(timestamp_list[index]))
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
                    # loginStatus = checkinout("checkOut", mac, timestamp_list[index] + missingTime)
                    loginStatus = odoo.mark_attendance('check_out', mac, epoch_to_datetime(timestamp_list[index]))
                    print(f"Making checkOut for OLd time stamp {loginStatus}")
                print(f"Making checkIn for OLd time stamps {loginStatus}")
                if index == len(timestamp_list) - 1:
                    # this is the last index loop
                    # loginStatus = checkinout("checkOut", mac, timestamp_list[index] + missingTime)
                    loginStatus = odoo.mark_attendance('check_out', mac, epoch_to_datetime(timestamp_list[index]) + missingTime)
            except IndexError as i:
                print(f"No movement detected for badge {mac}")
                # Loop through the list of datetime objects





"""
