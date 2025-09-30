from App.database import db
from App.models import ShiftAssignment
from datetime import time, datetime 

def staff_time_in(staff_id: int, shift_id: int, time_in: time) -> dict:
    """
    Staff records their start time for an assigned shift.
    """
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
    """
    Staff records their end time for an assigned shift.
    """
    assignment = ShiftAssignment.query.filter_by(staff_id=staff_id, shift_id=shift_id).first()
    if not assignment:
        return {"error": f"No assignment found for Staff ID {staff_id} on Shift ID {shift_id}."}
    if not assignment.time_in:
        return {"error": "Staff must time in before timing out."}  
    if assignment.time_out:
        return {"error": "Staff has already timed out for this shift."}

    # Basic validation: time_out must be after time_in (simplified: comparing just time objects)
    if datetime.combine(datetime.min, time_out) <= datetime.combine(datetime.min, assignment.time_in):
        return {"error": "Time out must be after time in."}

    assignment.time_out = time_out
    db.session.add(assignment)
    db.session.commit()
    return {"message": f"Staff ID {staff_id} timed out at {time_out.isoformat()} for Shift ID {shift_id}."}