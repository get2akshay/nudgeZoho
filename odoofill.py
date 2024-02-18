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


def day_attendancei(mac, YYYY, MM, DD, HH, test=False):
    first = False
    checkedout = False
    existing = {}
    timestamp_list = []
    existing = odoo.get_attendance_times(mac, YYYY, MM, DD)
    oute = int()
    inne = int()
    if len(existing) != 0:
        idd = existing.get(id)
        inn = existing.get("check_in")
        if inn:
            inne = odoo.get_epoch_timestamp(inn)
        out = existing.get("check_out")
        if out:
            oute = odoo.get_epoch_timestamp(out)
        if not inn or not out:
            timestamp_list = workHourRecord(mac, YYYY=YYYY, MM=MM, DD=DD, HH=HH, test=test)
            timestamp_list.sort()
            print(oute)
            print(inne)
            delta = (inne - (9 * 60 * 60))
            odoo.checkout(mac, inne - offset, idd)
            # odoo.mark_attendance('check_out', mac, timestamp_list[-1] - offset)
    else:
        timestamp_list = workHourRecord(mac, YYYY=YYYY, MM=MM, DD=DD, HH=HH, test=test)
        timestamp_list.sort()
        print("No record found! continue here to prepare record!")
        delta = (.5 * 60 * 60)
        for i in range(len(timestamp_list)):
            timestamp_list[i]
            if i == 0:
                print("First checkin for the day")
                odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
                first = True
                checkedout = False
                existing = odoo.get_attendance_times(mac, YYYY, MM, DD)
            if delta > tollarance:
                print(f"Motion delta {delta} greater than {tollarance} seconds")
                print(f"Checkout here for missing for more than {delta} seconds")
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
            if i == (len(timestamp_list) - 1):
                existing = odoo.get_attendance_times(mac, YYYY, MM, DD)
                if existing is not None and len(existing) != 0:
                    for e in existing:
                        for k, v in e.items():
                            if "Check-in" in k and not v:
                                odoo.mark_attendance('check_in', mac, timestamp_list[0] - offset)
                            if "Check-out" in k and not v:
                                odoo.mark_attendance('check_out', mac, timestamp_list[-1] - offset)
            return True




def day_attendance(mac, YYYY, MM, DD, HH, test=False):
    first = False
    checkedout = False
    existing = {}
    timestamp_list = []
    timestamp_list = workHourRecord(mac, YYYY=YYYY, MM=MM, DD=DD, HH=HH, test=test)
    timestamp_list.sort()
    for i in range(len(timestamp_list)):
        existing = odoo.get_attendance_times(mac, YYYY, MM, DD)
        print(existing)
        idd = existing.get("id")
        inn = existing.get("check_in")
        if inn:
            inne = odoo.get_epoch_timestamp(inn)
        out = existing.get("check_out")
        if out:
            oute = odoo.get_epoch_timestamp(out)
        if not inn and not out:
            odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
        if inn and not out:
            delta = timestamp_list[i] - inne
            if delta > (30 * 60) and idd:
                odoo.checkout(mac, timestamp_list[i], idd)
            else:
                print(f"Cloud has existing checkin for {mac} at {inn} for Attendance ID {idd}")
            if i == (timestamp_list[i] -1):
                odoo.checkout(mac, timestamp_list[i], idd)
                break
        if not inn and out:
            print("Not a possible situation according to current understanding!")
        if inn and out:
            print(f"Already marked for {mac} between {inn} and {out}")
            if (timestamp_list[i] - oute) > 30:
                 out = odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
                 if not out:
                     odoo.checkout(mac, inne, idd)
                     



                




""" 
    if inn is None or out is None:
        timestamp_list = []
        timestamp_list = workHourRecord(mac, YYYY=YYYY, MM=MM, DD=DD, HH=HH, test=test)
        timestamp_list.sort()
    elif inn and out is None:
        odoo.mark_attendance('check_out', mac, timestamp_list[-1] - offset)
        return

    # Loop through the list and compare each timestamp with the previous one
    delta = 0
    for i in range(len(timestamp_list)):
        timestamp_list[i]
        if i == 0:
            print("First checkin for the day")
            odoo.mark_attendance('check_in', mac, timestamp_list[i] - offset)
            first = True
            checkedout = False
        if delta > tollarance:
            print(f"Motion delta {delta} greater than {tollarance} seconds")
            print(f"Checkout here for missing for more than {delta} seconds")
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
        if i == (len(timestamp_list) - 1):
            existing = odoo.get_attendance_times(mac, YYYY, MM, DD)
            if existing is not None and len(existing) != 0:
                for e in existing:
                    for k, v in e.items():
                        if "Check-in" in k and not v:
                            odoo.mark_attendance('check_in', mac, timestamp_list[0] - offset)
                        if "Check-out" in k and not v:
                            odoo.mark_attendance('check_out', mac, timestamp_list[-1] - offset)
        return True
             """

with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)       


for mac in employees.values():
    run_daily(day_attendance, mac, YYYY=2024, MM=2, DD=18, HH=8, test=test)
    # run_daily(day_attendance, mac, YYYY=2024, MM=2, DD=16, HH=8, test=test)
    # print(mac)
