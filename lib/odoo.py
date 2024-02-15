import xmlrpc.client
from datetime import datetime, timedelta

# Specify your Odoo server information
# url = 'https://byplayit2.odoo.com/'
url = 'http://65.20.78.99:8069/'
db = 'nudge'
username = 'akshay.sharma@byplayit.com'
password = 'akshay911'

# Specify the employee's identification ID
# identification_id = '00:8c:10:30:02:6f'


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



def mark_attendance(checkx,identification_id, epoch):
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
        print(f"Attendance marked for employee with ID {identification_id}. Attendance ID is {attendance_id}.")
    else:
        print(f"No employee found with ID {identification_id}.")


