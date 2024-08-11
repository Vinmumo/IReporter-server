from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.image import Image, db
from ..models.user import User
from myapp.services.cloudinary_services import upload_file

api = Namespace('images', description='Image operations')

image_model = api.model('Image', {
    'id': fields.Integer(readonly=True, description='The image identifier'),
    'url': fields.String(required=True, description='The image URL'),
    'record_id': fields.Integer(required=True, description='The associated record identifier')
})

api.models[image_model.name] = image_model

@api.route('/')
class ImageList(Resource):
    @api.doc('get_images')
    @api.marshal_list_with(image_model)
    @jwt_required()
    def get(self):
        current_user = self._get_current_user()
        images = Image.query.filter_by(user_public_id=current_user.public_id).all()
        return images, 200

    @api.doc('upload_image')
    @api.expect(api.parser()
                .add_argument('file', type='file', location='files', required=True)
                .add_argument('record_id', type=int, required=True, help='The associated record identifier'))
    @api.marshal_with(image_model, code=201)
    @jwt_required()
    def post(self):
        current_user = self._get_current_user()
        file = request.files['file']
        upload_result = upload_file(file)
        new_image = Image(
            url=upload_result['url'],
            record_id=request.form['record_id'],
            user_public_id=current_user.public_id
        )
        db.session.add(new_image)
        db.session.commit()
        return new_image, 201

    def _get_current_user(self):
        current_user_public_id = get_jwt_identity()
        return User.query.filter_by(public_id=current_user_public_id).first_or_404()

@api.route('/<int:id>')
@api.param('id', 'The image identifier')
class ImageItem(Resource):
    @api.doc('delete_image')
    @api.response(200, 'Image deleted successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Image not found')
    @jwt_required()
    def delete(self, id):
        current_user = ImageList._get_current_user(self)
        image = Image.query.get_or_404(id)
        if image.user_public_id != current_user.public_id:
            api.abort(403, 'Unauthorized')
        db.session.delete(image)
        db.session.commit()
        return {'message': 'Image deleted successfully'}, 200

@api.errorhandler(Exception)
def handle_exception(error):
    return {'message': str(error)}, getattr(error, 'code', 500)