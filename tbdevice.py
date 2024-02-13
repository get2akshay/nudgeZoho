from lib import tb
# /api/tenant/devices?deviceName=Entry

api = f"api/tenant/devices"
# api = "api/device/types"
# api = "api/device/info"

params = {}
params.update({"deviceName" : "Entry"})
t = tb.rest_get(api,params)
if not t:
    print(f"API {api} resulted Empty json!")
else:
    id = t.get("id").get("id")
    print(id)
    api = "api/device/info"
    params = {}
    params.update({"deviceId" : id})
    t = tb.rest_get(api,params)
    print(t)


"""{
  "id": {
    "entityType": "DEVICE",
    "id": "587143d0-7c06-11ee-8d04-9bfe3627a1b1"
  },
  "createdTime": 1699207719053,
  "additionalInfo": {
    "gateway": false,
    "overwriteActivityTime": false,
    "description": "Anchor at entry"
  },
  "tenantId": {
    "entityType": "TENANT",
    "id": "a016a6a0-7bff-11ee-9dc7-1d05a6175b31"
  },
  "customerId": {
    "entityType": "CUSTOMER",
    "id": "a0959aa0-7bff-11ee-9dc7-1d05a6175b31"
  },
  "name": "Entry",
  "type": "Anchors",
  "label": "anchor",
  "deviceProfileId": {
    "entityType": "DEVICE_PROFILE",
    "id": "96bff1f0-7c00-11ee-8d04-9bfe3627a1b1"
  },
  "deviceData": {
    "configuration": {
      "type": "DEFAULT"
    },
    "transportConfiguration": {
      "type": "MQTT"
    }
  },
  "firmwareId": null,
  "softwareId": null,
  "externalId": null
}
"""