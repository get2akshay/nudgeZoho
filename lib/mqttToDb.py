import paho.mqtt.client as mqtt
import psycopg2
import json
from datetime import datetime
import time

# DB configuration
database = "tiddly"
tablename = "anchorsdata"
schema = "btdata"
# MQTT broker configuration
broker_address = "127.0.0.1"  # Replace with your broker's IP address
topic = "nudge/pub"
username = "test"
password = "test"


"""

SELECT epoch_time FROM btdata.anchorsdata WHERE epoch_time >= UNIX_TIMESTAMP(NOW() - INTERVAL '30 SECOND');

SELECT epoch_time FROM btdata.anchorsdata WHERE epoch_time >= EXTRACT(EPOCH FROM NOW() - INTERVAL '30 seconds');




"""


# Global dictionary to store the previous UUID values for each MAC address
previous_uuids = {}

def is_uuid_changed(mac_uuid):
    global previous_uuids
    
    # Extract MAC and UUID values from the input dictionary
    mac = mac_uuid.get("mac")
    uuid = mac_uuid.get("uuid")
    
    # If the MAC address is not in the dictionary, add it with the current UUID value
    if mac not in previous_uuids:
        previous_uuids[mac] = uuid
        return False  # First time seeing this MAC address, so UUID hasn't changed
    
    # If the UUID value has changed for the MAC address, update the dictionary and return True
    if previous_uuids[mac] != uuid:
        previous_uuids[mac] = uuid
        return True
    else:
        return False


def db_add(data):
    # PostgreSQL setup
    conn = psycopg2.connect(database=database, user="postgres", password="", host="/var/run/postgresql/")
    cur = conn.cursor()
    # Execute the query to get the list of databases
    try:
        # Construct the SQL query for inserting data into the table
        columns_sql = ', '.join(data.keys())
        values_sql = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in data.values()])
        # epoch_time = int(time.time())  # Current epoch time
        # Get the current time
        now = datetime.now()
        # Convert to epoch time
        epoch_time = int(time.mktime(now.timetuple()))
        sql_query = f"INSERT INTO {schema}.{tablename} ({columns_sql}, epoch_time) VALUES ({values_sql}, {epoch_time})"
        # Execute the SQL query to insert data into the table
        cur.execute(sql_query)

        # Commit the transaction
        conn.commit()
        # print("Data added to the table successfully!")
    except Exception as e:
        # print(f"Error: {e}")
        # Rollback the transaction in case of an error
        conn.rollback()
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()


def db_create():
    conn = psycopg2.connect(database=database, user="postgres", password="", host="/var/run/postgresql/")
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {database};")
        conn.commit()
    except Exception as e:
        # print(f"Error: {e}")
        # Rollback the transaction in case of an error
        conn.rollback()
        return False
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
    return True


def db_check():
    # PostgreSQL setup
    conn = psycopg2.connect(database=database, user="postgres", password="", host="/var/run/postgresql/")
    cur = conn.cursor()
    # Create db if it does not exist
    # JSON object representing the data structure
    data_structure = {
        "ID": "INT",
        "major": "INT",
        "minor": "INT",
        "uuid": "VARCHAR(255)",
        "power": "INT",
        "rssi": "INT",
        "mac": "VARCHAR(255)",
        "anchor": "VARCHAR(255)",
        "btdensity": "INT",
    }
    try:
        # Create schema if not exists
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        # Construct SQL query for creating the table
        columns_sql = ', '.join([f"{column} {data_structure[column]}" for column in data_structure])
        sql_query = f"CREATE TABLE IF NOT EXISTS btdata.anchorsdata ({columns_sql}, epoch_time BIGINT)"

        # Execute the SQL query to create the table
        cur.execute(sql_query)

        # Commit the transaction
        conn.commit()
        # print("Database, schema, and table created successfully!")
    except Exception as e:
        # print(f"Error: {e}")
        # Rollback the transaction in case of an error
        conn.rollback()
        return False
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
    return True
    

# Callback function for when a message is received from the broker
def on_message(client, userdata, message):
    # Decode the message payload (assumed to be JSON)
    payload = message.payload.decode("utf-8")
    
    # Parse the JSON data
    try:
        data = json.loads(payload)
        # Print the received data
        # print("Received message:")
        # print(json.dumps(data, indent=4))
        if not db_check():
            print(f"Database not present in DB will stop!")
            return False
        # print("Call add_db here!")
        for d in data:
            mac = d.get("mac")
            uuid = d.get("uuid")
            if is_uuid_changed(d):
                db_add(d)
            else:
                pass
                # print(f"UUID changed {mac} to {uuid} !")
    except json.decoder.JSONDecodeError as j:
        print(f"Caught error {j}")

    
    

    

# Create an MQTT client instance
client = mqtt.Client()

# Set username and password for authentication
client.username_pw_set(username, password)

# Set the callback function for when a message is received
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address)

# Subscribe to the topic
client.subscribe(topic)

# Loop to process incoming messages
client.loop_forever()