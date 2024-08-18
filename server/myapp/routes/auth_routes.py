from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..models.user import User, db
from sqlalchemy.exc import SQLAlchemyError

api = Namespace('auth', description='Authentication operations')

# Constants for admin user validation
ADMIN_EMAIL_DOMAIN = 'ireporter.com'
VALID_WORKER_IDS = ['IRA1', 'IRA2', 'IRA3', 'IRA4', 'IRA5']
# VALID_WORKER_EMAILS = ['worker1@organization.com', 'worker2@organization.com', 'worker3@organization.com']

# Models for API documentation and data validation
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='The user ID'),
    'email': fields.String(description='The user email address'),
    'is_admin': fields.Boolean(readonly=True, description='Admin status'),
    'worker_id': fields.String(description='Worker ID for admin users'),
    'created_at': fields.DateTime(readonly=True, description='The user creation timestamp'),
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='The user email address'),
    'password': fields.String(required=True, description='The user password')
})

user_register_model = api.model('UserRegister', {
    'email': fields.String(required=True, description='The user email address'),
    'password': fields.String(required=True, description='The user password'),
    'worker_id': fields.String(description='Worker ID for admin users')
})


@api.route('/register')
class UserRegister(Resource):
    @api.expect(user_register_model)
    @api.marshal_with(user_model, code=201)
    @api.doc(responses={201: 'User registered successfully', 400: 'Validation error'})
    def post(self):
        try:
            data = request.get_json()
            email = data['email']
            worker_id = data.get('worker_id')

            # Determine if the user should be an admin
            is_admin = False
            if email.endswith(ADMIN_EMAIL_DOMAIN):
                is_admin = True
                if worker_id not in VALID_WORKER_IDS:
                    return {'message': 'Invalid worker ID'}, 400
            else:
                worker_id = None

            # Check if the user already exists
            if User.query.filter_by(email=email).first():
                return {'message': 'User already exists'}, 400

            # Create new user
            new_user = User(
                email=email,
                is_admin=is_admin,
                worker_id=worker_id
            )
            new_user.set_password(data['password'])
            db.session.add(new_user)
            db.session.commit()

            return new_user, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'Database error occurred'}, 500
        except Exception as e:
            return {'message': 'Internal Server Error'}, 500


@api.route('/login')
class UserLogin(Resource):
    @api.expect(login_model)
    @api.doc(responses={200: 'Login successful', 401: 'Invalid credentials'})
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.public_id)
            refresh_token = create_refresh_token(identity=user.public_id)
            user_data = user.to_dict()
            return {
                'message': 'Logged in successfully',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_data
            }, 200
        return {'message': 'Invalid email or password'}, 401


@api.route('/refresh')
class UserRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_public_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_public_id)
        return {'access_token': new_access_token}, 200


@api.route('/user')
class UserProfile(Resource):
    @jwt_required()
    @api.marshal_with(user_model)
    def get(self):
        try:
            current_user_public_id = get_jwt_identity()
            user = User.query.filter_by(public_id=current_user_public_id).first()
            if not user:
                return {'error': 'User not found'}, 404
            return user.to_dict(), 200
        except Exception as e:
            return {'error': 'Internal Server Error'}, 500


@api.route('/users/<int:id>')
@api.param('id', 'The user identifier')
class UserUpdate(Resource):
    @jwt_required()
    @api.expect(user_model)
    @api.marshal_with(user_model)
    def put(self, id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        if not user or user.id != id:
            return {'error': 'Unauthorized'}, 403
        data = request.json
        user.email = data.get('email', user.email)
        if 'password' in data:
            user.set_password(data['password'])
        db.session.commit()
        return user

    @jwt_required()
    def delete(self, id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        if not user or (not user.is_admin and user.id != id):
            return {'error': 'Unauthorized'}, 403
        user_to_delete = User.query.get(id)
        if not user_to_delete:
            return {'error': 'User not found'}, 404
        db.session.delete(user_to_delete)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200


@api.route('/logout')
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        return {'message': 'Successfully logged out'}, 200
