from App.database import db

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aName =  db.Column(db.String(20), nullable=False, unique=False)
    

    def __init__(self, aName):
        self.aName = aName
        

    def get_json(self):
        return{
            'id': self.id,
            'aName': self.aName
        }