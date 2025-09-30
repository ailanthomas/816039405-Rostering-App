from App.database import db
from App.models import Shift
from datetime import date

def create_shift(shift_day: date):
    
    new_shift = Shift(
        day=shift_day
    )
    
    db.session.add(new_shift)
    db.session.commit()
    return new_shift

# Removed assign_staff_to_shift from here, it's now in App.controllers.shiftAssignment