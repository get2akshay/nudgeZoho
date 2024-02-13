from lib import tb
# /api/tenant/devices?deviceName=Entry

api = f"/api/tenant/devices?deviceName=Entry"

t = tb.rest_get(api)
if not t:
    print(f"API {api} resulted Empty json!")
else:
    print(t)