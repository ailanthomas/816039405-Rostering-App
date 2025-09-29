from App.database import db

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffname =  db.Column(db.String(20), nullable=False, unique=False)

    

    def __init__(self, staffname):
        self.staffname = staffname

    def get_json(self):
        return{
            'id': self.id,
            'staffname': self.staffname
        }