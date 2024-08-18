import uuid
from datetime import datetime
from myapp.extensions import db

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), default='Under Investigation')
    record_type = db.Column(db.String(20), nullable=False) # 'red-flag' or 'intervention'
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_public_id = db.Column(db.String(40), db.ForeignKey('users.public_id'), nullable=False)
    # contact_token = db.Column(db.String(100), unique=True, nullable=False) - can be incorporated later on
    images = db.relationship('Image', backref='record', lazy=True, cascade="all, delete-orphan")
    videos = db.relationship('Video', backref='record', lazy=True, cascade="all, delete-orphan")


    def __init__(self, **kwargs):
        super(Record, self).__init__(**kwargs)
        self.public_id = str(uuid.uuid4())

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'description': self.description,
            'location': self.location,
            'status': self.status,
            'record_type': self.record_type,
            'created_at': self.created_at.isoformat(),
            'images': [image.url for image in self.images],
            'videos': [video.url for video in self.videos],
            # 'contact_token': self.contact_token
        }