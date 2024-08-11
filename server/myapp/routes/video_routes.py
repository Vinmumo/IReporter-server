from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.record import Record, db
from ..models.video import Video
from ..models.user import User
from myapp.services.cloudinary_services import upload_file

api = Namespace('videos', description='Video operations')

video_model = api.model('Video', {
    'id': fields.Integer(readonly=True, description='The video identifier'),
    'url': fields.String(required=True, description='The video URL'),
    'record_id': fields.Integer(required=True, description='The associated record identifier')
})

@api.route('/')
class VideoList(Resource):
    @api.doc('create_video')
    @api.expect(video_model)
    @jwt_required()
    def post(self):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        record_id = request.form['record_id']
        record = Record.query.get_or_404(record_id)
        if record.user_public_id != user.public_id:
            return {'error': 'Unauthorized'}, 403
        video_file = request.files['video']
        upload_result = upload_file(video_file, resource_type='video')
        new_video = Video(url=upload_result['secure_url'], record_id=record_id, user_public_id=user.public_id)
        db.session.add(new_video)
        db.session.commit()
        return {'message': 'Video uploaded', 'video': marshal(new_video, video_model)}, 201

@api.route('/<int:id>')
@api.param('id', 'The video identifier')
class VideoItem(Resource):
    @api.doc('get_video')
    @api.marshal_with(video_model)
    @jwt_required()
    def get(self, id):
        video = Video.query.get_or_404(id)
        return marshal(video, video_model)

    @api.doc('update_video')
    @api.expect(video_model)
    @api.marshal_with(video_model)
    @jwt_required()
    def put(self, id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        video = Video.query.get_or_404(id)
        if video.user_public_id != user.public_id:
            return {'error': 'Unauthorized'}, 403
        video_file = request.files['video']
        upload_result = upload_file(video_file, resource_type='video')
        video.url = upload_result['secure_url']
        video.record_id = request.form['record_id']
        db.session.commit()
        return marshal(video, video_model)

    @api.doc('delete_video')
    @jwt_required()
    def delete(self, id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        video = Video.query.get_or_404(id)
        if video.user_public_id != user.public_id:
            return {'error': 'Unauthorized'}, 403
        db.session.delete(video)
        db.session.commit()
        return {'message': 'Video deleted'}, 200