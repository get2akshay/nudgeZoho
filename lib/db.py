import psycopg2
from decimal import Decimal
import datetime

# connect to the PostgreSQL database
# connect to the PostgreSQL database server
conn = psycopg2.connect(
    host="127.0.0.1",
    port="5432",
    database="tiddly",
    user="postgres",
    password="nl1234567"
)
# conn = psycopg2.connect("dbname=your_db user=your_user password=your_password")

# create a cursor object
cur = conn.cursor()

# Query to get MAC to TB UUID mapping

def getTimeStamp():
    import time
    # Get the current date as a datetime object
    today = datetime.date.today()
    # Get the start of the day as a datetime object
    start_of_day = datetime.datetime.combine(today, datetime.time())        
    # Convert the start of the day to epoch time
    start_of_day_epoch = int(time.mktime(start_of_day.timetuple()))
    # Print the start of the day epoch time
    print(f"Start of the day epoch time: {start_of_day_epoch}")

    # Get the current time as a datetime object
    now = datetime.datetime.now()
    # Convert the current time to epoch time
    now_epoch = int(time.mktime(now.timetuple()))
    # Print the current time epoch time
    print(f"Current time epoch time: {now_epoch}")
    return start_of_day_epoch, now_epoch

def get_mac_uuid(mac):
    return f"""SELECT
    most_common_entity_id
FROM (
    SELECT
        entity_id AS most_common_entity_id,
        ROW_NUMBER() OVER (PARTITION BY str_v ORDER BY COUNT(*) DESC) AS rn
    FROM
        ts_kv
    WHERE
        str_v SIMILAR TO '{mac}'
    GROUP BY
        str_v, entity_id
) AS subquery
WHERE
    rn = 1
LIMIT 2;"""

def next_motion_point():
    f"""
        SELECT
            ts/1000 AS time,
            str_v,
            (('x' || REPLACE(LEFT(str_v, 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS x_axis,
            (('x' || REPLACE(SUBSTRING(str_v FROM 10 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS y_axis,
            (('x' || REPLACE(SUBSTRING(str_v FROM 19 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS z_axis
        FROM
            ts_kv
        WHERE
            entity_id = '{uuid}'
            AND key = 53
            AND ts > extract(epoch from 'start_timestamp'::timestamp) * 1000 -- Only timestamps in the future from the specified start time
            AND (x_axis != 0 OR y_axis != 0 OR z_axis != 0) -- Check for non-zero values
        ORDER BY ts ASC -- Order by timestamp in ascending order
        LIMIT 1; -- Limit the result to 1 row
    """

def firstMoveOfTheDay(uuid):
    return """SELECT
            t1.ts/1000 AS time,
            t1.str_v,
            (('x' || REPLACE(LEFT(t1.str_v, 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS x_axis,
            (('x' || REPLACE(SUBSTRING(t1.str_v FROM 10 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS y_axis,
            (('x' || REPLACE(SUBSTRING(t1.str_v FROM 19 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS z_axis
    FROM
            ts_kv t1
        JOIN
            (SELECT DATE (ts/1000) AS date, MIN (ts) AS min_ts
            FROM ts_kv
            WHERE entity_id = '{uuid}'
            AND key = 53
            GROUP BY DATE (ts/1000)) t2
        ON t1.ts = t2.min_ts
        WHERE
            t1.entity_id = '{uuid}'
            AND t1.key = 53
    """

def buildquery(uuid):
    # define the SQL query as a string
    return f"""WITH GyroData AS (
  SELECT
    ts/1000 AS time,
    str_v,
    (('x' || REPLACE(LEFT(str_v, 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS x_axis,
    (('x' || REPLACE(SUBSTRING(str_v FROM 10 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS y_axis,
    (('x' || REPLACE(SUBSTRING(str_v FROM 19 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS z_axis
  FROM
    ts_kv
  WHERE
    entity_id = '{uuid}'
    AND key = 53
)

SELECT
  q1.time,
  CASE
    WHEN q2.x_axis = 0 AND q2.y_axis = 0 AND q2.z_axis = 0 THEN NULL
    ELSE q1.long_v
  END AS Activity
FROM
  (
    SELECT
      ts/1000 AS time,
      long_v
    FROM
      ts_kv
    WHERE
      entity_id = '{uuid}'
      AND key = 49
  ) AS q1
JOIN GyroData q2 ON q1.time = q2.time;"""

def motionInSpecifiedTimePeriod(mac, start_date, end_date):
    # Define the SQL query with placeholders
    uuid = getuuid(mac)
    if uuid is None:
        print(f"DB returend empty UUID value for {mac} during time period {start_date} to {end_date}")
        return None
    sql = f"""SELECT
                ts/1000 AS time,
                str_v,
                (('x' || REPLACE(LEFT(str_v, 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS x_axis,
                (('x' || REPLACE(SUBSTRING(str_v FROM 10 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS y_axis,
                (('x' || REPLACE(SUBSTRING(str_v FROM 19 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS z_axis
            FROM
                ts_kv
            WHERE
                entity_id = '{uuid}'
            AND key = 53
            AND TO_TIMESTAMP(ts/1000) >= TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS') AND TO_TIMESTAMP(ts/1000) <= TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS');
    """
    return query_db(query=sql, start_date=start_date, end_date=end_date)

     
    

def getuuid(mac):
    uuid = ""
    # execute the SQL query and pass the entity_id as a parameter
    data = query_db(get_mac_uuid(mac))
    try:
        for row in data:
        #print(next(iter(set(row))))
            uuid = next(iter(set(row)))
        if not uuid:
            print("MAC to UUID could not be fetched")
        # fetch the result set as a list of tuples
        # close the cursor and the connection
        return uuid
    except TypeError as t:
        print("DB dod not give any data!")
        pass

def getxyz(mac):
    latest_xyz = ()
    # fetch the result set as a list of tuples
    uuid = getuuid(mac)
    data = query_db(buildquery(uuid))
    for d in data:
        latest_xyz = d
    return latest_xyz

def allMotinPointsInADay(uuid):
    return f"""SELECT
        ts/1000 AS time,
        str_v,
        (('x' || REPLACE(LEFT(str_v, 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS x_axis,
        (('x' || REPLACE(SUBSTRING(str_v FROM 10 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS y_axis,
        (('x' || REPLACE(SUBSTRING(str_v FROM 19 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS z_axis
FROM
        ts_kv
    WHERE
        entity_id = '{uuid}'
        AND key = 53
        AND ts BETWEEN extract(epoch from (CURRENT_DATE - INTERVAL '1 DAY')) * 1000 AND extract(epoch from CURRENT_TIMESTAMP) * 1000;
"""

def get_timestamp(tup):
    # Check if the tuple has at least five elements
    if len(tup) < 5:
        print("Incorrect tupple {tup}")
        return None # or raise an exception
    # Extract the timestamp and the x, y, and z values
    timestamp = tup[0]
    x = float(tup[-3])
    y = float(tup[-2])
    z = float(tup[-1])
    # Count how many of the x, y, and z values are non-zero
    count = 0
    if x != 0:
        count += 1
    if y != 0:
        count += 1
    if z != 0:
        count += 1
    # If the count is greater than or equal to two, return the timestamp
    if count == 3:
        return timestamp


def getxyzSpecifictime(mac):
    motion = []
    # fetch the result set as a list of tuples
    uuid = getuuid(mac)
    data = query_db(allMotinPointsInADay(uuid))
    for point in data:
        motion.append(get_timestamp(point))
    return tuple(set(tuple(x for x in motion if x is not None)))

def query_db(query, start_date=None, end_date=None):
    # Define the connection string
    # create a cursor object
    # Connect to the database
    try:
        # connect to the PostgreSQL database server
        conn = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            database="tiddly",
            user="postgres",
            password="nl1234567"
        )
        # conn = psycopg2.connect("dbname=your_db user=your_user password=your_password")
        #conn = psycopg2.connect(conn_string)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    # Create a cursor
    cursor = conn.cursor()
    # Execute the query
    try:
        cursor.execute(query,(start_date, end_date))
    except psycopg2.Error as e:
        print(f"Error executing the query: {e}")
        return None
    # Fetch the output table
    output = cursor.fetchall()
    # Close the cursor and the connection
    cursor.close()
    conn.close()
    # Return the output table
    return output

def find_next_non_zero_timestamp(mac, start_timestamp):
    uuid = getuuid(mac)
    if uuid is None:
        print(f"DB returend empty UUID value for {mac} during time period {start_date} to {end_date}")
        return None
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            database="tiddly",
            user="postgres",
            password="nl1234567"
        )
        # Create a cursor object
        cursor = conn.cursor()

        # Prepare the SQL query
        query = f"""
            WITH GyroData AS (
                SELECT
                    ts/1000 AS time,
                    str_v,
                    (('x' || REPLACE(LEFT(str_v, 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS x_axis,
                    (('x' || REPLACE(SUBSTRING(str_v FROM 10 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS y_axis,
                    (('x' || REPLACE(SUBSTRING(str_v FROM 19 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS z_axis
                FROM
                    ts_kv
                WHERE
                    entity_id = '{uuid}'
                    AND key = 53
                    AND ts > extract(epoch from %s::{start_timestamp}) * 1000 -- Only timestamps in the future from the specified start time
            )

            SELECT
                time,
                str_v,
                x_axis,
                y_axis,
                z_axis
            FROM
                GyroData
            WHERE
                (x_axis != 0 OR y_axis != 0 OR z_axis != 0) -- Check for non-zero values
            ORDER BY time ASC -- Order by timestamp in ascending order
            LIMIT 1; -- Limit the result to 1 row
        """

        # Execute the SQL query
        cursor.execute(query, (start_timestamp,))

        # Fetch the result
        result = cursor.fetchone()

        return result

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)

    finally:
        # Close the cursor and connection
        if conn:
            cursor.close()
            conn.close()

# Example usage
# start_timestamp = '2024-03-02 08:39:53'
# result = find_next_non_zero_timestamp(start_timestamp)
# print("Result:", result)
