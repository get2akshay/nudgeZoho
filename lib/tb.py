import requests
from datetime import datetime, timedelta
import os
import yaml
import logging
params = dict()
# Get the current working directory
current_directory = os.getcwd()
# Construct the absolute path to the YAML file in the parent directory
yaml_file_path = os.path.join(f"{current_directory}", "config", "config.yaml")

config_data = {}

try:
    # Open and read the YAML file
    with open(yaml_file_path, "r") as file:
        config_data = yaml.safe_load(file)

except FileNotFoundError:
    print("Config file not found.")

if config_data is None:
    exit
    

# Access values from the YAML file
server_public = config_data["server_public"]["host"]
port = config_data["server_public"]["port"]
username = config_data["server_public"]["username"]
password = config_data["server_public"]["password"]
# Access values from the YAML file
edge = config_data["tenants"]["tidly"]["edge"]
edge_port = config_data["tenants"]["tidly"]["port"]
edge_username = config_data["tenants"]["tidly"]["username"]
edge_password = config_data["tenants"]["tidly"]["password"]
#Locations
anchors = config_data["tenants"]["tidly"]["anchors"]
#Badges
badges = config_data["tenants"]["tidly"]["HumanTags"]
# Print the values
print(f"Database Host: {server_public}")
print(f"Database Port: {port}")
print(f"Database Username: {username}")
print(f"Database Password: {password}")

#ThingsBoard
http = "http://"
webSocket = "ws://"
base_url = f"{http}{edge}:{edge_port}/"
get_url = f"{base_url}api/plugins/telemetry/DEVICE/1747e250-5a29-11ee-b96b-53725f09012e/values/timeseries"
# http://65.20.78.99:8080/api/plugins/telemetry/ASSET/7db05ee0-5d0e-11ee-b96b-53725f09012e/timeseries/ANY?scope=ANY
post_url = f"{base_url}api/plugins/telemetry/DEVICE/2196e090-5dd4-11ee-9c57-339635acbaee/timeseries/ANY?scope=ANY"
headers = {
    "Content-Type": "application/json",
}
# Generate fresh JWT token
def jwttoken():
    """curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"username":"tenant@thingsboard.org", "password":"tenant"}' 'http://THINGSBOARD_URL/api/auth/login'"""
    token = {}
    token.update({"token": ""})
    params = {
        "username": username,
        "password": password,
    }
    response = requests.post(f"{base_url}api/auth/login", headers=headers, json=params)
    if response.status_code == 200:
        # Parse the JSON response.
        token = response.json()
        return token.get("token")
    else:
        print(f"Failed to fetch JWT Token! Status code: {response.status_code}")
        return token.get("token")

#Get method
def rest_get(api):
    JWT_TOKEN = jwttoken()
    telemetry_data = {}
    # print(params)
    if JWT_TOKEN:
        headers["X-Authorization"] = f"Bearer {JWT_TOKEN}"
    response = requests.get(f"{base_url}{api}", headers=headers, params=params)
    # Check if the request was successful (HTTP status code 200).
    if response.status_code == 200:
        # Parse the JSON response.
        telemetry_data = response.json()
        # Process the telemetry data as needed.
        return telemetry_data
    else:
        logging.debug(f"Failed to fetch telemetry data. Status code: {response.status_code}")
        return telemetry_data

#Get method
def rest_post(api, payload):
    # Add the access token to the headers if it's required.
    JWT_TOKEN = jwttoken()
    if JWT_TOKEN:
        headers["X-Authorization"] = f"Bearer {JWT_TOKEN}"
    response = requests.post(api, headers=headers, json=payload)
    # Check if the request was successful (HTTP status code 200).
    if response.status_code == 200:
        logging.info("Time series data sent successfully.")
    else:
        logging.error(f"Failed to send time series data. Status code: {response.status_code}")

