import datetime
from lib import odoo
import numpy as np
test = False
if not test:
    from lib import db
from pdb import set_trace
import time
import yaml
# offset = (5 * 60 * 60) + (30 * 60)
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

# Usage:
# print(get_epoch_timestamp('2024-02-16 02:30:00'))  # Output: 1708223400

def workHourRecord(mac, YYYY, MM, DD, HH, test=False):
    if test:
        from lib import helper
        return helper.generate_timestamps(YYYY, MM, DD, HH)
    unique = []
    # Define the start date as a datetime object
    start_time = datetime.datetime(YYYY, MM, DD, HH, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    # Define the end date as a datetime object by adding 30 days to the start date
    DD = DD + 1
    try:
        end_time = datetime.datetime(YYYY, MM, DD, 2, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        # print(f"Getting Old Movement data from {start_time} to {end_time} Badge {mac} !")
        data = db.motionInSpecifiedTimePeriod(mac, start_time, end_time)
    except ValueError as v:
        # print(f"All Month days done, caught error {v}")
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
            # print(f"Time stamp empty for {mac} in the period {start_time} to {end_time} !")
            return unique

def cloud_data(YYYY, MM, DD):
    existing = {}
    existing = odoo.get_attendance_times(mac, YYYY, MM, DD)
    idd = existing.get("id")
    inn = existing.get("check_in")
    if inn:
        inne = odoo.get_epoch_timestamp(inn)
    out = existing.get("check_out")
    if out:
        oute = odoo.get_epoch_timestamp(out)
    return { "check_in": inn, "check_out": out, "id": idd }

tollarance = 30 * 60

def day_attendance(mac, YYYY, MM, DD, HH, test=False):
    timestamp_list = workHourRecord(mac, YYYY=YYYY, MM=MM, DD=DD, HH=HH, test=test)
    timestamp_list.sort()
    if len(timestamp_list) < 5:
        print(f"Very few movements for the day ! {len(timestamp_list)}")
        return
    idd = None
    force_out = False
    for i in range(len(timestamp_list)):
        if not force_out:
            existing = cloud_data(YYYY, MM, DD)
            inn = existing.get('check_in')
            out = existing.get('check_out')
            idd = existing.get('id')
        if force_out:
            odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
            existing = cloud_data(YYYY, MM, DD)
            inn = existing.get('check_in')
            out = existing.get('check_out')
            idd = existing.get('id')
            force_out = False

        if not inn and not idd:
            odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
        
        if i != 0 and (timestamp_list[i] - timestamp_list[i - 1]) > tollarance and inn and out and idd:
            print("Entered force out!")
            odoo.checkout(mac, timestamp_list[i - 1] - offset, idd)
            force_out = True

        if inn and not out and idd and (i == len(timestamp_list) - 1):
            odoo.checkout(mac, timestamp_list[i] - offset, idd)
        time.sleep(2)

with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)       

def dumm_do(mac, YYYY=2024, MM=2, DD=1, HH=8, test=test):
    print(f"For {mac} processing data from {YYYY} {MM} {DD} {HH} {test}")

for mac in employees.values():
    run_daily(day_attendance, mac, YYYY=2024, MM=2, DD=1, HH=8, test=test)
    # day_attendance(mac, YYYY=2024, MM=2, DD=1, HH=8, test=test)
    # run_daily(dumm_do, mac, YYYY=2024, MM=2, DD=1, HH=8, test=test)