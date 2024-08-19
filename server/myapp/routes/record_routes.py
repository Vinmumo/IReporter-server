from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from ..models.record import Record, db
from ..models.image import Image
from ..models.video import Video
from ..models.user import User
from ..services.email_service import send_status_change_email
from ..services.cloudinary_services import upload_file

api = Namespace('records', description='Record operations')

record_model = api.model('Record', {
    'public_id': fields.String(readonly=True, description='The record identifier'),
    'description': fields.String(required=True, description='The description of the record'),
    'location': fields.String(required=True, description='The location related to the record'),
    'status': fields.String(description='The current status of the record'),
    'record_type': fields.String(required=True, description='The type of record (red-flag or intervention)'),
    'created_at': fields.DateTime(description='Record creation date'),
    'images': fields.List(fields.String, description='List of image URLs'),
    'videos': fields.List(fields.String, description='List of video URLs')
})

class RecordList(Resource):
    @jwt_required()
    def options(self):
        return '', HTTPStatus.OK
    
    @api.doc('list_records')
    @api.marshal_with(record_model)
    @jwt_required()
    def get(self):
        """Fetch all records for the authenticated user"""
        current_user = self._get_current_user()
        records = Record.query.filter_by(user_public_id=current_user.public_id).all()

        for record in records:
            record.images = [image.url for image in Image.query.filter_by(record_id=record.id).all()]
            record.videos = [video.url for video in Video.query.filter_by(record_id=record.id).all()]

        return records, HTTPStatus.OK

    @api.doc('create_record')
    @api.expect(api.parser()
                .add_argument('description', type=str, required=True, help='The record description')
                .add_argument('location', type=str, required=True, help='The record location')
                .add_argument('record_type', type=str, required=True, help='The type of record')
                .add_argument('files', type='file', location='files', required=False, action='append', help='Images or videos associated with the record'))
    @api.marshal_with(record_model)
    @jwt_required()
    def post(self):
        current_user = self._get_current_user()
        description = request.form['description']
        location = request.form['location']
        record_type = request.form['record_type']

        new_record = Record(
            description=description,
            location=location,
            record_type=record_type,
            user_public_id=current_user.public_id
        )
        db.session.add(new_record)
        db.session.commit()

        files = request.files.getlist('files')
        for file in files:
            upload_result = upload_file(file)
            if 'image' in upload_result['resource_type']:
                new_image = Image(
                    url=upload_result['url'],
                    record_id=new_record.id,
                    user_public_id=current_user.public_id
                )
                db.session.add(new_image)
            elif 'video' in upload_result['resource_type']:
                new_video = Video(
                    url=upload_result['url'],
                    record_id=new_record.id,
                    user_public_id=current_user.public_id
                )
                db.session.add(new_video)
        
        db.session.commit()
        return new_record, HTTPStatus.CREATED

    def _get_current_user(self):
        current_user_public_id = get_jwt_identity()
        return User.query.filter_by(public_id=current_user_public_id).first_or_404()

class RecordItem(Resource):
    @api.doc('get_record')
    @api.marshal_with(record_model)
    @jwt_required()
    def get(self, public_id):
        """Fetch a single record by its public_id"""
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        return record, HTTPStatus.OK

    @api.doc('update_record')
    @api.expect(record_model, validate=True)
    @api.marshal_with(record_model)
    @jwt_required()
    def put(self, public_id):
        """Update an existing record"""
        current_user = RecordList._get_current_user(self)
        record = Record.query.filter_by(public_id=public_id).first_or_404()

        if record.user_public_id != current_user.public_id:
            api.abort(HTTPStatus.FORBIDDEN, 'Unauthorized')

        if record.status != 'Under Investigation':
            api.abort(HTTPStatus.BAD_REQUEST, 'Record status cannot be updated by the user')

        data = request.json
        record.description = data.get('description', record.description)
        record.location = data.get('location', record.location)
        db.session.commit()
        return record, HTTPStatus.OK

    @api.doc('change_record_status')
    @api.expect(record_model, validate=True)
    @api.marshal_with(record_model)
    @jwt_required()
    def patch(self, public_id):
        """Admin can update the status of a record"""
        current_user = RecordList._get_current_user(self)
        if not current_user.is_admin:
            api.abort(HTTPStatus.FORBIDDEN, 'Unauthorized')

        record = Record.query.filter_by(public_id=public_id).first_or_404()
        data = request.json
        new_status = data.get('status', record.status)

        record.status = new_status
        db.session.commit()

        user = User.query.filter_by(public_id=record.user_public_id).first_or_404()

        send_status_change_email(user.email, record)

        return record, HTTPStatus.OK

    @api.doc('delete_record')
    @api.response(HTTPStatus.NO_CONTENT, 'Record deleted successfully')
    @api.response(HTTPStatus.FORBIDDEN, 'Unauthorized')
    @jwt_required()
    def delete(self, public_id):
        """Delete a record by its public_id"""
        current_user = RecordList._get_current_user(self)
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        if record.user_public_id != current_user.public_id:
            api.abort(HTTPStatus.FORBIDDEN, 'Unauthorized')
        db.session.delete(record)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT

class RedFlagList(Resource):
    @api.doc('list_red_flags')
    @api.marshal_with(record_model)
    @jwt_required()
    def get(self):
        """Fetch all red-flag records for the authenticated user or admin"""
        current_user_public_id = get_jwt_identity()
        current_user = User.query.filter_by(public_id=current_user_public_id).first_or_404()

        if current_user.is_admin:
            red_flags = Record.query.filter_by(record_type='red-flag').all()
        else:
            red_flags = Record.query.filter_by(user_public_id=current_user_public_id, record_type='red-flag').all()

        if not red_flags:
            return jsonify({'message': 'No red flags found'}), HTTPStatus.NOT_FOUND
        
        for record in red_flags:
            record.images = [image.url for image in Image.query.filter_by(record_id=record.id).all()]
            record.videos = [video.url for video in Video.query.filter_by(record_id=record.id).all()]

        return red_flags, HTTPStatus.OK

class InterventionList(Resource):
    @api.doc('list_interventions')
    @api.marshal_with(record_model)
    @jwt_required()
    def get(self):
        """Fetch all intervention records for the authenticated user or admin"""
        current_user_public_id = get_jwt_identity()
        current_user = User.query.filter_by(public_id=current_user_public_id).first_or_404()

        if current_user.is_admin:
            interventions = Record.query.filter_by(record_type='intervention').all()
        else:
            interventions = Record.query.filter_by(user_public_id=current_user_public_id, record_type='intervention').all()

        if not interventions:
            return jsonify({'message': 'No interventions found'}), HTTPStatus.NOT_FOUND
        
        for record in interventions:
            record.images = [image.url for image in Image.query.filter_by(record_id=record.id).all()]
            record.videos = [video.url for video in Video.query.filter_by(record_id=record.id).all()]

        return interventions, HTTPStatus.OK

# Register resources 
api.add_resource(RecordList, '/', strict_slashes=False)
api.add_resource(RecordItem, '/<string:public_id>', strict_slashes=False)
api.add_resource(RedFlagList, '/red-flags', strict_slashes=False)
api.add_resource(InterventionList, '/interventions', strict_slashes=False)
