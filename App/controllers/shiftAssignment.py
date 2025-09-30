from App.database import db
from App.models import ShiftAssignment, Staff, Shift
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

def assign_staff_to_shift(staff_id: int, shift_id: int) -> dict:
    """
    (Admin) Assigns a staff member to a shift. Implements logic to prevent double-booking.
    """
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

    new_assignment = ShiftAssignment(
        staff_id=staff_id,
        shift_id=shift_id
    )

    try:
        db.session.add(new_assignment)
        db.session.commit()
        return {
            "message": f"Staff {staff.staffname} successfully assigned to shift on {shift.day.isoformat()}.",
            "staff_id": staff_id,
            "shift_id": shift_id
        }
    except IntegrityError:
        db.session.rollback()
        return {"error": "Assignment already exists (Staff ID and Shift ID combination)."}
    except Exception as e:
        db.session.rollback()
        return {"error": f"Database error during assignment: {str(e)}"}

def get_combined_roster_json() -> list:
    """
    (Staff) Retrieves the combined roster of all staff for the current and future periods.
    """
    assignments = ShiftAssignment.query.join(Shift).all()
    
    # Sort by day, then staff name for a clean roster view
    assignments.sort(key=lambda a: (a.shift.day, a.staff.staffname))

    roster = []
    for a in assignments:
        roster.append({
            'day': a.shift.day.isoformat(),
            'staff_name': a.staff.staffname,
            'shift_id': a.shift_id,
            # Placeholder for scheduled shift times if they were in the Shift model
        })
    return roster

def get_shift_report_for_period(start_date: date, end_date: date) -> dict:
    """
    (Admin) View shift report for the week/period.
    Shows who worked, when, and for how long (duration).
    """
    report_data = ShiftAssignment.query\
        .join(Shift)\
        .filter(Shift.day.between(start_date, end_date))\
        .filter(ShiftAssignment.time_in.isnot(None))\
        .filter(ShiftAssignment.time_out.isnot(None))\
        .all()
        
    report = {
        'period_start': start_date.isoformat(),
        'period_end': end_date.isoformat(),
        'staff_work_summary': {} # {staff_id: {total_hours: 0, shifts: []}}
    }

    for assignment in report_data:
        staff_id = assignment.staff_id
        staff_name = assignment.staff.staffname
        duration = assignment.calculate_duration()
        
        shift_details = assignment.get_json()
        
        if staff_id not in report['staff_work_summary']:
            report['staff_work_summary'][staff_id] = {
                'staff_name': staff_name,
                'total_hours': 0.0,
                'shifts': []
            }

        report['staff_work_summary'][staff_id]['total_hours'] += duration
        report['staff_work_summary'][staff_id]['shifts'].append({
            'shift_day': shift_details['shift_day'],
            'time_in': shift_details['time_in'],
            'time_out': shift_details['time_out'],
            'duration_hours': duration
        })

    # Final formatting for total hours
    for staff_data in report['staff_work_summary'].values():
        staff_data['total_hours'] = round(staff_data['total_hours'], 2)

    return report