from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.record import Record, db
from ..models.user import User
from ..models.image import Image
from ..models.video import Video
from myapp.services.cloudinary_services import upload_file

api = Namespace('records', description='Record operations')

record_model = api.model('Record', {
    'title': fields.String(required=True, description='The record title'),
    'description': fields.String(required=True, description='The record description'),
    'location': fields.String(required=True, description='The record location'),
    'status': fields.String(description='The record status'),
    'record_type': fields.String(required=True, description='The record type (red-flag or intervention)'),
    'created_at': fields.DateTime(readonly=True, description='The record creation timestamp')
})

@api.route('')
class RecordList(Resource):
    @api.doc('create_record')
    @api.expect(record_model)
    @jwt_required()
    def post(self):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        if not user:
            return {"error": "User not found"}, 404

        data = request.get_json()
        new_record = Record(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            record_type=data['record_type'],
            user_public_id=user.public_id
        )
        db.session.add(new_record)
        db.session.commit()

        # To add file uploads later

        return {"message": "Record added successfully", "record": marshal(new_record, record_model)}, 201

@api.route('/<string:public_id>')
@api.param('public_id', 'The record public identifier')
class RecordItem(Resource):
    @api.doc('get_record')
    @api.marshal_with(record_model)
    @jwt_required()
    def get(self, public_id):
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        return marshal(record, record_model)

    @api.doc('update_record')
    @api.expect(record_model)
    @api.marshal_with(record_model)
    @jwt_required()
    def put(self, public_id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        if record.user_public_id != user.public_id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        record.title = data.get('title', record.title)
        record.description = data.get('description', record.description)
        record.location = data.get('location', record.location)
        record.status = data.get('status', record.status)
        record.record_type = data.get('record_type', record.record_type)
        db.session.commit()
        return marshal(record, record_model)

    @api.doc('delete_record')
    @jwt_required()
    def delete(self, public_id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        record = Record.query.filter_by(public_id=public_id).first_or_404()
        if record.user_public_id != user.public_id:
            return {"error": "Unauthorized"}, 403

        db.session.delete(record)
        db.session.commit()
        return {"message": "Record deleted"}, 200