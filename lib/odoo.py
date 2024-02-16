import xmlrpc.client
from datetime import datetime, timedelta

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

def auth():
    # Get the uid
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    global uid
    uid = common.authenticate(db, username, password, {})
    if uid:
        return True
    else:
        return False

def get_checkin(identification_id):
    # Check if authenticated
    if not auth():
        return False
    # Get the attendance model
    attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee's attendance records
    attendance_ids = attendance.execute_kw(db, uid, password,
        'hr.attendance', 'search',
        [[['employee_id.identification_id', '=', identification_id]]])
    # Read the checkin time of the records
    checkin_times = attendance.execute_kw(db, uid, password,
        'hr.attendance', 'read',
        [attendance_ids, ['check_in']])
    # Return the checkin times as a list
    return [record['check_in'] for record in checkin_times]

def auto_checkout(identification_id, epoch_time=None):
    # Check if authenticated
    delta_minutes = 30
    if not auth():
        return False
    # Get the attendance model
    attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee's attendance records that have no check out
    attendance_ids = attendance.execute_kw(db, uid, password,
        'hr.attendance', 'search',
        [[['employee_id.identification_id', '=', identification_id], ['check_out', '=', False]]])
    # Read the checkin time of the records
    checkin_times = attendance.execute_kw(db, uid, password,
        'hr.attendance', 'read',
        [attendance_ids, ['check_in']])
    # Loop through the records and check the time difference
    for record in checkin_times:
        # Convert the checkin time to a datetime object
        checkin_time = datetime.strptime(record['check_in'], '%Y-%m-%d %H:%M:%S')
        # Get the current time
        current_time = datetime.now()
        if epoch_time is not None:
            checkin_time = epoch_time
        # Calculate the time difference in minutes
        time_diff = (current_time - checkin_time).total_seconds() / 60
        # If the time difference is more than 30 minutes, set the check out time to the current time
        if time_diff > delta_minutes:
            attendance.execute_kw(db, uid, password,
                'hr.attendance', 'write',
                [[record['id']], {'check_out': current_time.strftime('%Y-%m-%d %H:%M:%S')}])



def mark_attendancew(checkx,identification_id, epoch):
    if auth():
        print("Server available!")
    else:
        return False
    # Get the models object
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee
    employee_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[['identification_id', '=', identification_id]]])
    if employee_ids:
        # Mark the attendance
        attendance_id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [{'employee_id': employee_ids[0], checkx : epoch}])
        # print(f"Attendance marked for employee with ID {identification_id}. Attendance ID is {attendance_id}.")
    else:
        print(f"No employee found with ID {identification_id}.")


def mark_attendance(checkx, identification_id, epoch):
    if not auth():
        print("Server not available!")
        return False

    # Get the models object
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

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

    # Search for existing attendance record
    attendance_ids = models.execute_kw(db, uid, password, 'hr.attendance', 'search', [[('employee_id', '=', employee_ids[0]), (checkx, '=', odoo_time)]])
    
    if attendance_ids:
        # Attendance record already exists
        print(f"Attendance record already exists for employee with ID {identification_id} at {odoo_time}.")
        return False
    else:
        # Create new attendance record
        attendance_id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [{'employee_id': employee_ids[0], checkx : odoo_time}])
        print(f"Attendance marked for employee with ID {identification_id}. Attendance ID is {attendance_id}.")
        return True



def checkout(identification_id, epoch):
    # Check if authenticated
    if not auth():
        return False
    # Get the attendance model
    checkout_time = dateFormatOdoo(epoch)
    # 
    attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee's attendance records that have no check out
    attendance_ids = attendance.execute_kw(db, uid, password,
        'hr.attendance', 'search',
        [[['employee_id.identification_id', '=', identification_id], ['check_out', '=', False]]])
    if len(attendance_ids) == 0:
        print("No existing checkin!")
        return False
    else:
        # Read the checkin time of the records
        checkin_times = attendance.execute_kw(db, uid, password,
            'hr.attendance', 'read',
            [attendance_ids, ['check_in']])
        for record in checkin_times:
            # Convert the checkin time to a datetime object
            # If the time difference is more than 30 minutes, set the check out time to the current time
            attendance.execute_kw(db, uid, password,
                    'hr.attendance', 'write',
                    [[record['id']], {'check_out': checkout_time}])
    return True


def tverify_existing_checkin(identification_id, YYYY, MM, DD):
    # Day record
    day_status = {}
    day_list = []
    # Check if authenticated
    if not auth():
        return False
    # Get the attendance model
    attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Search for the employee's attendance records that have no check out
    # Model and field details
    model_name = 'hr.attendance'
    # Specify the date you want to check attendance for
    date_to_check = datetime(YYYY, MM, DD)
    # Search for attendance records for the specified date
    attendance_records = attendance.execute_kw(db, uid, password, model_name, 'search_read', [[('check_in', '>=', date_to_check.strftime('%Y-%m-%d 00:00:00')), ('check_in', '<=', date_to_check.strftime('%Y-%m-%d 23:59:59'))]], {'fields': ['employee_id', 'check_in', 'check_out']})
    # Print the attendance records
    for record in attendance_records:
        print(f"Employee ID: {record['employee_id'][1]}, Check In: {record['check_in']}, Check Out: {record['check_out']}")
    # Print the attendance records
    for record in attendance_records:
        # Get the employee's identification_id
        employee = attendance.execute_kw(db, uid, password, 'hr.employee', 'read', [record['employee_id'][0]], {'fields': ['identification_id']})
        print(f"Employee ID: {record['employee_id'][1]}, Identification ID: {employee[0]['identification_id']}, Check In: {record['check_in']}, Check Out: {record['check_out']}")
        day_status.update({'Badge': employee[0]['identification_id'], 'checkin': record['check_in'], 'checkout': record['check_out']})
        day_list.append(day_status)   
    return day_list

def verify_existing_checkin(identification_id, YYYY, MM, DD):
    # Check if authenticated
    if not auth():
        return False

    # Get the attendance model
    attendance = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Model and field details
    model_name = 'hr.attendance'

    # Specify the date you want to check attendance for
    date_to_check = datetime(YYYY, MM, DD)

    # Get the employee's ID
    employee_ids = attendance.execute_kw(db, uid, password, 'hr.employee', 'search', [[('identification_id', '=', identification_id)]])
    if not employee_ids:
        return []

    # Search for the employee's attendance records for the specified date
    attendance_records = attendance.execute_kw(db, uid, password, model_name, 'search_read', [[('employee_id', '=', employee_ids[0]), ('check_in', '>=', date_to_check.strftime('%Y-%m-%d 00:00:00')), ('check_in', '<=', date_to_check.strftime('%Y-%m-%d 23:59:59'))]], {'fields': ['check_in', 'check_out']})

    # Prepare the list of day records
    day_list = []
    for record in attendance_records:
        day_status = {'Badge': identification_id, 'checkin': record['check_in'], 'checkout': record['check_out']}
        day_list.append(day_status)

    return day_list
