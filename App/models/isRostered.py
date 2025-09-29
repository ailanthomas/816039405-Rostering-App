from App.database import db

class IsRostered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffId = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    rosterId = db.Column(db.Integer, db.ForeignKey('roster.rosterId'), nullable=False)
    shift = db.Column(db.String(20), nullable=False)

    def __init__(self, staffId, rosterId, shift):
        self.staffId = staffId
        self.rosterId = rosterId
        self.shift = shift