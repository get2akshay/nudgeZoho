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

def mark_attendance(identification_id):
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
        attendance_id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [{'employee_id': employee_ids[0], 'check_in': '2024-02-15 08:00:00'}])
        print(f"Attendance marked for employee with ID {identification_id}. Attendance ID is {attendance_id}.")
    else:
        print(f"No employee found with ID {identification_id}.")