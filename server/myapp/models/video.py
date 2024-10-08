from myapp.extensions import db


class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'record_id': self.record_id
        }