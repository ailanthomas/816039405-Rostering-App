from App.database import db
from App.models import Staff

def create_staff(staffname):
    """Creates a new Staff record."""
    newstaff = Staff(staffname=staffname)
    db.session.add(newstaff)
    db.session.commit()
    return newstaff

def get_all_staff_json():
    """Retrieves all staff records and converts them to a list of JSON dictionaries."""
    staff_objects = Staff.query.all()
    return [s.get_json() for s in staff_objects]