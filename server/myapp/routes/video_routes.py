from flask import Blueprint, request, jsonify
from ..models.record import Record, db
from ..models.image import Image
from ..models.video import Video
from ..services.cloudinary_services import upload_file

video_bp = Blueprint('video_bp', __name__)

@video_bp.route('/videos', methods=['POST'])
def create_video():
    record_id = request.form['record_id']
    video_file = request.files['video']
    upload_result = upload_file(video_file, resource_type='video')
    video_url = upload_result['secure_url']
    new_video = Video(url=video_url, record_id=record_id)
    db.session.add(new_video)
    db.session.commit()
    return jsonify({"message": "Video uploaded", "video": new_video.id}), 201

@video_bp.route('/videos/<int:id>', methods=['GET'])
def get_video(id):
    video = Video.query.get_or_404(id)
    return jsonify({
        "id": video.id,
        "url": video.url,
        "record_id": video.record_id
    }), 200



@video_bp.route('/videos/<int:id>', methods=['DELETE'])
def delete_video(id):
    video = Video.query.get_or_404(id)
    upload_file(video.url, resource_type='video')
    db.session.delete(video)
    db.session.commit()
    return jsonify({"message": "Video deleted"}), 200