from App.database import db
from App.models import shift
from datetime import date, time

def create_shift(shift_day: date):
    
    default_roster_id = 1
    new_shift = shift(
        rosterId=default_roster_id, 
        Day=shift_day
    )
    
    db.session.add(new_shift)
    db.session.commit()
    return new_shift
