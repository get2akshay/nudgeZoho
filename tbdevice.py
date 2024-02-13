from lib import tb
# /api/tenant/devices?deviceName=Entry

api = f"/api/tenant/devices?deviceName=Entry"

t = tb.rest_get(api)
print(t)