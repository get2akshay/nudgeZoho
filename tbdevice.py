from lib import tb
# /api/tenant/devices?deviceName=Entry


# api = "api/device/types"
# api = "api/device/info"



def deviceStatus(device):
    api = f"api/tenant/devices"
    params = {}
    params["deviceName"] = device
    t = tb.rest_get(api,params)
    if not t:
        print(f"API {api} resulted Empty json!")
        return None
    else:
        id = t.get("id").get("id")
        print(id)
        api = f"api/device/info/{id}"
        s = tb.rest_get(api, params)
        if s.get("active"):
            return True
        else:
            return False
        
anchors = ["Entry", "InsideKitchin", "EastWall", "	Kitchen Entry"]
for d in anchors:
    s = deviceStatus(d)
    print(f"Anchor {d} is {s}")
