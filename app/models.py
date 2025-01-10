from . import db

class Person(db.Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    image_path = db.Column(db.String(255), nullable=True)  # Optional field to save example images
    
    def __repr__(self):
        return f"<Person {self.name}>"

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    
    def __repr__(self):
        return f"<Attendance {self.name} on {self.date} at {self.time}>"
