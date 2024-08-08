from myapp.extensions import db
from datetime import datetime

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.now)
    images = db.relationship('Image', backref='record', lazy=True,cascade='all, delete-orphan')
    videos = db.relationship('Video', backref='record', lazy=True,cascade='all, delete-orphan')
