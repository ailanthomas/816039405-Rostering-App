from App.database import db
from App.models import Staff

def create_staff(staffname):
    newstaff = Staff(staffname=staffname)
    db.session.add(newstaff)
    db.session.commit()
    return newstaff

def get_all_staff_json():
    staff = Staff.query.all()
    return [staff.get_json() for sId in staff]