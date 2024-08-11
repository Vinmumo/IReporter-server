from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..models.user import User, db

api = Namespace('auth', description='Authentication operations')

# Constants for admin user validation
ADMIN_EMAIL_DOMAIN = 'organization.com'
VALID_WORKER_IDS = ['worker_id_1', 'worker_id_2', 'worker_id_3']
VALID_WORKER_EMAILS = ['worker1@organization.com', 'worker2@organization.com', 'worker3@organization.com']

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
        data = request.get_json()
        email = data['email']
        is_admin = email.endswith(ADMIN_EMAIL_DOMAIN)
        worker_id = data.get('worker_id')

        if is_admin:
            if worker_id not in VALID_WORKER_IDS or email not in VALID_WORKER_EMAILS:
                return {'message': 'Invalid worker ID or email'}, 400
        else:
            worker_id = None

        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 400

        new_user = User(
            email=email,
            is_admin=is_admin,
            worker_id=worker_id
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()

# Return the new user object to be marshaled
        return new_user, 201
    
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
            user_data = user.to_dict()  # Now includes 'id' as well
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
        new_access_token = create_access_token(identity=current_user_public_id)  # Use email as identity
        return {'access_token': new_access_token}, 200

@api.route('/user')
class UserProfile(Resource):
    @jwt_required()
    @api.marshal_with(user_model)
    def get(self):
        try:
            current_user_public_id = get_jwt_identity()
            user = User.query.filter_by(email=current_user_public_id).first()
            if not user:
                return {'error': 'User not found'}, 404
            return user.to_dict(), 200
        except Exception as e:
            print(f"Exception occurred: {e}")
            return {'error': 'Internal Server Error'}, 500

@api.route('/users/<int:id>')
@api.param('id', 'The user identifier')
class UserUpdate(Resource):
    @jwt_required()
    @api.expect(user_model)
    @api.marshal_with(user_model)
    def put(self, id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(email=current_user_public_id).first()
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
        user = User.query.filter_by(email=current_user_public_id).first()
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