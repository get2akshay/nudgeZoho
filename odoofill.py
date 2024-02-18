import datetime
from lib import odoo
import numpy as np
test = True
if not test:
    from lib import db
from pdb import set_trace
import time
import yaml
offset = (5 * 60 * 60) + (30 * 60) 

def run_daily(func, mac, YYYY, MM, DD, HH, test):
    start_date = datetime.datetime(YYYY, MM, DD, HH)
    present_date = datetime.datetime.now()

    while start_date <= present_date:
        # print(f"Running code for {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
        # Place your code here
        day = start_date.day
        year = start_date.year
        month = start_date.month
        hour = start_date.hour
        func(mac, year, month, day, hour, test)
        # Increment the day by one
        start_date += datetime.timedelta(days=1)
        # If the next day is in the future, wait until it comes
        if start_date > datetime.datetime.now():
            print(f"Waiting for {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
            while datetime.datetime.now() < start_date:
                time.sleep(60)  # Check every minute

# Define the method that takes an epoch time stamp as an argument
def epoch_to_datetime(epoch):
  # Convert the epoch time stamp to a datetime object
  dt = datetime.datetime.fromtimestamp(epoch)
  # Format the datetime object as a string
  dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
  # Return the formatted string
  return dt_str

def workHourRecord(mac, YYYY, MM, DD, HH, test=False):
    if test:
        from lib import helper
        return helper.generate_timestamps(YYYY, MM, DD, HH)
    unique = []
    # Define the start date as a datetime object
    start_time = datetime.datetime(YYYY, MM, DD, HH, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    # Define the end date as a datetime object by adding 30 days to the start date
    # DD = DD + 1
    try:
        end_time = datetime.datetime(YYYY, MM, DD, 23, 59, 0).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Getting Old Movement data from {start_time} to {end_time} Badge {mac} !")
        data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    except ValueError as v:
        print(f"All Month days done, caught error {v}")
        return unique
    if data is not None:
        # Use list comprehension to filter out the tuples that have at least two non zero values in the last three elements
        filtered_list = [t for t in data if np.count_nonzero(t[-3:]) > 2]
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

def day_attendancew(mac, YYYY, MM, DD, HH, test=False):
    timestamp_list = []
    timestamp_list = workHourRecord(mac, YYYY=YYYY, MM=MM, DD=DD, HH=HH, test=test)
    timestamp_list.sort()
    kvs = []
    kvs = odoo.verify_existing_checkin(mac, YYYY, MM, DD)
    if len(kvs) == 0 and len(timestamp_list) != 0:
        cin = odoo.dateFormatOdoo(min(timestamp_list) - offset)
        print(f"Making First CheckIN for {cin}")
        odoo.mark_attendance('check_in', mac, cin)
    else:
        for elem in kvs:
            if elem and elem.get('checkin') and elem.get('checkout'):
                print("Records exists for the")
        return True
    if len(timestamp_list) != 0:
        cin = odoo.dateFormatOdoo(max(timestamp_list) - offset)
        print(f"Making CheckOut for {cin}")
        odoo.checkout(mac, cin)
    # print(kvs)
    # for move in timestamp_list:
    # for i in range(len(timestamp_list)):
        # print(timestamp_list[i])
        # kvs = odoo.verify_existing_checkin(mac, YYYY, MM, DD)
tollarance = 30 * 60

def day_attendance(mac, YYYY, MM, DD, HH, test=False):
    timestamp_list = []
    timestamp_list = workHourRecord(mac, YYYY=YYYY, MM=MM, DD=DD, HH=HH, test=test)
    timestamp_list.sort()
    # Loop through the list and compare each timestamp with the previous one
    first = False
    checkedout = False
    delta = 0
    for i in range(len(timestamp_list)):
        timestamp_list[i]
        existing = odoo.verify_existing_checkin(mac, YYYY, MM, DD)
        if i == 0 and len(existing) == 0:
            print("First checkin for the day")
            odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
            first = True
            checkedout = False
        if delta > tollarance:
            print(f"Motion delta {delta} greater than {tollarance} seconds")
            print(f"Checkout here for missing mor for {delta} seconds")
            if first:
                cin = odoo.dateFormatOdoo(timestamp_list[i] - offset)
                print(f"Making CheckOut for {cin}")
                odoo.checkout(mac, timestamp_list[i] - offset)
                checkedout = True
                first = False
        else:
            print(f"Motion delta {delta} less than {tollarance} seconds")
            print(f"Keep last checkin as Badge Live on floor for {delta} seconds")
            if checkedout and not first:
                print("Checkin here for new time stamp!")
                cin = odoo.dateFormatOdoo(timestamp_list[i] - offset)
                print(f"Making after break Checkin for {cin}")
                odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
                checkedout = False
                first = True
        if i < (len(timestamp_list) - 1):
            delta = (timestamp_list[i+1] - timestamp_list[i])
        if i == len(timestamp_list) - 1:
           pass
            

with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)       

for mac in employees.values():
    run_daily(day_attendance, mac, YYYY=2024, MM=2, DD=15, HH=8, test=test)
    # print(mac)


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
