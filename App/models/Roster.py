from App.database import db
from datetime import date



class Roster(db.Model):
    rosterId = db.Column(db.Integer, primary_key=True)
    StaffId = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    ShiftId = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=True)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    
    

    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate 
        
