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

@api.route('')
class VideoList(Resource):
    @api.doc('create_video')
    @api.expect(api.parser()
                .add_argument('video', type='file', location='files', required=True)
                .add_argument('record_id', type=int, required=True, help='The associated record identifier'))
    @api.marshal_with(video_model, code=201)
    @jwt_required()
    def post(self):
        current_user = self._get_current_user()
        record_id = request.form['record_id']
        record = Record.query.get_or_404(record_id)
        if record.user_public_id != current_user.public_id:
            api.abort(403, 'Unauthorized')
        video_file = request.files['video']
        upload_result = upload_file(video_file, resource_type='video')
        new_video = Video(url=upload_result['secure_url'], record_id=record_id, user_public_id=current_user.public_id)
        db.session.add(new_video)
        db.session.commit()
        return new_video, 201

    def _get_current_user(self):
        current_user_public_id = get_jwt_identity()
        return User.query.filter_by(public_id=current_user_public_id).first_or_404()

@api.route('/<int:id>')
@api.param('id', 'The video identifier')
class VideoItem(Resource):
    @api.doc('get_video')
    @api.marshal_with(video_model)
    @jwt_required()
    def get(self, id):
        video = Video.query.get_or_404(id)
        return video

    @api.doc('delete_video')
    @api.response(200, 'Video deleted successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Video not found')
    @jwt_required()
    def delete(self, id):
        current_user = VideoList._get_current_user(self)
        video = Video.query.get_or_404(id)
        if video.user_public_id != current_user.public_id:
            api.abort(403, 'Unauthorized')
        db.session.delete(video)
        db.session.commit()
        return {'message': 'Video deleted'}, 200

@api.errorhandler(Exception)
def handle_exception(error):
    return {'message': str(error)}, getattr(error, 'code', 500)