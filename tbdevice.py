from lib import tb
# /api/tenant/devices?deviceName=Entry

api = f"api/tenant/devices"
# api = "api/device/types"
params = {}
params.update({"deviceName" : "Entry"})
t = tb.rest_get(api,params)
if not t:
    print(f"API {api} resulted Empty json!")
else:
    print(t)