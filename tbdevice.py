from lib import tb

t = tb.rest_get("'https://b7d7-103-234-158-46.ngrok-free.app:443/api/tenant/devices?deviceName=Entry")
print(t)