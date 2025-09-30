import click, pytest, sys
from flask.cli import with_appcontext, AppGroup
from App.database import db, get_migrate
from App.models import User # Assuming User model exists
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.controllers.staff import *
from App.controllers.shift import *
from App.controllers.shiftAssignment import assign_staff_to_shift, get_combined_roster_json, get_shift_report_for_period
from App.controllers.timeclock import staff_time_in, staff_time_out
from click import DateTime
from datetime import time ,date,datetime



app = create_app()
migrate = get_migrate(app)

@app.cli.command("init", help="Creates and initializes the database")

def init():
    initialize()
    print('database intialized')

'''
Admin Commands
'''
admin_cli = AppGroup('admin', help='Admin object commands')

@admin_cli.command("create", help="Creates a staff user")
@click.argument("staffname", type=str)

def createStaff(staffname):
    new_staff=create_staff(staffname=staffname)
    staffid=new_staff.id
    print(f'{staffname} created!, Your ID is {staffid}')
    return new_staff

@admin_cli.command("c_shift", help="Creates a shift")
@click.argument("day", type=DateTime(formats=["%Y-%m-%d"]))

def createShift(day):
    new_shift = create_shift(shift_day=day.date())
    day=new_shift.day
    print(f'Shift created for {day}')
    return new_shift

@admin_cli.command("assign_staff", help="(Admin) Assigns a staff member (Staff ID) to an existing shift (Shift ID).")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)

def assignStaffToShift(staff_id, shift_id):
    print(f"Attempting to assign Staff ID {staff_id} to Shift ID {shift_id}...")

    result = assign_staff_to_shift(
        staff_id=staff_id, 
        shift_id=shift_id
    )
    
    if result.get("error"):
        print(f"Assignment FAILED: {result['error']}")
    else:
        print(f"Assignment SUCCESSFUL: {result['message']}")
    
    return result

@admin_cli.command("shift_report", help="(Admin) View shift report for a date range.")
@click.argument("start_date", type=DateTime(formats=["%Y-%m-%d"]))
@click.argument("end_date", type=DateTime(formats=["%Y-%m-%d"]))

def getShiftReport(start_date, end_date):
    report = get_shift_report_for_period(start_date.date(), end_date.date())
    print(f"Shift Report for {report['period_start']} to {report['period_end']}:")
    
    if not report['staff_work_summary']:
        print("No completed shifts found in this period.")
        return

    for staff_id, data in report['staff_work_summary'].items():
        print(f"\n--- {data['staff_name']} (ID: {staff_id}) ---")
        print(f"TOTAL HOURS WORKED: {data['total_hours']}")
        for shift in data['shifts']:
            print(f"  {shift['shift_day']}: {shift['time_in']} - {shift['time_out']} ({shift['duration_hours']} hrs)")

'''
Staff Commands
'''

staff_cli = AppGroup('staff', help='Staff object commands')

@staff_cli.command("view_roster", help="(Staff) View combined roster of all staff.")

def viewRoster():
    roster = get_combined_roster_json()
    print("\n--- Combined Staff Roster ---")
    if not roster:
        print("Roster is currently empty.")
        return

    for entry in roster:
        print(f"Day: {entry['day']} | Staff: {entry['staff_name']} | Shift ID: {entry['shift_id']}")

@staff_cli.command("time_in", help="(Staff) Time in at the start of shift.")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.argument("time_in_str", type=click.STRING) # Expecting "HH:MM:SS"

def timeIn(staff_id, shift_id, time_in_str):
    try:
        t_in = datetime.strptime(time_in_str, "%H:%M:%S").time()
    except ValueError:
        print("Error: Time in format must be 'HH:MM:SS'.")
        return

    result = staff_time_in(staff_id, shift_id, t_in)
    print(result.get("message") or result.get("error"))

@staff_cli.command("time_out", help="(Staff) Time out at the end of shift.")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.argument("time_out_str", type=click.STRING) # Expecting "HH:MM:SS"

def timeOut(staff_id, shift_id, time_out_str):
    try:
        t_out = datetime.strptime(time_out_str, "%H:%M:%S").time()
    except ValueError:
        print("Error: Time out format must be 'HH:MM:SS'.")
        return

    result = staff_time_out(staff_id, shift_id, t_out)
    print(result.get("message") or result.get("error"))


app.cli.add_command(admin_cli) 
app.cli.add_command(staff_cli)