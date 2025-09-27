from App.database import db

class Roster(db.Model):
    rosterId = db.Column(db.Integer, primary_key=True)
    startDate = db.Column(db.date, nullable=False)
    endDate = db.Column(db.date, nullable=False)
    publicHoliday = db.Column(db.boolean, nullable=False)
    
    

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

