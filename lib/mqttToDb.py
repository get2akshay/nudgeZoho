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
broker_address = "192.168.0.184"  # Replace with your broker's IP address
topic = "nudge"
username = "test"
password = "test"

def db_add(data):
    # PostgreSQL setup
    conn = psycopg2.connect(database=database, user="postgres", password="", host="/var/run/postgresql/")
    cur = conn.cursor()
    # Execute the query to get the list of databases
    try:
        # Construct the SQL query for inserting data into the table
        columns_sql = ', '.join(data.keys())
        values_sql = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in data.values()])
        epoch_time = int(time.time())  # Current epoch time
        sql_query = f"INSERT INTO btdata.anchorsdata ({columns_sql}, epoch_time) VALUES ({values_sql}, {epoch_time})"

        # Execute the SQL query to insert data into the table
        cur.execute(sql_query)

        # Commit the transaction
        conn.commit()
        print("Data added to the table successfully!")
    except Exception as e:
        print(f"Error: {e}")
        # Rollback the transaction in case of an error
        conn.rollback()
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()


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
        print("Database, schema, and table created successfully!")
    except Exception as e:
        print(f"Error: {e}")
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
    data = json.loads(payload)
    
    # Print the received data
    print("Received message:")
    print(json.dumps(data, indent=4))
    if not db_check():
        print(f"Database not present in DB will stop!")
        return False
    print("Call add_db here!")
    db_add(data)
    

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
