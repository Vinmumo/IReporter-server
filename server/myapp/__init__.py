from flask import Flask

from myapp.models.image import Image
from myapp.models.record import Record
from myapp.models.user import User
from myapp.models.video import Video
from myapp.extensions import db,migrate
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()
    
    return app
