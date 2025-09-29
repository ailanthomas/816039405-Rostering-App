from App.database import db
from datetime import date,time

class shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rosterId = db.Column(db.Integer, db.ForeignKey('roster.rosterId',use_alter=True), nullable=True)
    Day = db.Column(db.Date, nullable=False)
    timeIn = db.Column(db.Time, nullable=True)
    timeOut = db.Column(db.Time, nullable=True)

    def __init__(self,rosterId, Day):
        self.rosterId = rosterId
        self.Day = Day
