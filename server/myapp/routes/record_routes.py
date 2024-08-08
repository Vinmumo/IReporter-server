from datetime import datetime
from xml.dom.minidom import Notation
from myapp.extensions import db

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.now)
    images = db.relationship('Image', backref='record_ref', lazy=True,cascade='all, delete-orphan')
    videos = db.relationship('Video', backref='record_ref', lazy=True)


    def __init__(self, title, description, status='Pending', location=None, user_id=None):
        if not self.validate_title(title):
            raise ValueError("Title is required and must be less than 200 characters.")
        if not self.validate_description(description):
            raise ValueError("Description is required.")
        if not self.validate_status(status):
            raise ValueError("Invalid status.")
        # if Notation is not None and not self.validate_coordinates(Notation):
        #     raise ValueError("Invalid geographic coordinates.")

        self.title = title
        self.description = description
        self.status = status
        self.location = location
        self.user_id = user_id

    @staticmethod
    def validate_title(title):
        return len(title) > 0 and len(title) <= 200

    @staticmethod
    def validate_description(description):
        return len(description) > 0

    @staticmethod
    def validate_status(status):
        return status in ['Pending', 'InProgress', 'Completed']

    # @staticmethod
    # def validate_coordinates(coordinates):
    #     return coordinates is None or (isinstance(coordinates.location, (int, float)) and isinstance(coordinates.location, (int, float)))
