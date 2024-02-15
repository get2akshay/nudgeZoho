
import datetime
from lib import db
import numpy as np
from lib import odoo


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
        

for epoch in  workHourRecord('00:8c:10:30:02:6f', YYYY=2024, MM=2, DD=1, HH=8):
    print(epoch)
    checkin = odoo.get_checkin('00:8c:10:30:02:6f')
    if not checkin:
        odoo.mark_attendance('00:8c:10:30:02:6f', epoch_to_datetime(epoch))
    else:
        print("Apply chekin time check logic here!")
