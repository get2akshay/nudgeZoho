import xmlrpc.client
from datetime import datetime
from time import sleep

# Specify your Odoo server information
# url = 'https://byplayit2.odoo.com/'
url = 'http://65.20.78.99:8069/'
db = 'nudge'
username = 'akshay.sharma@byplayit.com'
password = 'akshay911'

def dateFormatOdoo(timestamp):
    # Create a datetime object from the epoch time stamp
    # Format the datetime object as a string
    # Convert epoch to datetime
    dt = datetime.fromtimestamp(timestamp)
    # Format datetime in ISO 8601 format
    odoo_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    return odoo_time

def get_epoch_timestamp(date_string):
    dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return int(dt.timestamp())

def auth():
    # Get the uid
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    global models
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    global uid
    count = 0
    while count < 30:
        try:
            uid = common.authenticate(db, username, password, {})
            if uid:
                return True
            else:
                return False
        except ConnectionRefusedError as ce:
            print(f"Caught connection exception! {ce}")
            sleep(30)
            count += 1
            continue

def mark_attendance(checkx, identification_id, epoch):
    if not auth():
        print("Server not available!")
        return False
    # Get the models object
    # models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee
    employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[['identification_id', '=', identification_id]]])
    if not employee_ids:
        print(f"No employee found with ID {identification_id}.")
        return False
    # Convert epoch to datetime in UTC
    # dt = datetime.utcfromtimestamp(epoch)
    odoo_time = dateFormatOdoo(epoch)

    # Format datetime in ISO 8601 format
    # odoo_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    try:
        # Your XML-RPC code here
        # Search for existing attendance record
        attendance_ids = models.execute_kw(db, uid, password, 'hr.attendance', 'search', [[('employee_id', '=', employee_ids[0]), (checkx, '=', odoo_time)]])
        if attendance_ids:
            # Attendance record already exists
            print(f"Attendance record already exists for employee with ID {identification_id} at {odoo_time}.")
            return False
        else:
            # Create new attendance record
            attendance_id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [{'employee_id': employee_ids[0], checkx : odoo_time}])
            # print(f"Attendance marked for employee with ID {identification_id}. Attendance ID is {attendance_id}.")
            return True
    except xmlrpc.client.Fault as fault:
        print(f"An XML-RPC fault occurred: {fault}")
        return False

def checkout(identification_id, epoch, idd):
    # Check if authenticated
    if not auth():
        return False
    # Get the attendance model
    checkout_time = dateFormatOdoo(epoch)
    # 
    # attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee's attendance records that have no check out
    attendance_ids = models.execute_kw(db, uid, password,
        'hr.attendance', 'search',
        [[['employee_id.identification_id', '=', identification_id], ['check_out', '=', False]]])
    if len(attendance_ids) == 0:
        print("No existing checkin!")
        return False
    else:
        # Read the checkin time of the records
        checkin_times = models.execute_kw(db, uid, password,
            'hr.attendance', 'read',
            [attendance_ids, ['check_in']])
        for record in checkin_times:
            # Convert the checkin time to a datetime object
            # If the time difference is more than 30 minutes, set the check out time to the current time
            # attendance.execute_kw(db, uid, password,
            #         'hr.attendance', 'write',
            #         [[record['id']], {'check_out': checkout_time}])
            models.execute_kw(db, uid, password,
                    'hr.attendance', 'write',
                    [idd, {'check_out': checkout_time}])
    return True

def verify_existing_checkin(identification_id, YYYY, MM, DD):
    # Check if authenticated
    if not auth():
        return False

    # Get the attendance model
    # attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Model and field details
    model_name = 'hr.attendance'

    # Specify the date you want to check attendance for
    date_to_check = datetime(YYYY, MM, DD)

    # Get the employee's ID
    employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[('identification_id', '=', identification_id)]])
    if not employee_ids:
        return []

    # Search for the employee's attendance records for the specified date
    attendance_records = models.execute_kw(db, uid, password, model_name, 'search_read', [[('employee_id', '=', employee_ids[0]), ('check_in', '>=', date_to_check.strftime('%Y-%m-%d 00:00:00')), ('check_in', '<=', date_to_check.strftime('%Y-%m-%d 23:59:59'))]], {'fields': ['check_in', 'check_out']})

    # Prepare the list of day records
    day_list = []
    for record in attendance_records:
        day_status = {'Badge': identification_id, 'checkin': record['check_in'], 'checkout': record['check_out']}
        day_list.append(day_status)

    return day_list

def get_attendance_times(identification_id, YYYY, MM, DD, test=False):
    data = {}
    if not auth():
        return False
    # common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    # uid = common.authenticate(db, username, password, {})
    # models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Format the date in the 'YYYY-MM-DD' format
    date = datetime(YYYY, MM, DD)
    date_str = date.strftime('%Y-%m-%d')

    # Add the date criteria to the search
    attendance_ids = models.execute_kw(db, uid, password,
        'hr.attendance', 'search', [[['employee_id.identification_id', '=', identification_id], ['check_in', '>=', date_str], ['check_in', '<', date_str + ' 23:59:59']]])

    attendances = models.execute_kw(db, uid, password,
        'hr.attendance', 'read', [attendance_ids, ['check_in', 'check_out']])
    id = 0
    for attendance in attendances:
        # print(f"Check-in: {attendance['check_in']}, Check-out: {attendance['check_out']}")
        if  attendance.get('id') >= id:
            data.update({"id": attendance['id'], "check_in": attendance['check_in'], "check_out": attendance['check_out']})
        id = attendance.get('id')
    return data

def get_done_date(mac, YYYY, MM, DD, test=False):
    # {'id': 75, 'check_in': '2023-12-01 08:00:48', 'check_out': '2023-12-01 18:53:49'}
    data = get_attendance_times(mac, YYYY, MM, DD, test)
    if data:
        if data.get('id') and data.get('check_in') and data.get('check_out'):
            return True
        elif data.get('id') and data.get('check_in') and not data.get('check_out'):
            if delete_attendance_by_date_and_id(mac, YYYY, MM, DD, test):
                print(f"Partial record deleted fill reattempt for {mac} {YYYY} {MM} {DD}")
                return False
            else:
                print(f"Could not delete Partial record, fill reattempt for {mac} {YYYY} {MM} {DD}")
                """Todo handle is delete fails"""
                return False
        elif not data.get('id') and not data.get('check_in') and not data.get('check_out'):
            return False
    return False


def delete_attendance_by_date_and_id(identification_id, YYYY, MM, DD, test=False):
    if not auth():
        return False
    # common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    # uid = common.authenticate(db, username, password, {})

    # models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Format the date in the 'YYYY-MM-DD' format
    date = datetime(YYYY, MM, DD)
    date_str = date.strftime('%Y-%m-%d')

    # Search for the attendance records with the given identification_id and date
    attendance_ids = models.execute_kw(db, uid, password,
        'hr.attendance', 'search', [[['employee_id.identification_id', '=', identification_id], ['check_in', '>=', date_str], ['check_in', '<', date_str + ' 23:59:59']]])
    # print(attendance_ids)
    # Delete the attendance records
    result = models.execute_kw(db, uid, password,
        'hr.attendance', 'unlink', [attendance_ids])
    return result



def odoo_version():
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    return common.version()

def get_employee_id(identification_id):
    if auth():
        employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[['identification_id', '=', identification_id]]])
        return employee_ids[0]

def get_attandanceids(employee_id):
    if auth():
        attendance_ids = models.execute_kw(db, uid, password, 'hr.attendance', 'search', [[('employee_id', '=', employee_id)]])
        return sorted(attendance_ids)

def get_latest_attndance_time(employee_id):
    attendance_id = max(get_attandanceids(employee_id))
    attendance_data = []
    if attendance_id:
        # Get the check-in and check-out times for a specific attendance ID
        attendance_data = models.execute_kw(db, uid, password, 'hr.attendance', 'read', [attendance_id], {'fields': ['check_in', 'check_out']})

    for val in attendance_data[-1].values():
        if not val:
            return False
    return attendance_data[-1]

def find_next_non_zero_timestamp(start_timestamp):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname='your_db_name',
            user='your_db_user',
            password='your_db_password',
            host='your_db_host'
        )

        # Create a cursor object
        cursor = conn.cursor()

        # Prepare the SQL query
        query = """
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
                AND ts > extract(epoch from %s::timestamp) * 1000 -- Only timestamps in the future from the specified start time
                AND (x_axis != 0 OR y_axis != 0 OR z_axis != 0) -- Check for non-zero values
            ORDER BY ts ASC -- Order by timestamp in ascending order
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





            
         



    

# Usage:
# get_attendance_times('myid', datetime(2024, 2, 15))
