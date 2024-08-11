from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.record import Record, db
from ..models.user import User

api = Namespace('records', description='Record operations')

record_model = api.model('Record', {
    'public_id': fields.String(readonly=True, description='The record identifier'),
    'title': fields.String(required=True, description='The title of the record'),
    'description': fields.String(required=True, description='The description of the record'),
    'location': fields.String(required=True, description='The location related to the record'),
    'status': fields.String(description='The current status of the record'),
    'record_type': fields.String(required=True, description='The type of record (red-flag or intervention)'),
    'created_at': fields.DateTime(description='Record creation date'),
    'images': fields.List(fields.String, description='List of image URLs'),
    'videos': fields.List(fields.String, description='List of video URLs')
})

@api.route('/')
class RecordList(Resource):
    @api.doc('list_records')
    @api.marshal_with(record_model)
    @jwt_required()
    def get(self):
        """Fetch all records for the authenticated user"""
        current_user = self._get_current_user()
        records = Record.query.filter_by(user_public_id=current_user.public_id).all()
        return records

    @api.doc('create_record')
    @api.expect(record_model, validate=True)
    @api.marshal_with(record_model)
    @jwt_required()
    def post(self):
        """Create a new record"""
        current_user = self._get_current_user()
        data = request.json
        new_record = Record(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            record_type=data['record_type'],
            user_public_id=current_user.public_id
        )
        db.session.add(new_record)
        db.session.commit()
        return new_record, 201

    def _get_current_user(self):
        current_user_public_id = get_jwt_identity()
        return User.query.filter_by(public_id=current_user_public_id).first_or_404()


@api.route('/<string:public_id>')
@api.param('public_id', 'The record identifier')
class RecordItem(Resource):
    @api.doc('get_record')
    @api.marshal_with(record_model)
    @jwt_required()
    def get(self, public_id):
        """Fetch a single record by its public_id"""
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        return record

    @api.doc('update_record')
    @api.expect(record_model, validate=True)
    @api.marshal_with(record_model)
    @jwt_required()
    def put(self, public_id):
        """Update an existing record"""
        current_user = RecordList._get_current_user(self)
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        if record.user_public_id != current_user.public_id:
            api.abort(403, 'Unauthorized')
        data = request.json
        record.title = data.get('title', record.title)
        record.description = data.get('description', record.description)
        record.location = data.get('location', record.location)
        record.status = data.get('status', record.status)
        record.record_type = data.get('record_type', record.record_type)
        db.session.commit()
        return record

    @api.doc('delete_record')
    @api.response(204, 'Record deleted successfully')
    @api.response(403, 'Unauthorized')
    @jwt_required()
    def delete(self, public_id):
        """Delete a record by its public_id"""
        current_user = RecordList._get_current_user(self)
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        if record.user_public_id != current_user.public_id:
            api.abort(403, 'Unauthorized')
        db.session.delete(record)
        db.session.commit()
        return '', 204

@api.errorhandler(Exception)
def handle_exception(error):
    return {'message': str(error)}, getattr(error, 'code', 500)