import datetime
import datetime
from lib import odoo
import numpy as np
test = False
if not test:
    from lib import db
from pdb import set_trace
import time
import yaml
import threading

# offset = (5 * 60 * 60) + (30 * 60)
offset = 0

off_floor = 30 * 60

tdd = [1706779963, 1706780640, 1706790586, 1706792442, 1706792448, 1706792770, 1706793326, 1706795112, 1706795114, 1706799685, 1706801012, 1706802195, 1706802210, 1706802296, 1706802471, 1706802472, 1706803193, 1706803820, 1706804712, 1706806236, 1706806238, 1706806552, 1706806572, 1706806574, 1706806689, 1706806691, 1706806693, 1706806699, 1706806700, 1706807178, 1706807180, 1706807968, 1706807972, 1706808217, 1706808251, 1706808269, 1706808291, 1706808318, 1706808320, 1706809142, 1706809653, 1706809655, 1706812381, 1706812384, 1706812386, 1706812910]    

def extract_datetime_components(date_string, offset_minutes=offset):
    try:
        # Parse the input date string
        dt_nooffset = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

        # Add the offset to the datetime
        dt = dt_nooffset + datetime.timedelta(minutes=offset_minutes)

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

def cloud_data(YYYY, MM, DD):
    idd = int()    
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

def markinglogic(mac, ist_start_date, test=False):
    if not test:
        timestamp_list = workHourRecord(mac, ist_start_date, test=test)
    else:
        timestamp_list = tdd
    if timestamp_list is not None:
        sorted(timestamp_list)
    if len(timestamp_list) < 2:
        # print(f"Very few movements for the day ! {len(timestamp_list)}")
        return True
    else:
        pass
        # print(f"There were total {timestamp_list} moves for {mac} on {ist_start_date}")

    def checkin_thread(timestamp):
        # print("First checkin!")
        odoo.checkin_employee(mac, timestamp - offset)
        time.sleep(1)
    def checkout_thread(timestamp, idd):
        # print("Last checkout")
        odoo.checkout_employee(mac, timestamp - offset, idd)
        time.sleep(1)
    dic = {"id": False, "check_in": False, "check_out": False}
    idd = 0
    check_in = 0
    check_out = 0
    less = False
    greater = False
    for idx, timestamp in enumerate(sorted(timestamp_list)):
        if idx == 0:
            # First timestamp, mark as check-in
            checkin_thread(timestamp)
            continue
        elif idx == len(timestamp_list) - 1:
            # Last timestamp, mark as check-out
            checkout_thread(timestamp, idd)
            break
        else:
            time_diff = timestamp - timestamp_list[idx - 1]
            if time_diff > tollarance and not greater:
                dic = odoo.get_latest_attndance_time(mac)
                idd = False
                if type(dic) is dict:
                    idd = dic.get('id')
                    check_in_str = dic.get('check_in')
                    if check_in_str:
                        check_in = odoo.get_epoch_timestamp(check_in_str)
                    check_out_str = dic.get('check_out')
                    if check_out_str:
                        check_out = odoo.get_epoch_timestamp(check_out_str)
                    if idd and check_in and not check_out and timestamp > check_in:
                        checkout_thread(timestamp_list[idx - 1], idd)
                        checkin_thread(timestamp)
                    greater = True
                    less = False
            elif time_diff < tollarance and not less:
                dic = odoo.get_latest_attndance_time(mac)
                idd = False
                if type(dic) is dict:
                    idd = dic.get('id')
                    check_in_str = dic.get('check_in')
                    if check_in_str:
                        check_in = odoo.get_epoch_timestamp(check_in_str)
                    check_out_str = dic.get('check_out')
                    if check_out_str:
                        check_out = odoo.get_epoch_timestamp(check_out_str)
                    if idd and check_in and check_out and timestamp > check_out:
                        checkin_thread(timestamp)
                    greater = False
                    less = True


with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)

# Given IST start date string
ist_start_date_str = "2024-03-01 07:00:00"
ist_start_date = datetime.datetime.strptime(ist_start_date_str, "%Y-%m-%d %H:%M:%S")
# Get the current date
current_date = datetime.datetime.now()
# Increment the date until the current day
while ist_start_date.date() <= current_date.date():
    print(ist_start_date.strftime("%Y-%m-%d %H:%M:%S"))

    print(f"Will run marking logic for date {ist_start_date}")
    for mac in employees.values():
        markinglogic(mac, ist_start_date, test=test)
    
    ist_start_date += datetime.timedelta(days=1)
