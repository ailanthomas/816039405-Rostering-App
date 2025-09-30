

# Dependencies
* Python3/pip3
* Packages listed in requirements.txt

# Installing Dependencies
```bash
$ pip install -r requirements.txt
```

# Configuration Management


Configuration information such as the database url/port, credentials, API keys etc are to be supplied to the application. However, it is bad practice to stage production information in publicly visible repositories.
Instead, all config is provided by a config file or via [environment variables](https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/).


# Flask Commands

wsgi.py is a utility script for performing various tasks related to the project. You can use it to import and test any code in the project. 
You just need create a manager command function, for example:








```python 


# =====================================================================
# CLI COMMANDS
# =====================================================================

app = create_app()

# Base Init Command
init_cli = AppGroup('init', help='Initializes the database')
@init_cli.command("init", help="Creates and initializes the database")


# --- Admin Commands ---
admin_cli = AppGroup('admin', help='Admin object commands')

#Create a Staff
@admin_cli.command("create", help="Creates a staff user")
@click.argument("staffname", type=str)


#Create Shift
@admin_cli.command("c_shift", help="Creates a shift")
@click.argument("day", type=click.DateTime(formats=["%Y-%m-%d"]))


#Assign Staff cmd
@admin_cli.command("assign_staff", help="(Admin) Assigns a staff member (Staff ID) to an existing shift (Shift ID).")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)


#View Shift report cmd 
@admin_cli.command("shift_report", help="(Admin) View shift report for a date range.")
@click.argument("start_date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.argument("end_date", type=click.DateTime(formats=["%Y-%m-%d"]))
def getShiftReport(start_date, end_date):


# --- Staff Commands ---
staff_cli = AppGroup('staff', help='Staff object commands')

#View Roster cmd
@staff_cli.command("view_roster", help="(Staff) View combined roster of all staff.")

#Time in cmd
@staff_cli.command("time_in", help="(Staff) Time in at the start of shift.")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.argument("time_in_str", type=click.STRING) # Expecting "HH:MM:SS"


#time out cmd
@staff_cli.command("time_out", help="(Staff) Time out at the end of shift.")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.argument("time_out_str", type=click.STRING) # Expecting "HH:MM:SS"



# =====================================================================
# 2. MODELS
# =====================================================================

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aName =  db.Column(db.String(20), nullable=False, unique=False)
    
    def __init__(self, aName):
        self.aName = aName
        
    def get_json(self):
        return{'id': self.id, 'aName': self.aName}

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    staffname = db.Column(db.String(120), nullable=False)
    
    assignments = db.relationship('ShiftAssignment', back_populates='staff', cascade='all, delete-orphan')

    def __init__(self, staffname):
        self.staffname = staffname
        
    def get_json(self):
        return {'id': self.id, 'staffname': self.staffname}

    def __repr__(self):
        return f'<Staff {self.id}: {self.staffname}>'

class Shift(db.Model):
    __tablename__ = 'shift'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False) 

    assignments = db.relationship('ShiftAssignment', back_populates='shift', cascade='all, delete-orphan')

    def __init__(self, day):
        self.day = day

    def get_json(self):
        return {'id': self.id, 'day': self.day.isoformat()}


class ShiftAssignment(db.Model):
    __tablename__ = 'shift_assignment'
    
    # Composite Primary Key
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), primary_key=True)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), primary_key=True)

    # Time tracking fields (Time In/Time Out)
    time_in = db.Column(db.Time, nullable=True)
    time_out = db.Column(db.Time, nullable=True)
    
    # Relationships 
    staff = db.relationship('Staff', back_populates='assignments')
    shift = db.relationship('Shift', back_populates='assignments')

    def __init__(self, staff_id, shift_id):
        self.staff_id = staff_id
        self.shift_id = shift_id
        
    def calculate_duration(self):
        if self.time_in and self.time_out:
            dt_in = datetime.combine(datetime.min, self.time_in)
            dt_out = datetime.combine(datetime.min, self.time_out)
            duration = dt_out - dt_in
            return round(duration.total_seconds() / 3600, 2)
        return 0

    def get_json(self):
        return {
            'staff_id': self.staff_id,
            'shift_id': self.shift_id,
            'staff_name': self.staff.staffname,
            'shift_day': self.shift.day.isoformat(), 
            'time_in': self.time_in.isoformat() if self.time_in else None,
            'time_out': self.time_out.isoformat() if self.time_out else None,
            'duration_hours': self.calculate_duration()
        }

class RosteringPeriod(db.Model):
    __tablename__ = 'rosteringPeriod'
    
    id = db.Column(db.Integer, primary_key=True)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('startDate', 'endDate', name='uix_start_end_date'),
    )
    
    def __init__(self, startDate: date, endDate: date):
        self.startDate = startDate
        self.endDate = endDate  
        
    def get_json(self):
        return {'id': self.id, 'start_date': self.startDate.isoformat(), 'end_date': self.endDate.isoformat()}

# =====================================================================
# 3. CONTROLLERS
# =====================================================================

# --- Staff Controllers ---

def create_staff(staffname):
    """Creates a new Staff record."""
    newstaff = Staff(staffname=staffname)
    db.session.add(newstaff)
    db.session.commit()
    return newstaff

def get_all_staff_json():
    """Retrieves all staff records."""
    staff_objects = Staff.query.all()
    return [s.get_json() for s in staff_objects]

# --- Shift Controllers ---

def create_shift(shift_day: date):
    """Creates a new Shift record."""
    new_shift = Shift(day=shift_day)
    db.session.add(new_shift)
    db.session.commit()
    return new_shift

# --- ShiftAssignment Controllers (Roster/Reporting) ---

def assign_staff_to_shift(staff_id: int, shift_id: int) -> dict:
    """(Admin) Assigns a staff member to a shift, preventing double-booking."""
    staff = Staff.query.get(staff_id)
    shift = Shift.query.get(shift_id)

    if not staff:
        return {"error": f"Staff with ID {staff_id} not found."}
    if not shift:
        return {"error": f"Shift with ID {shift_id} not found."}

    # Check for double-booking on the same day
    existing_assignment = db.session.query(ShiftAssignment)\
        .join(Shift)\
        .filter(and_(
            ShiftAssignment.staff_id == staff_id,
            Shift.day == shift.day
        ))\
        .first()

    if existing_assignment:
        return {"error": f"Staff {staff.staffname} is already assigned to a shift on {shift.day.isoformat()}."}

    new_assignment = ShiftAssignment(staff_id=staff_id, shift_id=shift_id)

    try:
        db.session.add(new_assignment)
        db.session.commit()
        return {"message": f"Staff {staff.staffname} successfully assigned to shift on {shift.day.isoformat()}.",
                "staff_id": staff_id, "shift_id": shift_id}
    except IntegrityError:
        db.session.rollback()
        return {"error": "Assignment already exists (Staff ID and Shift ID combination)."}
    except Exception as e:
        db.session.rollback()
        return {"error": f"Database error during assignment: {str(e)}"}

def get_combined_roster_json() -> list:
    """(Staff) Retrieves the combined roster of all staff."""
    assignments = ShiftAssignment.query.join(Shift).all()
    assignments.sort(key=lambda a: (a.shift.day, a.staff.staffname))

    roster = []
    for a in assignments:
        roster.append({
            'day': a.shift.day.isoformat(),
            'staff_name': a.staff.staffname,
            'shift_id': a.shift_id,
        })
    return roster

def get_shift_report_for_period(start_date: date, end_date: date) -> dict:
    """(Admin) View shift report for the week/period based on time_in/time_out."""
    report_data = ShiftAssignment.query\
        .join(Shift)\
        .filter(Shift.day.between(start_date, end_date))\
        .filter(ShiftAssignment.time_in.isnot(None))\
        .filter(ShiftAssignment.time_out.isnot(None))\
        .all()
        
    report = {'period_start': start_date.isoformat(), 'period_end': end_date.isoformat(), 'staff_work_summary': {}}

    for assignment in report_data:
        staff_id = assignment.staff_id
        duration = assignment.calculate_duration()
        shift_details = assignment.get_json()
        
        if staff_id not in report['staff_work_summary']:
            report['staff_work_summary'][staff_id] = {
                'staff_name': assignment.staff.staffname, 'total_hours': 0.0, 'shifts': []
            }

        report['staff_work_summary'][staff_id]['total_hours'] += duration
        report['staff_work_summary'][staff_id]['shifts'].append({
            'shift_day': shift_details['shift_day'], 'time_in': shift_details['time_in'],
            'time_out': shift_details['time_out'], 'duration_hours': duration
        })

    for staff_data in report['staff_work_summary'].values():
        staff_data['total_hours'] = round(staff_data['total_hours'], 2)

    return report


# --- Time Clock Controllers ---

def staff_time_in(staff_id: int, shift_id: int, time_in: time) -> dict:
    """Staff records their start time for an assigned shift."""
    assignment = ShiftAssignment.query.filter_by(staff_id=staff_id, shift_id=shift_id).first()
    
    if not assignment:
        return {"error": f"No assignment found for Staff ID {staff_id} on Shift ID {shift_id}."} 
        
    if assignment.time_in:
        return {"error": "Staff has already timed in for this shift."}

    assignment.time_in = time_in
    db.session.add(assignment)
    db.session.commit()
    return {"message": f"Staff ID {staff_id} timed in at {time_in.isoformat()} for Shift ID {shift_id}."}

def staff_time_out(staff_id: int, shift_id: int, time_out: time) -> dict:
    """Staff records their end time for an assigned shift."""
    assignment = ShiftAssignment.query.filter_by(staff_id=staff_id, shift_id=shift_id).first()
    
    if not assignment:
        return {"error": f"No assignment found for Staff ID {staff_id} on Shift ID {shift_id}."}
    
    if not assignment.time_in:
        return {"error": "Staff must time in before timing out."}
        
    if assignment.time_out:
        return {"error": "Staff has already timed out for this shift."}

    # Validation: time_out must be after time_in
    if datetime.combine(datetime.min, time_out) <= datetime.combine(datetime.min, assignment.time_in):
        return {"error": "Time out must be after time in."}

    assignment.time_out = time_out
    db.session.add(assignment)
    db.session.commit()
    return {"message": f"Staff ID {staff_id} timed out at {time_out.isoformat()} for Shift ID {shift_id}."}


# =====================================================================
# 4. CLI COMMANDS
# =====================================================================

app = create_app()

# Base Init Command
init_cli = AppGroup('init', help='Initializes the database')
@init_cli.command("init", help="Creates and initializes the database")
def init():
    with app.app_context():
        initialize()
    print('Database initialized')


# --- Admin Commands ---
admin_cli = AppGroup('admin', help='Admin object commands')

@admin_cli.command("create", help="Creates a staff user")
@click.argument("staffname", type=str)
def createStaff(staffname):
    with app.app_context():
        new_staff=create_staff(staffname=staffname)
        staffid=new_staff.id
    print(f'{staffname} created! Your ID is {staffid}')

@admin_cli.command("c_shift", help="Creates a shift")
@click.argument("day", type=click.DateTime(formats=["%Y-%m-%d"]))
def createShift(day):
    with app.app_context():
        new_shift = create_shift(shift_day=day.date())
        day_str=new_shift.day
    print(f'Shift created for {day_str}')

@admin_cli.command("assign_staff", help="(Admin) Assigns a staff member (Staff ID) to an existing shift (Shift ID).")
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
def assignStaffToShift(staff_id, shift_id):
    print(f"Attempting to assign Staff ID {staff_id} to Shift ID {shift_id}...")
    with app.app_context():
        result = assign_staff_to_shift(staff_id=staff_id, shift_id=shift_id)
    
    if result.get("error"):
        print(f"Assignment FAILED: {result['error']}")
    else:
        print(f"Assignment SUCCESSFUL: {result['message']}")

@admin_cli.command("shift_report", help="(Admin) View shift report for a date range.")
@click.argument("start_date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.argument("end_date", type=click.DateTime(formats=["%Y-%m-%d"]))
def getShiftReport(start_date, end_date):
    with app.app_context():
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


# --- Staff Commands ---
staff_cli = AppGroup('staff', help='Staff object commands')

@staff_cli.command("view_roster", help="(Staff) View combined roster of all staff.")
def viewRoster():
    with app.app_context():
        roster = get_combined_roster_json()
    
    print("\n--- Combined Staff Roster ---")
    if not roster:
        print("Roster is currently empty.")
        return

=





# Troubleshooting

## Views 404ing

If your newly created views are returning 404 ensure that they are added to the list in main.py.

```python
from App.views import (
    user_views,
    index_views
)

# New views must be imported and added to this list
views = [
    user_views,
    index_views
]
```

## Cannot Update Workflow file

If you are running into errors in gitpod when updateding your github actions file, ensure your [github permissions](https://gitpod.io/integrations) in gitpod has workflow enabled ![perms](./images/gitperms.png)

## Database Issues

If you are adding models you may need to migrate the database with the commands given in the previous database migration section. Alternateively you can delete you database file.
