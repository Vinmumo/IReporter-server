from flask import Blueprint, request, jsonify
from ..models.record import Record, db
from ..models.image import Image
from ..models.video import Video
from ..services.cloudinary_services import upload_file
# import cloudinary.uploader

record_bp = Blueprint('record_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@record_bp.route('/add_record', methods=['POST'])
def add_record():
    title = request.form['title']
    description = request.form['description']
    location = request.form['location']
    user_id = request.form['user_id']
    image_file = request.files.get('image')
    video_file = request.files.get('video')

    new_record = Record(title=title, description=description, location=location, user_id=user_id)
    db.session.add(new_record)
    db.session.commit()  # Save the record first to get the id

    if image_file and allowed_file(image_file.filename):
        upload_result = upload_file(image_file)
        image_url = upload_result['secure_url']
        new_image = Image(url=image_url, record_id=new_record.id)
        db.session.add(new_image)

    if video_file and allowed_file(video_file.filename):
        upload_result = upload_file(video_file, resource_type='video')
        video_url = upload_result['secure_url']
        new_video = Video(url=video_url, record_id=new_record.id)
        db.session.add(new_video)

    db.session.commit()

    return jsonify({"message": "Record added successfully"}), 201

@record_bp.route('/records', methods=['GET'])
def get_all_records():
    records = Record.query.all()
    records_list = []
    for record in records:
        record_data = {
            "id": record.id,
            "title": record.title,
            "description": record.description,
            "location": record.location,
            "user_id": record.user_id,
            "status": record.status,
            "created_at": record.created_at,
            "images": [{"id": img.id, "url": img.url} for img in record.images],
            "videos": [{"id": vid.id, "url": vid.url} for vid in record.videos]
        }
        records_list.append(record_data)
    
    return jsonify(records_list), 200


@record_bp.route('/records/<int:id>', methods=['GET'])
def get_record(id):
    record = Record.query.get_or_404(id)
    return jsonify({
        "id": record.id,
        "title": record.title,
        "description": record.description,
        "location": record.location,
        "user_id": record.user_id,
        "status": record.status,
        "created_at": record.created_at,
        "images": [{"id": img.id, "url": img.url} for img in record.images],
        "videos": [{"id": vid.id, "url": vid.url} for vid in record.videos]
    }), 200

@record_bp.route('/records/<int:id>', methods=['PUT'])
def update_record(id):
    record = Record.query.get_or_404(id)
    record.title = request.form['title']
    record.description = request.form['description']
    record.location = request.form['location']
    record.status = request.form['status']
    db.session.commit()
    return jsonify({"message": "Record updated"}), 200

# @record_bp.route('/records/<int:id>', methods=['DELETE'])
# def delete_record(id):
#     record = Record.query.get_or_404(id)
#     for img in record.images:
#         cloudinary.uploader.destroy(img.url)
#         db.session.delete(img)
#     for vid in record.videos:
#         cloudinary.uploader.destroy(vid.url, resource_type='video')
#         db.session.delete(vid)
#     db.session.delete(record)
#     db.session.commit()
#     return jsonify({"message": "Record deleted"}), 200
