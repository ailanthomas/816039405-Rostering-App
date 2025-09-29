from App.database import db



class Roster(db.Model):
    rosterId = db.Column(db.Integer, primary_key=True)
    startDate = db.Column(db.String, nullable=False)
    endDate = db.Column(db.String, nullable=False)
    
    

    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate 
        
