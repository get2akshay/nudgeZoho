import datetime
from lib import remotedb
start_time = datetime.datetime(2024, 3, 1, 8, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
end_time = datetime.datetime(2024, 3, 2, 2, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
while True:
    out = remotedb.motion('00:8c:10:30:02:7a', start_time, end_time)
    if out:
        print(out)