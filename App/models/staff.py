from App.database import db

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    staffname = db.Column(db.String(120), nullable=False)
    
    assignments = db.relationship('ShiftAssignment', back_populates='staff', cascade='all, delete-orphan')

    def __init__(self, staffname):
        self.staffname = staffname
        
    def get_json(self):
        return {
            'id': self.id,
            'staffname': self.staffname,
        }

    def __repr__(self):
        return f'<Staff {self.id}: {self.staffname}>'