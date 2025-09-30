
from App.database import db
from sqlalchemy import UniqueConstraint

class ShiftAssignment(db.Model):
    __tablename__ = 'shift_assignment'
    
    # Composite Primary Key
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), primary_key=True)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), primary_key=True)

    time_in = db.Column(db.Time, nullable=True)
    time_out = db.Column(db.Time, nullable=True)
    
    # Relationships to access the related objects
    staff = db.relationship('Staff', back_populates='assignments')
    shift = db.relationship('Shift', back_populates='assignments')

    def __init__(self, staff_id, shift_id):
        self.staff_id = staff_id
        self.shift_id = shift_id
        
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

    def calculate_duration(self):
        if self.time_in and self.time_out:
            # Convert time objects to datetime for subtraction
            from datetime import datetime
            dt_in = datetime.combine(datetime.min, self.time_in)
            dt_out = datetime.combine(datetime.min, self.time_out)
            duration = dt_out - dt_in
            #conversion to hours (as a float)
            return round(duration.total_seconds() / 3600, 2)
        return 0