import paho.mqtt.publish as publish
import json
from random import randrange, choice
import yaml
# The data to publish
import uuid
anchors = ['Kitchen', 'Entry', 'EastWall']

def giveUUID():
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    # Convert the UUID to a 32-bit hex string
    uuid_32 = random_uuid.hex
    return uuid_32

with open('staff.yaml', 'r') as file:
    employees = yaml.safe_load(file)  


broker_ip = "192.168.0.184"

def publish_to_mqtt(broker_ip, username, password, topic, message):
    # Construct the authentication dictionary
    auth = {'username': username, 'password': password}
    
    # Publish the message to the MQTT topic
    publish.single(topic, payload=json.dumps(message), hostname=broker_ip, auth=auth)

# Example usage:
if __name__ == "__main__":
    broker_ip = "192.168.0.184"
    username = "test"
    password = "test"
    topic = "nudge"
    data = {
    "ID": 1,
    "major": 00000,
    "minor": 1,
    "uuid": giveUUID(),
    "power": -59,
    "rssi": randrange(start=-95, stop=-63, step=5),
    "mac": choice(list(employees.values())),
    "anchor": choice(list(anchors)),
    "btdensity": randrange(start=30, stop=100, step=3)
    }
    message = data

    publish_to_mqtt(broker_ip, username, password, topic, message)



