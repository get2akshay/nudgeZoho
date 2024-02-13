from lib import tb

t = tb.rest_get("'https://192.168.0.108:8080/api/tenant/devices?deviceName=Entry")
print(t)