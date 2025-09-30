from App.database import db
from datetime import date,time

class Shift(db.Model):
    __tablename__ = 'shift'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False) 

    assignments = db.relationship('ShiftAssignment', back_populates='shift', cascade='all, delete-orphan')

    def __init__(self, day):
        self.day = day

    def get_json(self):
        return {
            'id': self.id,
            'day': self.day.isoformat(),
            'num_staff_assigned': len(self.assignments)
        }