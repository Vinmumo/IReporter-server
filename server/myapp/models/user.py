
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from myapp.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Change to Boolean
    worker_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    records = db.relationship('Record', backref='user', lazy=True,cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs) #Initialize parent class
        self.public_id = str(uuid.uuid4()) #Generate unique public id


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)