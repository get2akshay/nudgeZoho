from lib import tb, command
import schedule
import time
from datetime import datetime



def deviceStatus(device):
    api = f"api/tenant/devices"
    params = {}
    params["deviceName"] = device
    t = tb.rest_get(api,params)
    if not t:
        # print(f"API {api} resulted Empty json!")
        return None
    else:
        id = t.get("id").get("id")
        # print(id)
        api = f"api/device/info/{id}"
        s = tb.rest_get(api, params)
        if s.get("active"):
            return True
        else:
            return False
        
anchors = ["Entry", "InsideKitchin", "EastWall", "Kitchen Entry"]

def job(anchors):
    for d in anchors:
        s = deviceStatus(d)
        # print(f"Anchor {d} is {s}")
        if not s:
            if d in "Entry" or d in "EastWall" or d == "Kitchen Entry":
                output, error = command.ssh_command("192.168.0.1", "admin", "admin@123", "ls -lrt")
                print('Output from SSH:', output)
                if error:
                    print('Error:', error)
            else:
                print("Kitchen Anchor down!")

def run_job_every_5_min(anchors):
    schedule.every(5).minutes.do(job, anchors)

def run_job_every_30_min(anchors):
    my_list = ['item1', 'item2', 'item3']  # replace with your list
    schedule.every(30).minutes.do(job, anchors)

while True:
    job(anchors)
    # current_time = datetime.now().hour
    # if current_time >= 8 and current_time <= 23:
    #     run_job_every_5_min(anchors)
    # else:
    #     run_job_every_30_min(anchors)
    # schedule.run_pending()
    # time.sleep(5)

