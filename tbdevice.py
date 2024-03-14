from lib import tb, command
import time
from datetime import datetime
from lib import sendmail

def messgprep(msg):
    # Set your Gmail credentials and email details
    return {'subject': "Tiddly Zone Sensors Down!", 'body': f"These anchors are down: {msg}", 'sender_email': 'bot@gmail.com', 'recipient_email': 'akshayy2k@gmail.com', 'password': 'nl@1234567'}


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
    down = "Test"
    for d in anchors:
        s = deviceStatus(d)
        print(f"Anchor {d} is {s}")
        # Call the function to send the email
        down = "Anchors down"
        if not s:
            if d in "Entry" or d in "EastWall" or d == "Kitchen Entry":
                down += f" {d} "
            else:
                down += f" {d} "
                print("Kitchen Anchor down!")
    if down:
        sendmail.send_email(down)
        return False
    else:
        return True
prevmin = 0
happychcek = 30
while True:
    curmin = datetime.now().minute
    if (curmin - prevmin) > happychcek:
        out = job(anchors)
        if out:
            continue
        else:
            happychcek = 10
    prevmin = curmin