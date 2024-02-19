import datetime
import random
import time

def generate_timestamps(YYYY, MM, DD, HH):
    # Create a datetime object for the start time
    start_time = datetime.datetime(YYYY, MM, DD, HH)

    # Create a datetime object for the end time (next day at 01:00 AM)
    end_time = start_time + datetime.timedelta(days=1, hours=1, minutes=30)

    # Initialize the current time to the start time
    current_time = start_time

    # Initialize an empty list to store the timestamps
    timestamps = []

    while current_time <= end_time:
        # Append the epoch timestamp of the current time to the list
        timestamps.append(int(time.mktime(current_time.timetuple())))

        # Increment the current time by a random number of minutes between 0 and 30
        current_time += datetime.timedelta(minutes=random.randint(25, 30))

    return timestamps

