import uuid
from datetime import datetime
from myapp.extensions import db
from myapp.models.user import User
from myapp.models.record import Record
from myapp.models.image import Image
from myapp.models.video import Video
from werkzeug.security import generate_password_hash

def seed():
    # Drop all tables and create them
    db.drop_all()
    db.create_all()

    # Create sample users
    user1 = User(
        username='reporter1',
        public_id=str(uuid.uuid4()),
        email='reporter1@example.com',
        password_hash=generate_password_hash('password123')
    )
    user2 = User(
        username='reporter2',
        public_id=str(uuid.uuid4()),
        email='reporter2@example.com',
        password_hash=generate_password_hash('password123')
    )
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()  # Commit users to get their IDs

    # Create sample records related to corruption
    record1 = Record(
        title='Bribery Incident',
        description='Witnessed a bribery incident at the city hall.',
        location='City Hall',
        user_id=user1.id,
        status='open',
        created_at=datetime.now()
    )
    record2 = Record(
        title='Embezzlement Case',
        description='Suspected embezzlement of public funds in the local council.',
        location='Local Council Office',
        user_id=user2.id,
        status='open',
        created_at=datetime.now()
    )
    record3 = Record(
        title='Fraudulent Activity',
        description='Observed fraudulent activity during the procurement process.',
        location='Procurement Office',
        user_id=user1.id,
        status='resolved',
        created_at=datetime.now()
    )
    db.session.add(record1)
    db.session.add(record2)
    db.session.add(record3)
    db.session.commit()  # Commit records to get their IDs

    # Create sample images related to the records
    image1 = Image(
        url='http://example.com/bribery.jpg',
        record_id=record1.id
    )
    image2 = Image(
        url='http://example.com/embezzlement.jpg',
        record_id=record2.id
    )
    image3 = Image(
        url='http://example.com/fraud.jpg',
        record_id=record3.id
    )
    db.session.add(image1)
    db.session.add(image2)
    db.session.add(image3)

    # Create sample videos related to the records
    video1 = Video(
        url='http://example.com/bribery_video.mp4',
        record_id=record1.id
    )
    video2 = Video(
        url='http://example.com/embezzlement_video.mp4',
        record_id=record2.id
    )
    video3 = Video(
        url='http://example.com/fraud_video.mp4',
        record_id=record3.id
    )
    db.session.add(video1)
    db.session.add(video2)
    db.session.add(video3)

    # Commit the changes
    db.session.commit()

if __name__ == '__main__':
    from myapp import create_app
    app = create_app()
    with app.app_context():
        seed()
