from App.database import db
from datetime import date
from sqlalchemy import UniqueConstraint

# This model defines the full week/period for which a set of shifts is being planned.
class RosteringPeriod(db.Model):
    __tablename__ = 'rosteringPeriod'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Store the user-entered start and end dates for the period
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    
    # Ensures no two rostering periods can start and end on the exact same dates
    __table_args__ = (
        UniqueConstraint('startDate', 'endDate', name='uix_start_end_date'),
    )
    
    def __init__(self, startDate: date, endDate: date):
        self.startDate = startDate
        self.endDate = endDate 
        
    def get_json(self):
        return {
            'id': self.id,
            'start_date': self.startDate.isoformat(),
            'end_date': self.endDate.isoformat()
        }