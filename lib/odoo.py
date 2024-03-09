import xmlrpc.client
from datetime import datetime
import http.client
from time import sleep
from pdb import set_trace
from urllib.parse import urlparse
import pytz
# IST = pytz.timezone('Asia/Kolkata')  # Define the IST timezone
# Define the UTC timezone
UTC = pytz.utc

# Specify your Odoo server information
# url = 'https://byplayit2.odoo.com/'
url = 'http://65.20.78.99:8069/'
db = 'nudge'
username = 'akshay.sharma@byplayit.com'
password = 'akshay911'
# Odoo XML-RPC endpoint
common_endpoint = f"{url}/xmlrpc/2/common"
object_endpoint = f"{url}/xmlrpc/2/object"
timeout = 30

# Function to create a ServerProxy instance with timeout
def server_proxy(endpoint, timeout):
    # parsed_url = urlparse(endpoint)
    # connection = http.client.HTTPConnection(parsed_url.hostname, parsed_url.port, timeout=timeout)
    # transport = xmlrpc.client.Transport()
    # transport._connection = connection
    return xmlrpc.client.ServerProxy(endpoint)

# Function to authenticate with Odoo
def authenticate_with_odoo(timeout):
    endpoint = common_endpoint
    common_proxy = server_proxy(endpoint, timeout)
    return common_proxy.authenticate(db, username, password, {})

uid = authenticate_with_odoo(timeout)

def dateFormatOdoo(timestamp):
    """
    Convert the timestamp to IST format.
    """
    # Convert the timestamp to a datetime object
    dt = datetime.fromtimestamp(timestamp)
    # Convert the datetime object to IST timezone
    dt_ist = dt.astimezone(UTC)
    # Format the datetime in the required format (assuming 'YYYY-MM-DD HH:mm:ss')
    return dt_ist.strftime('%Y-%m-%d %H:%M:%S')

def get_epoch_timestamp(date_string):
    dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return int(dt.timestamp())

def auth():
    # Get the uid
    common = xmlrpc.client.ServerProxy(common_endpoint)
    global models
    models = xmlrpc.client.ServerProxy(object_endpoint)
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
    checkout_time = dateFormatOdoo(epoch)
    # attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee's attendance records that have no check out
    try:
        models = server_proxy(object_endpoint, timeout=timeout)
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
    except xmlrpc.client.Fault as fault:
        print(f"An XML-RPC fault occurred: {fault}")
        return False
    

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
    models = server_proxy(object_endpoint, timeout=timeout)
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
    models = server_proxy(object_endpoint, timeout=timeout)
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
    models = server_proxy(object_endpoint, timeout=timeout)
    employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[['identification_id', '=', identification_id]]])
    if (len(employee_ids)) == 0:
        return False
    else:
        return employee_ids[0]

def get_attandanceids(employee_id):
    models = server_proxy(object_endpoint, timeout=timeout)
    retry_count = 3
    attendance_ids = []
    while retry_count > 0:
        try:
            # Attempt to fetch attendance IDs
            attendance_ids = models.execute_kw(db, uid, password, 'hr.attendance', 'search', [[('employee_id', '=', employee_id)]])
            return sorted(attendance_ids)
        except xmlrpc.client.ProtocolError as e:
            print("Error occurred while sending the request:", e)
            retry_count -= 1
            if retry_count == 0:
                print("Retry limit exceeded.")
                raise
            print(f"Retrying after 10 seconds. Retry attempts left: {retry_count}")
            sleep(10)
        except Exception as e:
            print("An unexpected error occurred:", e)
            sleep(10)
    return None

def get_latest_attndance_time(identification_id):
    models = server_proxy(object_endpoint, timeout=timeout)
    employee_id = get_employee_id(identification_id)
    if not employee_id:
            return False
    ids = get_attandanceids(employee_id)
    if ids:
        attendance_id = max(ids)
        attendance_data = []
        if attendance_id:
            # Get the check-in and check-out times for a specific attendance ID
            attendance_data = models.execute_kw(db, uid, password, 'hr.attendance', 'read', [attendance_id], {'fields': ['check_in', 'check_out']})

        # for val in attendance_data[-1].values():
            # if not val:
                # return False
        return attendance_data[-1]
    else:
        return {"id": False, "check_in": False, "check_out": False}

# Function to check-in using employee ID
def checkin_employee(identification_id, timestamp):
    # models_proxy = xmlrpc.client.ServerProxy(object_endpoint)
    # Check if authenticated
    models = server_proxy(object_endpoint, timeout=timeout)
    try:
        employee_id = get_employee_id(identification_id)
        if not employee_id:
            return False
        # Search for the employee based on employee ID
        # employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[('employee_id', '=', employee_id)]])
        employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[['identification_id', '=', identification_id]]])
        
        if employee_ids:
            # Employee found, perform check-in
            attendance_data = {
                'employee_id': employee_ids[0],
                'check_in': dateFormatOdoo(timestamp),
            }
            attendance_id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [attendance_data])
            if attendance_id:
                print(f"Checked in for Employee ID {employee_id} at {timestamp}")
                return True
            else:
                print(f"Failed to check in for Employee ID {employee_id}")
                return False
        else:
            print(f"Employee with ID {employee_id} not found.")
            return False
    except xmlrpc.client.Fault as fault:
        print(f"An XML-RPC fault occurred: {fault}")
        return False

# Function to check-out using employee ID
def checkout_employee(identification_id, timestamp, idd):
    # models_proxy = xmlrpc.client.ServerProxy(object_endpoint)
    # Check if authenticated
    models = server_proxy(object_endpoint, timeout=timeout)
    employee_id = get_employee_id(identification_id)
    try:
        nidd = models.execute_kw(db, uid, password,'hr.attendance', 'write', [[idd], {'check_out': dateFormatOdoo(timestamp), 'employee_id': employee_id}])
        return nidd
    except xmlrpc.client.Fault as fault:
        print(f"An XML-RPC fault occurred: {fault}")
        return False

# Function to create break time record for an employee
def mark_break_time(identification_id, start_date, end_date):
    # Check if authenticated
    models = server_proxy(object_endpoint, timeout=timeout)
    employee_id = get_employee_id(identification_id)
    if not employee_id:
            return False
    # Search for the leave type representing break time
    leave_type_id = models.execute_kw(db, uid, password, 'hr.leave.type', 'search', 
                                            [[('name', '=', 'Break Time')]])
    if leave_type_id:
        leave_type_id = leave_type_id[0]
    else:
        print("Break Time leave type not found.")
        return

    # Create leave record for break time
    leave_data = {
        'employee_id': employee_id,
        'holiday_status_id': leave_type_id,
        'request_date_from': dateFormatOdoo(start_date),
        'request_date_to': dateFormatOdoo(end_date),
        'state': 'validate',  # Optional: Set to 'validate' to automatically approve the break time
    }
    leave_id = models.execute_kw(db, uid, password, 'hr.leave', 'create', [leave_data])
    if leave_id:
        print("Break time marked successfully.")
    else:
        print("Failed to mark break time.")


def checkout_timestamp_diff(check_out, its):
    # Convert the string to a datetime object
    utc_time = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S")
    # Calculate the epoch time (seconds since January 1, 1970)
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    print(f"Epoch time for {check_out} is: {int(epoch_time)} seconds")
    return (epoch_time - its)

