from myapp.extensions import db
from sqlite3 import IntegrityError

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'), nullable=False)

    def __init__(self, url, record_id=None):
        if not self.validate_url(url):
            raise ValueError("Invalid image URL.")
        self.url = url
        self.record_id = record_id  # Updated here to use record_id instead of record

    @staticmethod
    def validate_url(url):
        # Validation to check if the URL has a valid image extension
        valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
        if not any(url.lower().endswith(ext) for ext in valid_extensions):
            return False
        return True

    @staticmethod
    def create_image(url, record_id=None):
        if not Image.validate_url(url):
            raise ValueError("Invalid image URL format.")
        
        new_image = Image(url=url, record_id=record_id)  # Updated here to use record_id
        try:
            db.session.add(new_image)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Image could not be added.")
