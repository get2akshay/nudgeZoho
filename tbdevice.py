from lib import tb
from lib import sendmail
import random
import sched
import time
import random
# Initialize the scheduler
scheduler = sched.scheduler(time.time, time.sleep)
test = False
email_body = ''

def messgprep(msg):
    # Set your Gmail credentials and email details
    eng = ""
    for k in msg.keys():
        eng += f' {k}, '
    return {'subject': "Tiddly Zone Sensors Down!", 'body': f"These anchors are down: '{eng}'", 'sender_email': 'bot@byplayit.com', 'recipient_email': 'makaloshospitalityllp@gmail.com, sunita@byplayit.com', 'password': 'NlIsMySaviour46'}

def deviceStatus(device):
    if test:
        return random.choice([True, False])
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

def job():
    status = {}
    for d in anchors:
        s = deviceStatus(d)
        print(f"Anchor {d} is {s}")
        # Call the function to send the email
        if not s:
            if d in "Entry":
                status.update({"Entry" : False})
            elif d in "EastWall":
                status.update({"EastWall" : False}) 
            elif d == "Kitchen Entry":
                status.update({"Kitchen Entry" : False}) 
            elif d == "Kitchen Entry":
                status.update({"InsideKitchin" : False})
        else:
            print("Anchors are up!")
    return status


def check_function_one():
    result = job()
    if not result:
        print("Function one returned empty dictionary. Continuing...")
        # Schedule the next check in 5 minutes
        scheduler.enter(300, 1, job)
    else:
        print("Function one returned non empty dictionary. Triggering function two...")
        # Schedule the next check in 15 minutes
        scheduler.enter(3600, 1, job)
        sendmail.send_email(messgprep(result))

if __name__ == "__main__":
    while True:
        current_time = time.localtime()
        hour = current_time.tm_hour
        delay = 0
        if 2 <= hour < 8:
           # Run every hour between 0200 and 0800
           delay = 3600
        else:
            delay = 0
        scheduler.enter(delay, 1, check_function_one)
        # Run the scheduler
        scheduler.run()


    